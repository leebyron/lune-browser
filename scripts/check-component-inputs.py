#!/usr/bin/env python3
"""Run the inherited lightweight patch/i18n checks on exact locked inputs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import lune


def check(platform, source_strings=False):
    platform = platform.resolve()
    lock = lune.read_json(lune.LOCK)
    lune.validate_lock(lock)
    lune.check_checkout(platform, lock)
    core = platform / 'helium-chromium'

    def run(script, *args):
        subprocess.run([sys.executable, str(core / 'devutils' / script), *map(str, args)],
                       cwd=core, check=True, env=lune.build_env())

    run('lint.py')
    run('lint.py', '-t', platform)
    run('i18n_lint.py')
    print('Locked core/platform patch series and translation files passed.')
    if not source_strings:
        return
    # The upstream CLI fetches moving Windows/Linux/macOS branches. Use only its
    # extractor on our checked core and platform; do not call prep_platform_repos.
    sys.path[:0] = [str(core / 'devutils'), str(core)]
    import i18n_generate
    i18n_generate.PLATFORMS = ('macos',)
    expected = json.loads((core / 'i18n/source.gen.json').read_text())
    extracted = list(i18n_generate.extract_strings(core, platform.parent))
    missing = [entry['name'] for entry in extracted if entry not in expected]
    if missing:
        raise ValueError(f'Core/macOS strings missing or changed in source.gen.json: {missing}')
    print(f'{len(extracted)} core/macOS source strings match the translation registry.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('platform', type=Path)
    parser.add_argument('--source-strings', action='store_true',
                        help='Also check extracted core/macOS strings against source.gen.json')
    args = parser.parse_args()
    try:
        check(args.platform, args.source_strings)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'error: {error}\n')
