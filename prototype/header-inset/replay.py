#!/usr/bin/env python3
"""Strictly replay and reverse the prototype delta against quilt preimages."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('evidence', type=Path)
args = parser.parse_args()
source = args.source.resolve()
platform = Path(__file__).resolve().parents[2]
names = ['helium/ui/obscured-header-prototype.patch',
         'helium/ui/obscured-header-cover-prototype.patch',
         'helium/ui/obscured-header-menu-prototype.patch']
args.evidence.mkdir(parents=True, exist_ok=True)
patches = [platform/'patches'/name for name in names]
baseline = {}
for name, patch in zip(names, patches):
    assert '+++ b/' in patch.read_text(), f'Expected a/b patch paths: {patch}'
    for line in patch.read_text().splitlines():
        if line.startswith('+++ b/'):
            baseline.setdefault(line[6:], source/'.pc'/name/line[6:])
patch_tool = shutil.which('gpatch')
assert patch_tool, 'GNU patch is required'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='replay-', dir=args.evidence) as temp:
    scratch = Path(temp)
    for name, original in baseline.items():
        dest = scratch/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, dest)
    def apply(patch, reverse=False):
        command = [patch_tool, '--batch', '--fuzz=0', '-p1', '-i', str(patch)]
        if reverse:
            command.append('-R')
        result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
    for patch in patches:
        apply(patch)
    final = {}
    for name in baseline:
        assert (scratch/name).read_bytes() == (source/name).read_bytes(), name
        final[name] = digest(source/name)
    for patch in reversed(patches):
        apply(patch, reverse=True)
    for name, original in baseline.items():
        assert (scratch/name).read_bytes() == original.read_bytes(), name
report = {'forward_and_reverse_match': True,
          'patches': {name:digest(patch) for name,patch in zip(names,patches)},
          'files': final}
(args.evidence/'replay.json').write_text(json.dumps(report, indent=2)+'\n')
print(f'Strict forward/reverse replay passed for {len(baseline)} files')
