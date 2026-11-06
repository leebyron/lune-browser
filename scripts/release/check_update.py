#!/usr/bin/env python3
"""Exercise a notarized DMG install and Sparkle update in an isolated directory."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import plistlib
import socket
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.request import Request, build_opener, ProxyHandler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('smoke', Path(__file__).resolve().parents[1] / 'smoke-browser.py')
smoke = module_from_spec(spec)
spec.loader.exec_module(smoke)


def run(*args):
    return subprocess.run([str(a) for a in args], check=True, text=True, capture_output=True).stdout


def info(app):
    return plistlib.loads((app / 'Contents/Info.plist').read_bytes())


def verify(app):
    run('codesign', '--verify', '--deep', '--strict', app)
    run('xcrun', 'stapler', 'validate', app)
    run('spctl', '--assess', '--type', 'execute', app)


@contextmanager
def session(app, driver, profile, log):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    opener = build_opener(ProxyHandler({}))
    def request(method, path, data=None):
        req = Request(f'http://127.0.0.1:{port}' + path, method=method,
                      data=None if data is None else json.dumps(data).encode(),
                      headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=90) as response:
            return json.load(response)['value']
    with log.open('w') as stream:
        process = subprocess.Popen([str(driver), f'--port={port}', '--allowed-ips=127.0.0.1'],
                                   stdout=stream, stderr=subprocess.STDOUT)
        path = None
        try:
            for _ in range(120):
                try:
                    if request('GET', '/status')['ready']:
                        break
                except OSError:
                    pass
                time.sleep(.5)
            else:
                raise RuntimeError('ChromeDriver startup timeout')
            value = request('POST', '/session', {'capabilities': {'alwaysMatch': {
                'goog:chromeOptions': {'binary': str(app / 'Contents/MacOS/Lune'), 'args': [
                    '--headless=new', '--no-first-run', '--no-default-browser-check',
                    '--disable-background-networking', '--password-store=basic', '--use-mock-keychain',
                    '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',
                    f'--user-data-dir={profile}']}}}})
            path = '/session/' + value['sessionId']
            yield lambda method, suffix, data=None: request(method, path + suffix, data)
        finally:
            if path:
                request('DELETE', path)
            process.terminate()
            process.wait(timeout=30)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-dmg', type=Path, required=True)
    p.add_argument('--driver', type=Path, required=True)
    p.add_argument('--sparkle-cli', type=Path, required=True)
    p.add_argument('--feed', required=True)
    p.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--expected-build', type=int, default=2)
    a = p.parse_args()
    a.directory = a.directory.resolve()
    a.directory.mkdir(parents=True, exist_ok=False)
    app = a.directory / 'Lune.app'
    report = {'architecture': a.arch, 'feed': a.feed, 'passed': False,
              'updater': 'Sparkle CLI using the app key; native UI integration tested separately'}
    fixture = ThreadingHTTPServer(('127.0.0.1', 0), smoke.Page)
    threading.Thread(target=fixture.serve_forever, daemon=True).start()
    try:
        mounted = plistlib.loads(subprocess.check_output(['hdiutil', 'attach', '-readonly', '-nobrowse', '-plist', str(a.baseline_dmg.resolve())]))
        volume = next(Path(e['mount-point']) for e in mounted['system-entities'] if 'mount-point' in e)
        try:
            run('ditto', volume / 'Lune.app', app)
        finally:
            run('hdiutil', 'detach', volume)
        verify(app)
        report['before_build'] = info(app)['CFBundleVersion']
        if int(report['before_build']) >= a.expected_build:
            raise ValueError('Baseline must be older than the candidate')
        profile = a.directory / 'profile'
        for phase in ['before', 'after']:
            with session(app, a.driver.resolve(), profile, a.directory / f'{phase}.log') as request:
                route = 'write' if phase == 'before' else 'read'
                request('POST', '/url', {'url': f'http://127.0.0.1:{fixture.server_port}/{route}'})
                stored = request('POST', '/execute/sync', {'script': "return localStorage.getItem('lune-smoke');", 'args': []})
                if stored != 'persisted':
                    raise RuntimeError('Installed browser profile did not persist')
            if phase == 'before':
                result = subprocess.run([str(a.sparkle_cli.resolve()), str(app), '--check-immediately',
                    '--feed-url', a.feed, '--user-agent-name', 'Lune release validation', '--verbose'],
                    text=True, capture_output=True, timeout=900)
                (a.directory / 'sparkle.log').write_text(result.stdout + result.stderr)
                result.check_returncode()
                verify(app)
                if info(app)['CFBundleVersion'] != str(a.expected_build):
                    raise RuntimeError('Sparkle did not install the expected build')
                if run('lipo', '-archs', app / 'Contents/MacOS/Lune').strip() != a.arch:
                    raise RuntimeError('Updated app architecture changed')
        report.update(after_build=info(app)['CFBundleVersion'], profile_persisted=True,
                      relaunch_passed=True, signatures_and_gatekeeper_passed=True, passed=True)
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        fixture.shutdown()
        (a.directory / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
