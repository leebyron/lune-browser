#!/usr/bin/env python3
"""Verify a signed release's displayed identity and public browsing in a disposable profile."""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import platform
import re
import threading

from check_update import info, run, session, smoke, verify


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', type=Path, required=True)
    parser.add_argument('--driver', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--chromium-version', required=True)
    parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    args = parser.parse_args()
    app = args.app.resolve()
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    report = dict(version=args.version, chromium_version=args.chromium_version,
                  architecture=args.arch, host_architecture=platform.machine(),
                  native_hardware=platform.machine() == args.arch,
                  timestamp=datetime.now(timezone.utc).isoformat(), passed=False)
    fixture = ThreadingHTTPServer(('127.0.0.1', 0), smoke.Page)
    threading.Thread(target=fixture.serve_forever, daemon=True).start()
    try:
        verify(app)
        plist = info(app)
        assert plist['CFBundleVersion'] == args.version
        assert plist['CFBundleShortVersionString'] == args.version
        assert plist['LuneReleaseVersion'] == args.version
        binary = app/'Contents/MacOS/Lune'
        assert run('lipo', '-archs', binary).strip() == args.arch
        report.update(source_commit=plist['LuneSourceRevision'],
                      executable_sha256=digest(binary),
                      signed_app=True, minimum_system_version=plist['LSMinimumSystemVersion'],
                      feed=plist['SUFeedURL'])
        report['macho_minimums'] = {}
        for path in [binary, app/'Contents/Frameworks/Lune Framework.framework/Lune Framework']:
            build = run('xcrun', 'vtool', '-show-build', path)
            minimum = re.search(r'\bminos\s+(\S+)', build).group(1)
            assert tuple(map(int, minimum.split('.'))) <= (13, 0)
            report['macho_minimums'][str(path.relative_to(app))] = minimum
        for phase in ('before', 'after'):
            with session(app, args.driver.resolve(), directory/'profile',
                         directory/f'{phase}.log', ['--host-resolver-rules=']) as request:
                def js(script, asynchronous=False):
                    return request('POST', '/execute/' + ('async' if asynchronous else 'sync'),
                                   {'script': script, 'args': []})
                request('POST', '/url', {'url': f'http://127.0.0.1:{fixture.server_port}/' +
                        ('write' if phase == 'before' else 'read')})
                assert js("return localStorage.getItem('lune-smoke');") == 'persisted'
                if phase == 'after':
                    report['profile_persistence'] = True
                    continue
                request('POST', '/url', {'url': 'lune://version'})
                identity = js("""return {lune:document.querySelector('#copy-content-helium > span')?.textContent.trim(),
                    chromium:document.querySelector('#copy-content > span')?.textContent.trim(),
                    text:document.body.innerText};""")
                assert identity['lune'] == args.version, identity
                assert args.chromium_version in identity['text'], identity
                report['version_page'] = identity
                request('POST', '/url', {'url': 'lune://settings/help'})
                about = js("""const done=arguments[arguments.length-1];
                    import('chrome://resources/js/load_time_data.js')
                      .then(m=>done(m.loadTimeData.getString('aboutBrowserVersion')))
                      .catch(e=>done({error:String(e)}));""", True)
                assert isinstance(about, str) and args.version in about, about
                report['about_version'] = about
                report['public_pages'] = []
                for url, expected in [('https://example.com/', 'Example Domain'),
                                      ('https://lune.computer/', 'Lune')]:
                    request('POST', '/url', {'url': url})
                    page = js('return {url:location.href,title:document.title,text:document.body.innerText};')
                    assert page['url'].startswith(url) and expected in page['text'], page
                    report['public_pages'].append(dict(url=page['url'], title=page['title']))
        report.update(browse=True, passed=True)
    except Exception as error:
        report['error'] = repr(error)
        raise
    finally:
        fixture.shutdown()
        (directory/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
