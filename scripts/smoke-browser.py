#!/usr/bin/env python3
"""Smoke-test the built app via its matching ChromeDriver and an isolated profile.

Only loopback pages are loaded. This is not signing, Gatekeeper, or update testing.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import socket
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.request import Request, build_opener, ProxyHandler


class Page(BaseHTTPRequestHandler):
    def do_GET(self):
        write = "localStorage.setItem('lune-smoke', 'persisted');" if self.path == '/write' else ''
        data = ("<!doctype html><title>Lune build smoke</title><body><h1>Lune</h1><script>"
                + write + "document.body.dataset.runtime = 'ok';</script></body>").encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_output', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    output = args.build_output.resolve()
    app = output / 'Lune.app'
    with (app / 'Contents/Info.plist').open('rb') as f:
        info = plistlib.load(f)
    if info['CFBundleIdentifier'] != 'computer.lune.browser':
        raise RuntimeError('Unexpected bundle identity.')
    binary = app / 'Contents/MacOS' / info['CFBundleExecutable']
    architecture = subprocess.check_output(['/usr/bin/lipo', '-archs', binary], text=True).strip()
    if architecture != 'arm64':
        raise RuntimeError(f'This first-build smoke test expects arm64, got {architecture}.')
    driver = output / 'chromedriver'
    version = subprocess.check_output([driver, '--version'], text=True).strip()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Page)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    opener = build_opener(ProxyHandler({}))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    log = args.report.with_suffix('.chromedriver.log')

    def request(method, path, body=None):
        req = Request(base + path, method=method,
                      data=None if body is None else json.dumps(body).encode(),
                      headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=60) as response:
            value = json.load(response)['value']
        if isinstance(value, dict) and 'error' in value:
            raise RuntimeError(value)
        return value

    report = {'bundle_id': info['CFBundleIdentifier'], 'architecture': architecture,
              'driver_version': version, 'app_version': info['CFBundleShortVersionString'],
              'checks': [], 'mode': 'headless', 'release_validated': False}
    try:
        with tempfile.TemporaryDirectory(prefix='lune-smoke-profile-') as profile, log.open('w') as logfile:
            env = {key: os.environ[key] for key in
                   ('HOME', 'USER', 'LOGNAME', 'PATH', 'TMPDIR', 'LC_ALL', 'DEVELOPER_DIR')
                   if key in os.environ}
            process = subprocess.Popen([driver, f'--port={port}', '--allowed-ips=127.0.0.1'],
                                       stdout=logfile, stderr=subprocess.STDOUT, env=env)
            session = None
            try:
                for _ in range(60):
                    if process.poll() is not None:
                        raise RuntimeError(f'ChromeDriver exited; see {log}')
                    try:
                        if request('GET', '/status').get('ready'):
                            break
                    except (URLError, ConnectionError):
                        pass
                    time.sleep(0.5)
                else:
                    raise RuntimeError('ChromeDriver did not become ready.')
                for phase in ('write', 'read'):
                    created = request('POST', '/session', {'capabilities': {'alwaysMatch': {
                        'goog:chromeOptions': {'binary': str(binary), 'args': [
                            '--headless=new', '--no-first-run', '--no-default-browser-check',
                            '--disable-background-networking', f'--user-data-dir={profile}']}}}})
                    session = created['sessionId']
                    path = '/session/' + session
                    request('POST', path + '/url', {'url': f'http://127.0.0.1:{server.server_port}/{phase}'})
                    title = request('GET', path + '/title')
                    result = request('POST', path + '/execute/sync', {
                        'script': "return {runtime:document.body.dataset.runtime,stored:localStorage.getItem('lune-smoke')};", 'args': []})
                    if title != 'Lune build smoke' or result != {'runtime': 'ok', 'stored': 'persisted'}:
                        raise RuntimeError(f'Browser smoke failed in {phase}: {title!r}, {result!r}')
                    report['checks'].append({'phase': phase, 'title': title, **result})
                    request('DELETE', path)
                    session = None
                report['passed'] = True
            finally:
                if session:
                    try:
                        request('DELETE', '/session/' + session)
                    except Exception:
                        pass
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    finally:
        server.shutdown()
        server.server_close()
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
