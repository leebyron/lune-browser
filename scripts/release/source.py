#!/usr/bin/env python3
"""Assemble a public source kit from committed inputs and pinned archives only."""
import argparse
import configparser
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.output.exists():
        raise ValueError('Source kit already exists')
    if subprocess.check_output(['git', 'diff', 'HEAD', '--', 'config', 'manifests/browser.lock.json',
                                'manifests/patches.json', 'scripts', 'branding'], cwd=ROOT):
        raise ValueError('Commit release inputs before exporting sources')
    lock = json.loads((ROOT / 'manifests/browser.lock.json').read_text())
    config = configparser.ConfigParser(interpolation=None)
    config.read(ROOT / 'manifests/downloads-arm64.ini')
    archives = []
    for name in config.sections():
        entry = config[name]
        path = args.archives / entry['download_filename']
        algorithm = 'sha256' if 'sha256' in entry else 'sha512'
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, algorithm).hexdigest()
        if digest != entry[algorithm]:
            raise ValueError(f'Archive hash mismatch: {path.name}')
        if path.stat().st_size >= 2 * 1024**3:
            raise ValueError(f'Archive exceeds GitHub asset limit: {path.name}')
        archives.append({'filename': path.name, algorithm: digest, 'upstream_url': entry['url'],
                         'size': path.stat().st_size})
    args.output.mkdir(parents=True)
    kit = args.output / 'source-kit'
    kit.mkdir()
    for name in ('helium', 'macos'):
        ref = lock['components'][name]['ref']
        actual = subprocess.check_output(['git', 'rev-parse', ref + '^{commit}'], cwd=ROOT, text=True).strip()
        if actual != lock['components'][name]['commit']:
            raise ValueError(f'Wrong input ref: {ref}')
        subprocess.run(['git', 'bundle', 'create', str(kit / f'{name}.bundle'), ref], cwd=ROOT, check=True)
    subprocess.run(['git', 'archive', '--format=tar', '--prefix=orchestrator/',
                    '-o', str(kit / 'orchestrator.tar'), 'HEAD', 'scripts', 'config', 'manifests',
                    'branding', 'AGENTS.md', 'agent-docs/project'], cwd=ROOT, check=True)
    (kit / 'archives.json').write_text(json.dumps(archives, indent=2) + '\n')
    (kit / 'README.txt').write_text('''Lune corresponding source kit

This kit contains exact Helium-derived core/macOS Git histories, retained licenses,
and committed orchestration, configuration, patch provenance, and build instructions.
The adjacent release assets listed in archives.json are all pinned source/dependency
archives used for this macOS build. Verify their hashes before unpacking.

Extract orchestrator.tar. Read orchestrator/agent-docs/project/building.md and
builds/2026-11-06-release-bootstrap.md for the pinned Xcode/SDK/Python environment,
release-specific GN flags, and signing/versioning steps. Apple signing credentials
and Sparkle private keys are intentionally not distributed; use your own for a fork.

Clone macos.bundle at the macOS input tag in manifests/browser.lock.json. Clone
helium.bundle at the core input tag into macos/helium-chromium. Preserve the gitlink.
Copy the adjacent archives into macos/build/download_cache. Source
macos/devutils/shared.sh with _root_dir set to the absolute macos path and
LUNE_DOWNLOADS_INI set to orchestrator/manifests/downloads-arm64.ini. Invoke
prepare_sources true, then write_gn_args TARGET release (TARGET is arm64 or x86_64).
Add the release GN flags recorded in the release evidence and run gn_gen, followed
by helium_build -j 10 chrome/installer/mac. Both targets can be built on Apple silicon.

Lune's browser changes are GPL-3.0 with imported licenses retained. Chromium,
Sparkle, bundled dependencies, artwork, and assets retain their respective licenses.
Consult each component's LICENSE, LICENSE.ungoogled_chromium, third-party notices,
and the packaged chrome://credits page. No blanket relicensing is applied here.
''')
    archive = args.output / 'lune-source-kit.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        tar.add(kit, arcname='lune-source-kit')
    (args.output / 'source-assets.json').write_text(json.dumps({
        'orchestrator_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_kit': archive.name, 'archives': archives}, indent=2) + '\n')
    print(archive)


if __name__ == '__main__':
    main()
