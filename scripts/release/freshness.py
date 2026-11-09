#!/usr/bin/env python3
"""Record a fresh macOS Stable observation; fail closed on lag or lookup failure."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

URL = 'https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Mac&num=1'


def compare(candidate, response):
    if not isinstance(response, list) or not response:
        raise ValueError('Missing stable release')
    observed = response[0]
    if observed.get('channel') != 'Stable' or observed.get('platform') != 'Mac':
        raise ValueError('Wrong stable channel/platform')
    stable = observed['version']
    if not all(re.fullmatch(r'[0-9]+(?:\.[0-9]+){3}', v) for v in (candidate, stable)):
        raise ValueError('Malformed Chromium version')
    a, b = [tuple(map(int, v.split('.'))) for v in (candidate, stable)]
    return stable, 'current' if a == b else 'behind' if a < b else 'ahead'


def check(candidate):
    evidence = dict(candidate=candidate, checked_at=datetime.now(timezone.utc).isoformat(),
                    source=URL, channel='Stable', platform='Mac', result='unknown', allowed=False)
    try:
        response = json.loads(subprocess.check_output(['curl', '--fail', '--silent', '--show-error',
            '--location', '--max-time', '30', URL], text=True))
        stable, result = compare(candidate, response)
        evidence.update(stable=stable, result=result, response=response, allowed=result in ('current', 'ahead'))
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as error:
        evidence['error'] = str(error)
    return evidence


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chromium', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError('Do not overwrite freshness evidence')
    evidence = check(a.chromium)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({k:v for k,v in evidence.items() if k != 'response'}))
    return 0 if evidence['allowed'] else 1


if __name__ == '__main__':
    sys.exit(main())
