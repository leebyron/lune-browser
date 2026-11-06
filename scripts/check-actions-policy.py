#!/usr/bin/env python3
"""Audit GitHub's repository-wide workflow registry, including imported histories."""
import json
import subprocess
import sys

REPOSITORY = 'leebyron/lune-browser'
ACTIVE = {f'.github/workflows/{name}.yml' for name in ('browser', 'checks', 'website')}


def audit(workflows):
    errors = []
    found = set()
    for workflow in workflows:
        path, state = workflow['path'], workflow['state']
        print(f'{state}: {path}')
        if path in ACTIVE:
            found.add(path)
            if state != 'active':
                errors.append(f'Expected local workflow is not active: {path}')
        elif state not in ('disabled_manually', 'disabled_inactivity', 'deleted'):
            errors.append(f'Unreviewed/inherited workflow can run: {path} ({state}); '
                          'disable it in GitHub Actions before publishing more component/input refs.')
    errors.extend(f'Local workflow missing from registry: {path}' for path in sorted(ACTIVE - found))
    return errors


def main():
    result = subprocess.run(
        ['gh', 'api', '--paginate', '--slurp', f'repos/{REPOSITORY}/actions/workflows'],
        check=True, capture_output=True, text=True)
    pages = json.loads(result.stdout)
    errors = audit([workflow for page in pages for workflow in page['workflows']])
    if errors:
        raise ValueError('\n'.join(errors))
    print('Only the three reviewed local workflows are active.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'error: {error}')
