#!/usr/bin/env python3
"""Prepare clean locked sources and inventory their bytes for release builds."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from model import ROOT, sha
sys.path.insert(0, str(ROOT / 'scripts'))
import lune

EXCLUDED = {'out', '.git', '.pc', '__pycache__'}


def inventory(source):
    files, links = {}, {}
    for directory, dirs, names in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in sorted(names + [d for d in dirs if (Path(directory) / d).is_symlink()]):
            path = Path(directory) / name
            relative = path.relative_to(source).as_posix()
            if path.is_symlink():
                links[relative] = os.readlink(path)
            elif path.is_file() and not name.endswith('.pyc'):
                files[relative] = sha(path)
    return files, links


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--platform', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    platform = a.platform.resolve()
    source = platform / 'build/src'
    report = a.report.resolve()
    lock = lune.read_json(ROOT / 'manifests/browser.lock.json')
    lune.validate_lock(lock)
    lune.require_clean_orchestrator()
    lune.check_checkout(platform, lock)
    if source.exists() or report.exists():
        raise ValueError('Use a new source tree and report; never reset existing build work')
    env = lune.build_env()
    host = subprocess.check_output(['uname', '-m'], text=True).strip()
    if host not in ('arm64', 'x86_64'):
        raise ValueError('Unsupported build host')
    env['LUNE_DOWNLOADS_INI'] = str(ROOT / f'manifests/downloads-{"arm64" if host == "arm64" else "x64"}.ini')
    report.parent.mkdir(parents=True, exist_ok=True)
    shell = '''set -euo pipefail
_root_dir="$1"
source "$_root_dir/devutils/shared.sh"
prepare_sources true
configure_siso
'''
    with report.with_suffix('.log').open('x') as log:
        subprocess.run(['/bin/bash', '-c', shell, 'lune-release-prepare', str(platform)],
                       cwd=platform, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    files, links = inventory(source)
    result = dict(schema_version=1, inventory_version=1, helium=lock['components']['helium']['commit'],
                  macos=lock['components']['macos']['commit'], strict_replay_passed=True,
                  scope='complete prepared source inventory excluding outputs and bookkeeping',
                  files=files, symlinks=links, preparation_log_sha256=sha(report.with_suffix('.log')))
    report.write_text(json.dumps(result, indent=2) + '\n')
    print(f'Prepared and inventoried {len(files)} files and {len(links)} symlinks: {source}')


if __name__ == '__main__':
    main()
