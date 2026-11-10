#!/usr/bin/env python3
"""Prepare unpublished GitHub releases and publish accepted production feeds."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile

from model import ARCHES, DOWNLOADS, REPOSITORY, ROOT, filename, git, load_record, sha, validate_acceptance, version_key
from freshness import check


def gh(*args):
    return subprocess.check_output(['gh', *map(str,args)], text=True).strip()


def manifest(directory, source_checkout=ROOT):
    data=json.loads((directory/'release.json').read_text())
    load_record(data['version'], root=source_checkout)
    if data.get('tag') != 'v' + data['version'] or set(data['downloads']) != set(ARCHES):
        raise ValueError('Invalid release tag or architecture set')
    for arch, row in data['downloads'].items():
        name = filename(data['version'], arch)
        if row['filename'] != name or row['url'] != f"{DOWNLOADS}/{data['tag']}/{name}":
            raise ValueError('Invalid immutable download identity')
        if data['assets'][name] != {'sha256': row['sha256'], 'size': row['size']}:
            raise ValueError('Download metadata differs from asset bytes')
    if {name for name in data['assets'] if name.endswith('.dmg')} != {filename(data['version'], arch) for arch in ARCHES}:
        raise ValueError('Exactly one DMG per architecture is required')
    if data['source_commit'] != git(source_checkout,'rev-parse','HEAD'):
        raise ValueError('Publication must run from the frozen source commit')
    for name,record in data['assets'].items():
        p=(directory/name).resolve()
        if p.parent != directory.resolve() or sha(p)!=record['sha256'] or p.stat().st_size!=record['size']:
            raise ValueError(f'Changed publication asset: {name}')
    validate_acceptance(data, json.loads((directory/'validation.json').read_text()), 'staging')
    return data


def fresh(data,directory,phase):
    evidence=check(data['chromium_version'])
    evidence.update(version=data['version'],source_commit=data['source_commit'],phase=phase)
    path=directory/f'freshness-{phase}-{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")}.json'
    path.write_text(json.dumps(evidence,indent=2)+'\n')
    if not evidence['allowed']:
        raise ValueError(f"Freshness blocks {phase}: {evidence['result']}; see {path}")
    return evidence


def releases():
    # The tag endpoint is for published releases. Authenticated listings also
    # include drafts visible to this repository's publisher.
    return [row for page in json.loads(gh(
        'api', f'repos/{REPOSITORY}/releases', '--paginate', '--slurp'))
        for row in page]


def release(tag):
    matches = [row for row in releases() if row['tag_name'] == tag]
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one visible release for {tag}; found {len(matches)}')
    return matches[0]


def check_assets(data,remote):
    actual={a['name']:a for a in remote['assets']}
    for name,expected in data['assets'].items():
        asset=actual.get(name,{})
        if asset.get('size')!=expected['size'] or asset.get('digest')!='sha256:'+expected['sha256']:
            raise ValueError(f'Published asset mismatch: {name}')


def public_source(data, checkout):
    """Verify anonymous source access at the exact release and component refs."""
    lock = json.loads((checkout/'manifests/browser.lock.json').read_text())
    repository = lock['repository']
    if repository != 'https://github.com/leebyron/lune-browser.git':
        raise ValueError('Unexpected source repository')
    visibility = json.loads(subprocess.check_output([
        'curl', '--fail', '--silent', '--show-error',
        'https://api.github.com/repos/leebyron/lune-browser'], text=True))
    if visibility.get('private') is not False:
        raise ValueError('Source repository is not publicly accessible')
    expected = {f"refs/tags/{data['tag']}": data['source_commit']}
    expected.update({row['ref']: row['commit'] for row in lock['components'].values()})
    refs = [name for ref in expected for name in (ref, ref+'^{}')]
    output = subprocess.check_output([
        'git', '-c', 'credential.helper=', 'ls-remote', '--exit-code',
        repository, *refs], text=True)
    actual = {ref: commit for commit, ref in (line.split() for line in output.splitlines())}
    for ref, commit in expected.items():
        if actual.get(ref+'^{}', actual.get(ref)) != commit:
            raise ValueError(f'Public source ref missing or changed: {ref}')
    return dict(repository=repository, tag=data['tag'], commit=data['source_commit'], refs=expected)


def upload(a):
    data=manifest(a.directory, a.source_checkout)
    source=public_source(data, a.source_checkout)
    # Public Git refs provide source; release uploads contain browser delivery only.
    paths=[a.directory/name for name in data['assets']]+[a.directory/'release.json',a.directory/'SHA256SUMS']
    fresh(data,a.directory,'candidate')
    existing=releases()
    if any(r['tag_name']==data['tag'] for r in existing):
        raise ValueError('Release already exists; inspect it rather than replacing assets')
    notes=a.notes_file or a.source_checkout/f"agent-docs/project/releases/{data['version']}.md"
    gh('release','create',data['tag'],'--repo',REPOSITORY,'--draft',
       '--title',f"Lune {data['version']}",'--notes-file',notes)
    for path in paths:
        gh('release','upload',data['tag'],path,'--repo',REPOSITORY)
    remote=release(data['tag']);check_assets(data,remote)
    # Verify every uploaded file using GitHub's server-computed digest.
    uploaded={x['name']:x for x in remote['assets']}
    for path in paths:
        if uploaded[path.name].get('digest')!='sha256:'+sha(path):
            raise ValueError(f'Uploaded bytes differ: {path.name}')
    receipt = dict(version=data['version'], source_commit=data['source_commit'],
                   assets={p.name: dict(sha256=sha(p), size=p.stat().st_size) for p in paths},
                   publisher_commit=git(ROOT, 'rev-parse', 'HEAD'), public_source=source)
    (a.directory/'upload-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print('Verified draft uploaded. It remains unpublished until production acceptance passes.')


def promote(a):
    data=manifest(a.directory, a.source_checkout);remote=release(data['tag'])
    check_assets(data,remote)
    receipt=json.loads((a.directory/'upload-receipt.json').read_text())
    if receipt['version'] != data['version'] or receipt['source_commit'] != data['source_commit']:
        raise ValueError('Upload receipt identifies a different release')
    check_assets(receipt,remote)
    if 'public_source' in receipt and public_source(data, a.source_checkout) != receipt['public_source']:
        raise ValueError('Public source identity changed since upload')
    validate_acceptance(data, json.loads(a.acceptance.read_text()), a.channel)
    acceptance=json.loads(a.acceptance.read_text())
    if a.channel=='stable':
        published=releases()
        for r in published:
            if not r['draft'] and not r['prerelease'] and r['tag_name'].startswith('v'):
                if version_key(r['tag_name'][1:])>version_key(data['version']):
                    raise ValueError('A newer stable release is already published')
    # GitHub public feeds are maintained together in one ordinary, fast-forward commit.
    repo=a.checkout.resolve()
    if git(repo,'status','--porcelain') or git(repo,'branch','--show-current')!='main':
        raise ValueError('Public feed checkout must be clean on main')
    url=git(repo,'remote','get-url','origin')
    if url not in (f'https://github.com/{REPOSITORY}.git',f'git@github.com:{REPOSITORY}.git'):
        raise ValueError('Wrong public repository')
    subprocess.run(['git','-C',repo,'pull','--ff-only','origin','main'],check=True)
    current=repo/f'updates/{a.channel}/release.json'
    if current.exists():
        old=json.loads(current.read_text())
        if version_key(old['version'])>version_key(data['version']):
            raise ValueError('Refuse stale feed promotion')
        if old['version']==data['version'] and old!=data:
            raise ValueError('Same version has different publication data')
    # Validate acceptance and any recorded owner deferral before public changes.
    if remote['prerelease']:
        raise ValueError('Production delivery does not promote prereleases')
    fresh(data,a.directory,'production-publication')
    if remote['draft']:
        gh('release','edit',data['tag'],'--repo',REPOSITORY,
           '--draft=false','--prerelease=false','--latest=false')
    # Anonymous byte verification precedes any moving link change.
    for arch,row in data['downloads'].items():
        with tempfile.TemporaryDirectory(prefix='lune-readback-') as tmp:
            p=Path(tmp)/row['filename']
            subprocess.run(['curl','--fail','--location','--retry','2','--output',p,row['url']],check=True)
            if sha(p)!=row['sha256']:raise ValueError('Anonymous download hash mismatch')
    observation=fresh(data,a.directory,a.channel)
    for arch in ARCHES:
        path=repo/f'updates/{a.channel}/mac/appcast-{arch}.xml';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((a.directory/f'appcast-{arch}.xml').read_bytes())
    current.write_bytes((a.directory/'release.json').read_bytes())
    (current.parent/'acceptance.json').write_text(json.dumps(acceptance,indent=2)+'\n')
    (current.parent/'freshness.json').write_text(json.dumps(observation,indent=2)+'\n')
    subprocess.run(['git','-C',repo,'add',f'updates/{a.channel}'],check=True)
    if git(repo,'diff','--cached','--name-only'):
        subprocess.run(['git','-C',repo,'commit','-m',f"Promote Lune {data['version']} to {a.channel}"],check=True)
    subprocess.run(['git','-C',repo,'push','origin','main'],check=True)
    if a.channel=='stable':
        gh('release','edit',data['tag'],'--repo',REPOSITORY,'--prerelease=false','--latest=true')
    print('Feeds published; verify raw feed and latest-link readback before deploying the website.')


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('upload','promote'):
        q=sub.add_parser(name);q.add_argument('--directory',type=Path,required=True)
        q.add_argument('--source-checkout',type=Path,default=ROOT,
                       help='Clean checkout of the exact frozen browser source commit')
        if name=='upload':
            q.add_argument('--notes-file',type=Path)
        else:
            q.add_argument('--channel',choices=['stable'],default='stable')
            q.add_argument('--acceptance',type=Path,required=True);q.add_argument('--checkout',type=Path,required=True)
    a=p.parse_args()
    if git(ROOT, 'status', '--porcelain'):
        raise ValueError('Commit publication-tool changes before use')
    globals()[a.command](a)


if __name__=='__main__':main()
