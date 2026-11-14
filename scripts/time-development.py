#!/usr/bin/env python3
"""Append one development command's wall time and outcome to a JSONL report."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--iteration', required=True)
    parser.add_argument('--arch', choices=('arm64', 'x86_64'), default='arm64')
    parser.add_argument('--phase', required=True, choices=(
        'build', 'compile', 'link', 'fixture', 'preview', 'checks', 'export',
        'edit-to-preview'))
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a command is required after --')

    # Fail before executing if the report cannot be opened.
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open('a') as report:
        record = dict(iteration=args.iteration, arch=args.arch, phase=args.phase,
                      cwd=str(Path.cwd()), command=command, started_at=timestamp())
        started = time.monotonic()
        try:
            returncode = subprocess.run(command, check=False).returncode
        except OSError as error:
            returncode = 127 if isinstance(error, FileNotFoundError) else 126
            record['launch_error'] = str(error)
            print(f'error: {error}', file=sys.stderr)
        except KeyboardInterrupt:
            returncode = 130
            record['interrupted'] = True
        record.update(finished_at=timestamp(),
                      seconds=round(time.monotonic() - started, 6),
                      returncode=returncode)
        # A signal return code becomes the conventional shell exit status.
        exit_code = 128 - returncode if returncode < 0 else returncode
        record['exit_code'] = exit_code
        report.write(json.dumps(record) + '\n')
        report.flush()
    print(f'{args.iteration} {args.phase} ({args.arch}): '
          f'{record["seconds"]:.3f}s, exit {exit_code}', file=sys.stderr)
    return exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except OSError as error:
        sys.exit(f'error: {error}')
