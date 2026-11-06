#!/usr/bin/env python3
"""Run the inherited lightweight patch/i18n checks on exact locked inputs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import lune


def catalog_gaps(extracted, expected):
    # Later patches can replace a message added earlier. This is an audit of
    # extracted additions, not a generator for final conditional resources.
    latest = {(entry['source'], entry['name']): entry for entry in extracted}
    return [entry for entry in latest.values() if entry not in expected]


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
    # The extractor expects a directory named macos; an isolated adapter also
    # prevents it from picking up an unrelated sibling onboarding checkout.
    with tempfile.TemporaryDirectory(prefix='lune-string-audit-') as temp:
        (Path(temp) / 'macos').symlink_to(platform, target_is_directory=True)
        extracted = list(i18n_generate.extract_strings(core, Path(temp)))
    missing = catalog_gaps(extracted, expected)
    if missing:
        print(f'WARNING: {len(missing)} extracted core/macOS messages are missing or changed '
              'in source.gen.json. English fallback remains accepted; remediation: '
              'https://github.com/leebyron/lune-browser/issues/4')
        for entry in missing:
            print(f"  {entry['name']}: {entry['message']}")
    else:
        print('Extracted core/macOS source strings match the translation registry.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('platform', type=Path)
    parser.add_argument('--source-strings', action='store_true',
                        help='Also report source catalog coverage (advisory; English fallback is accepted)')
    args = parser.parse_args()
    try:
        check(args.platform, args.source_strings)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'error: {error}\n')
