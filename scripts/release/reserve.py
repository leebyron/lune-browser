#!/usr/bin/env python3
"""Prepare an unused release record; committing it reserves the version."""
import argparse
import json
from pathlib import Path

from model import ARCHES, ROOT, filename, git, sha, version_key, version_parts


def check_allocation(version, allocated):
    day, sequence = version_parts(version)
    if version in allocated:
        raise ValueError('Version already reserved; never reuse it')
    if allocated and version_key(version) <= max(map(version_key, allocated)):
        raise ValueError('Release must be newer than every reserved version')
    same_day = [version_parts(v)[1] for v in allocated if version_parts(v)[0] == day]
    if sequence != max(same_day, default=0) + 1:
        raise ValueError('Use the next sequence for this release date')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version', required=True)
    a = p.parse_args()
    day, sequence = version_parts(a.version)
    if git(ROOT, 'status', '--porcelain'):
        raise ValueError('Commit input and note changes before reserving a release')
    # Fetch first in the runbook. Include abandoned allocations in retained history.
    history = git(ROOT, 'log', '--all', '--format=', '--name-only', '--', 'manifests/releases/*.json')
    allocated = {Path(name).stem for name in history.splitlines() if name.endswith('.json')}
    check_allocation(a.version, allocated)
    names = {'manifests/browser.lock.json', 'manifests/patches.json', 'config/product.json',
             'config/release-recipe.json', f'agent-docs/project/releases/{a.version}.md',
             'agent-docs/project/releases.md', 'agent-docs/project/release-delivery.md'}
    names.update(json.loads((ROOT / 'manifests/browser.lock.json').read_text())['download_configs'])
    names.update(git(ROOT, 'ls-files', 'scripts', 'config/requirements*.txt').splitlines())
    for name in names:
        git(ROOT, 'ls-files', '--error-unmatch', name)
    record = dict(schema_version=1, version=a.version, date=day.isoformat(), sequence=sequence,
                  timezone='America/Los_Angeles', architectures=list(ARCHES), tag='v' + a.version,
                  initial_channel='stable', filenames={arch: filename(a.version, arch) for arch in ARCHES},
                  files={name: sha(ROOT / name) for name in sorted(names)})
    path = ROOT / f'manifests/releases/{a.version}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
