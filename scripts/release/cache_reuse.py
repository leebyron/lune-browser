#!/usr/bin/env python3
"""Seed fresh, attested sources from an idle compatible Siso output cache.

Only matching source bytes inherit timestamps. Both Siso's file-state database
and its separate Ninja dependency database must follow the new workspace.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from model import ROOT, sha
from prepare import inventory
import ninja_deps

sys.path.insert(0, str(ROOT / 'scripts'))
import lune

PENDING = '.lune-cache-transfer-pending'
OUTPUTS = {'arm64': 'Default', 'x86_64': 'Intel'}


def relocated(name, roots, destination, relative_to=None):
    if not os.path.isabs(name):
        return name
    normalized = os.path.normpath(name)
    for root in roots:
        if normalized == root or normalized.startswith(root + '/'):
            result = str(destination) + normalized[len(root):]
            return os.path.relpath(result, relative_to) if relative_to else result
    return name


def relocate_state(value, roots, destination):
    if isinstance(value, str):
        return relocated(value, roots, destination)
    if isinstance(value, list):
        return [relocate_state(v, roots, destination) for v in value]
    if isinstance(value, dict):
        return {relocated(k, roots, destination): relocate_state(v, roots, destination)
                for k, v in value.items()}
    return value


def dependency_mapper(roots, source, out, files, state):
    # Older ad-hoc transfers left Clang resource paths several workspaces old.
    # Recover only this pinned toolchain subtree, with its cached content digest
    # checked against the freshly attested bytes. Never guess arbitrary roots.
    marker = '/third_party/llvm-build/'
    cached = {}
    for entry in state['entries']:
        name = os.path.normpath(entry['name'])
        if marker in name and entry.get('digest', {}).get('hash'):
            relative = 'third_party/llvm-build/' + name.split(marker, 1)[1]
            cached.setdefault(relative, set()).add(entry['digest']['hash'])

    def mapper(name):
        mapped = relocated(name, roots, source, out)
        if not os.path.isabs(mapped):
            return mapped
        normalized = os.path.normpath(mapped)
        if marker in normalized:
            suffix = normalized.split(marker, 1)[1]
            relative = 'third_party/llvm-build/' + suffix
            if (suffix.startswith('Release+Asserts/lib/clang/')
                    and cached.get(relative) == {files.get(relative)}):
                return os.path.relpath(source / relative, out)
        raise ValueError(f'Unproven dependency from another source workspace: {name}; use a cold build')
    return mapper


def fingerprint(out):
    return {name: sha(out / name) for name in
            ('.siso_deps', '.siso_fs_state', 'build.ninja', 'args.gn')}


def verify_cached_source_ids(state, roots, source, files):
    """Reject stale content hidden behind an unchanged cached file timestamp."""
    for entry in state['entries']:
        mapped = Path(relocated(entry['name'], roots, source))
        if not mapped.is_relative_to(source):
            continue
        relative = mapped.relative_to(source).as_posix()
        digest = entry.get('digest', {}).get('hash')
        if relative in files and digest and digest != files[relative]:
            cached_time = entry.get('id', {}).get('mod_time')
            if cached_time == mapped.stat().st_mtime_ns:
                raise ValueError('Cached source bytes differ despite an identical timestamp: '
                                 f'{relative}; use a cold build')


def seed(source, cache_source, prepared_report, report, arches, env, *, verified_inventory=None):
    started = time.monotonic()
    source, donor = source.resolve(), cache_source.resolve()
    if source == donor or source.is_relative_to(donor) or donor.is_relative_to(source):
        raise ValueError('Cache donor and fresh source must be separate workspaces')
    report = report.resolve()
    if report.exists():
        raise ValueError('Preserve existing cache-transfer evidence')
    if report.is_relative_to(donor) or report.is_relative_to(source):
        raise ValueError('Keep cache-transfer evidence outside both source trees')
    if (source / 'out').is_symlink():
        raise ValueError('Fresh output root must not be a symlink to another workspace')
    prepared = json.loads(prepared_report.read_text())
    if not prepared.get('strict_replay_passed') or prepared.get('inventory_version') != 1:
        raise ValueError('Completed strict source preparation is required')
    print('Verifying fresh source inventory', flush=True)
    files, links = verified_inventory if verified_inventory is not None else inventory(source)
    if files != prepared['files'] or links != prepared['symlinks']:
        raise ValueError('Fresh source differs from its preparation inventory')
    # A different compiler/PGO/SDK can legitimately require a cold build. Do not
    # make path relocation conceal such a change.
    recipe = json.loads((ROOT / 'config/release-recipe.json').read_text())
    for name, digest in recipe['source_tools'].items():
        if sha(source / name) != digest or sha(donor / name) != digest:
            raise ValueError(f'Cache toolchain input differs: {name}; use a cold build')
    for name, target in links.items():
        if not (donor / name).is_symlink() or os.readlink(donor / name) != target:
            raise ValueError(f'Cache source symlink changed: {name}; use a cold build')
    for arch in arches:
        target = source / 'out' / OUTPUTS[arch]
        if target.exists():
            raise ValueError(f'Never overwrite existing outputs: {target}')
    source.joinpath('out').mkdir(exist_ok=True)
    marker = source / 'out' / PENDING
    with marker.open('x') as stream:
        json.dump({'donor': str(donor), 'report': str(report)}, stream)
    result = dict(schema_version=1, donor=str(donor), source=str(source),
                  prepared_report_sha256=sha(prepared_report), architectures={})
    # Hold all donor locks through timestamp comparison and output copying.
    # The fingerprint also rejects concurrent non-Siso edits to these inputs.
    from contextlib import ExitStack
    with ExitStack() as stack:
        before = {}
        for arch in arches:
            prior = donor / 'out' / OUTPUTS[arch]
            lock = stack.enter_context((prior / '.siso_lock').open('rb'))
            fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
            before[arch] = fingerprint(prior)
        matched, changed = 0, []
        print('Comparing donor source bytes and restoring matching timestamps', flush=True)
        for name, digest in files.items():
            prior, fresh = donor / name, source / name
            if (prior.is_file() and not prior.is_symlink()
                    and prior.stat().st_size == fresh.stat().st_size and sha(prior) == digest):
                os.utime(fresh, ns=(fresh.stat().st_atime_ns, prior.stat().st_mtime_ns))
                matched += 1
            else:
                fresh.touch()
                changed.append(name)
        result.update(matching_source_timestamps=matched, changed_sources=changed)
        roots = sorted({os.path.normpath(str(cache_source.absolute())), str(donor)},
                       key=len, reverse=True)
        siso = source / 'third_party/siso/cipd/siso'
        for arch in arches:
            print(f'Snapshotting and relocating {arch} outputs and dependency metadata', flush=True)
            prior, dest = donor / 'out' / OUTPUTS[arch], source / 'out' / OUTPUTS[arch]
            dest.mkdir()
            # APFS clone-on-write preserves the donor and avoids a second physical
            # copy. Cross-filesystem copies use the standard metadata copy path.
            for item in prior.iterdir():
                if item.name in ('Lune.app', '.siso_lock') or item.name.startswith(('siso_', '.siso.')):
                    continue
                if sys.platform == 'darwin' and prior.stat().st_dev == dest.stat().st_dev:
                    subprocess.run(['/bin/cp', '-cRpP', str(item), str(dest)], check=True, env=env)
                elif item.is_dir() and not item.is_symlink():
                    shutil.copytree(item, dest / item.name, symlinks=True)
                else:
                    shutil.copy2(item, dest / item.name, follow_symlinks=False)
            state = json.loads(subprocess.check_output(
                [siso, 'fs', 'export', '-C', prior], cwd=donor, env=env))
            verify_cached_source_ids(state, roots, source, files)
            dependencies = ninja_deps.read(dest / '.siso_deps')
            mapper = dependency_mapper(roots, source, dest, files, state)
            stats = ninja_deps.write(dest / '.siso_deps', dependencies, mapper)
            state = relocate_state(state, roots, source)
            state.pop('build_targets', None)
            subprocess.run([siso, 'fs', 'import', '-C', dest], cwd=source, env=env,
                           input=json.dumps(state).encode(), check=True)
            result['architectures'][arch] = dict(dependencies=stats,
                donor_metadata_sha256=before[arch], file_state_entries=len(state['entries']),
                fresh_app_bundle_required=True)
        for arch in arches:
            if fingerprint(donor / 'out' / OUTPUTS[arch]) != before[arch]:
                raise ValueError('Donor changed during cache transfer; do not use this snapshot')
    result['duration_seconds'] = time.monotonic() - started
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + '\n')
    marker.unlink()
    print(f'Cache transfer completed: {report}', flush=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--cache-source', type=Path, required=True)
    p.add_argument('--prepared-report', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--arch', action='append', choices=OUTPUTS, required=True)
    a = p.parse_args()
    lune.check_build_space(a.source)
    result = seed(a.source, a.cache_source, a.prepared_report, a.report,
                  list(dict.fromkeys(a.arch)), lune.build_env())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
