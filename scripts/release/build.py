#!/usr/bin/env python3
"""Compile an attested prepared source tree using the frozen release recipe."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from model import ROOT, feed_url, git, load_record, sha
sys.path.insert(0, str(ROOT / 'scripts'))
import lune
from prepare import inventory


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version', required=True)
    p.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--prepared-report', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    load_record(a.version)
    lock = json.loads((ROOT / 'manifests/browser.lock.json').read_text())
    lune.validate_lock(lock)
    lune.validate(argparse.Namespace(git_objects=True))
    recipe = json.loads((ROOT / 'config/release-recipe.json').read_text())
    src = a.source.resolve()
    prepared = json.loads(a.prepared_report.read_text())
    for component in ('helium', 'macos'):
        if prepared[component] != lock['components'][component]['commit']:
            raise ValueError('Prepared source uses different component inputs')
    if not prepared.get('strict_replay_passed') or prepared.get('inventory_version') != 1:
        raise ValueError('Strict preparation and complete source inventory required')
    def verify_sources():
        files, links = inventory(src)
        if files != prepared['files'] or links != prepared['symlinks']:
            changed = sorted(name for name in files.keys() | prepared['files'].keys()
                             if files.get(name) != prepared['files'].get(name))
            raise ValueError(f'Prepared source changed: {changed[:20]}; check symlinks too')
    verify_sources()
    env = lune.build_env()
    def output(*cmd): return subprocess.check_output(cmd, text=True, env=env).strip()
    if output('sw_vers', '-productVersion') != recipe['host_macos_version'] or output('sw_vers', '-buildVersion') != recipe['host_macos_build']:
        raise ValueError('Host macOS differs from the frozen toolchain')
    if output('uname', '-m') != recipe['host_architecture']:
        raise ValueError('Unexpected build host architecture')
    if sorted(output('python', '-m', 'pip', 'freeze').splitlines()) != sorted(recipe['python_packages']):
        raise ValueError('Build Python packages differ from the frozen toolchain')
    xcode = output('xcodebuild', '-version')
    if f"Xcode {recipe['xcode_version']}" not in xcode or f"Build version {recipe['xcode_build']}" not in xcode:
        raise ValueError('Unexpected Xcode toolchain')
    if output('xcrun', '--sdk', 'macosx', '--show-sdk-version') != recipe['sdk_version']:
        raise ValueError('Unexpected SDK')
    for name,digest in recipe['source_tools'].items():
        if sha(src/name)!=digest:
            raise ValueError(f'Toolchain input changed: {name}')
    if output('python', '--version') != recipe['python_version']:
        raise ValueError('Unexpected build Python')
    if output('xcrun', 'metal', '--version').splitlines()[0] != recipe['metal_version']:
        raise ValueError('Unexpected Metal toolchain')
    if output('sccache', '--version') != recipe['sccache_version']:
        raise ValueError('Unexpected compiler cache version')
    out = src / 'out' / ('Default' if a.arch == 'arm64' else 'Intel')
    args = dict(recipe['gn_args'], target_cpu=json.dumps('arm64' if a.arch == 'arm64' else 'x64'),
                sparkle_feed_url=json.dumps(feed_url(a.arch)))
    out.mkdir(parents=True, exist_ok=True)
    (out / 'args.gn').write_text(''.join(f'{k}={v}\n' for k,v in sorted(args.items())))
    a.report = a.report.resolve()
    if a.report.exists(): raise ValueError('Build report exists; preserve previous evidence')
    a.report.parent.mkdir(parents=True, exist_ok=True)
    report = dict(arch=a.arch, release_version=a.version, platform_commit=prepared['macos'],
        core_commit=prepared['helium'], orchestrator_commit=git(ROOT, 'rev-parse', 'HEAD'),
        release_record_sha256=sha(ROOT / f'manifests/releases/{a.version}.json'),
        prepared_report_sha256=sha(a.prepared_report), args_sha256=sha(out / 'args.gn'),
        xcode=xcode, host_os=output('sw_vers'), python=sys.version, release_validated=False)
    started = time.time()
    with a.report.with_suffix('.log').open('w') as log:
        subprocess.run([src/'buildtools/mac/gn', 'gen', str(out)], cwd=src, env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
        result = subprocess.run(['/usr/bin/caffeinate', '-i', src/'third_party/siso/cipd/siso',
            'ninja', '--fast_local', '-C', str(out), f"-local_jobs={recipe['local_jobs']}",
            *recipe['targets']], cwd=src, env=env, stdout=log, stderr=subprocess.STDOUT)
    verify_sources()
    report.update(exit_code=result.returncode, duration_seconds=time.time()-started)
    a.report.write_text(json.dumps(report, indent=2)+'\n')
    return result.returncode


if __name__ == '__main__': sys.exit(main())
