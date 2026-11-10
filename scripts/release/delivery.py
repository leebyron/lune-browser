#!/usr/bin/env python3
"""Prepare immutable GitHub release assets and architecture-specific feed files.

This command only stages local files. Publication and promotion require fresh
Chromium checks, public readback, and the acceptance gates in the release runbook.
"""
import argparse
import json
from pathlib import Path
import shutil
from model import ARCHES, DOWNLOADS, filename, load_record, sha, validate_acceptance
from appcast import make_feed, validate_candidate


def prepare(directories, destination, evidence):
    if destination.exists(): raise ValueError('Never replace a staged publication')
    candidates = [json.loads((d / 'candidate.json').read_text()) for d in directories]
    if len(candidates) != 2 or {c['arch'] for c in candidates} != set(ARCHES):
        raise ValueError('Both architecture candidates are required')
    for field in ('version', 'orchestrator_commit', 'lock_sha256', 'core_commit', 'platform_commit', 'release_record_sha256', 'chromium_version', 'minimum_system_version'):
        if len({c[field] for c in candidates}) != 1:
            raise ValueError(f'Candidates differ in {field}')
    version = candidates[0]['version']
    load_record(version)
    for d,c in zip(directories,candidates): validate_candidate(c,d/c['filename'])
    validation = dict(version=version, source_commit=candidates[0]['orchestrator_commit'],
                      downloads={c['arch']: {'sha256': c['sha256']} for c in candidates})
    validate_acceptance(validation, evidence, 'staging')
    destination.mkdir(parents=True)
    assets = {}; downloads = {}
    for d,c in zip(directories,candidates):
        name=c['filename']
        shutil.copyfile(d/name,destination/name)
        assets[name] = {'sha256':sha(destination/name),'size':(destination/name).stat().st_size}
        url=f'{DOWNLOADS}/v{version}/{name}'
        feed=f"appcast-{c['arch']}.xml"
        (destination/feed).write_bytes(make_feed(c,url))
        assets[feed]={'sha256':sha(destination/feed),'size':(destination/feed).stat().st_size}
        downloads[c['arch']]={'url':url,'filename':name,'sha256':c['sha256'],'size':c['size']}
    manifest=dict(schema_version=1,version=version,tag='v'+version,
                  source_commit=candidates[0]['orchestrator_commit'],chromium_version=candidates[0]['chromium_version'],
                  minimum_system_version=candidates[0]['minimum_system_version'],downloads=downloads,assets=assets)
    (destination/'validation.json').write_text(json.dumps(evidence, indent=2)+'\n')
    assets['validation.json'] = {'sha256': sha(destination/'validation.json'), 'size': (destination/'validation.json').stat().st_size}
    (destination/'release.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (destination/'SHA256SUMS').write_text(''.join(f"{v['sha256']}  {name}\n" for name,v in sorted(assets.items()))+
                                         f"{sha(destination/'release.json')}  release.json\n")
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--arm64',type=Path,required=True);p.add_argument('--x86-64',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--evidence',type=Path,required=True);a=p.parse_args()
    prepare([a.arm64,a.x86_64],a.output,json.loads(a.evidence.read_text()))


if __name__=='__main__':main()
