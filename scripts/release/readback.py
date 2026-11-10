#!/usr/bin/env python3
"""Verify anonymous GitHub feeds and downloads against the publication manifest."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from model import ARCHES, LATEST, feed_url, sha


def fetch(url,path):
    subprocess.run(['curl','--fail','--silent','--show-error','--location','--retry','2',
                    '--output',str(path),url],check=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--channel',choices=['stable','staging'],required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve prior readback evidence')
    data=json.loads((a.directory/'release.json').read_text())
    report=dict(version=data['version'],channel=a.channel,passed=False,checks=[])
    try:
        with tempfile.TemporaryDirectory(prefix='lune-public-readback-') as tmp:
            tmp=Path(tmp)
            for arch in ARCHES:
                name=f'appcast-{arch}.xml';url=feed_url(arch,a.channel)
                path=tmp/name;fetch(url,path)
                if path.read_bytes()!=(a.directory/name).read_bytes():raise ValueError('Public feed differs')
                report['checks'].append({'url':url,'sha256':sha(path)})
                row=data['downloads'][arch]
                urls=[row['url']]
                if a.channel=='stable':urls.append(f"{LATEST}/{row['filename']}")
                for url in urls:
                    path=tmp/row['filename'];fetch(url,path)
                    if sha(path)!=row['sha256']:raise ValueError('Public download differs')
                    report['checks'].append({'url':url,'sha256':sha(path)})
            report['passed']=True
    finally:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
