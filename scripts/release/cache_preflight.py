"""Ask Siso for its actual build plan before permitting compilation."""
import os
from pathlib import Path
import re
import subprocess

from cache_reuse import PENDING


def check(source, out, targets, env, log_path):
    source, out = source.resolve(), out.resolve()
    log_path = Path(log_path).resolve()
    if (source / 'out' / PENDING).exists():
        raise ValueError('Incomplete cache transfer; preserve and inspect its workspace/report')
    explain = Path(log_path).with_suffix('.explain')
    if explain.exists():
        raise ValueError('Preserve existing cache-preflight explanation')
    with Path(log_path).open('x') as log:
        subprocess.run([source / 'third_party/siso/cipd/siso', 'ninja',
                        '--fast_local', '-n', '-C', out,
                        '-explain_log=' + str(explain), *targets],
                       cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    missing, reasons = [], {}
    if explain.exists():
        for line in explain.read_text().splitlines():
            reason = None
            if 'missing-inputs:' in line:
                reason = 'missing_dependency'
            elif re.search(r'^deps for .+ dirty:', line):
                reason = 'dirty_dependency'
            elif line.startswith('command line changed for '):
                reason = 'command_changed'
            elif ' older than most recent input ' in line:
                reason = 'newer_input'
            elif line.startswith('output ') and "doesn't exist" in line:
                reason = 'missing_output'
            if reason:
                reasons[reason] = reasons.get(reason, 0) + 1
            match = re.search(r'missing-inputs: input (.+?): (?:stat|lstat|file)', line)
            if match and os.path.isabs(match[1]):
                path = Path(match[1]).resolve()
                if not path.is_relative_to(source):
                    missing.append(str(path))
    if missing:
        raise ValueError('Cache contains missing dependencies outside this workspace; '
                         'repair cache relocation or choose a cold build before compiling: '
                         + repr(sorted(set(missing))[:8]))
    return {'dry_run_passed': True, 'invalidation_reasons': reasons,
            'log': str(log_path), 'explain': str(explain)}
