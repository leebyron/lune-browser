#!/usr/bin/env python3
"""Check the startup notice with real session files and both setup states.

Launch without ChromeDriver's enable-automation/no-first-run flags, which would
suppress the notice being tested. Attach only after the browser has started.
"""
import argparse
import http.server
import json
from pathlib import Path
import socket
import subprocess
import threading
import time

import requests

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
parser.add_argument('evidence', type=Path)
args = parser.parse_args()
build = args.output.resolve()
evidence = args.evidence.resolve()
evidence.mkdir(parents=True, exist_ok=False)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'<title>Saved session fixture</title><p>Saved tab</p>'
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
saved_url = f'http://127.0.0.1:{server.server_port}/saved'
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
driver_log = (evidence/'driver.log').open('w')
driver = subprocess.Popen([str(build/'chromedriver'), f'--port={port}',
                           '--allowed-ips=127.0.0.1'],
                          stdout=driver_log, stderr=subprocess.STDOUT)


def wd(method, path, data=None):
    response = requests.request(method, f'http://127.0.0.1:{port}'+path,
                                json=data, timeout=60)
    value = response.json()['value']
    if isinstance(value, dict) and 'error' in value:
        raise RuntimeError(value)
    return value


results = []
browser = None
try:
    for attempt in range(100):
        try:
            if wd('GET', '/status')['ready']:
                break
        except requests.RequestException:
            pass
        time.sleep(.1)
    else:
        raise RuntimeError('ChromeDriver did not start')

    for completed in (False, True):
        case = evidence/('setup-complete' if completed else 'setup-incomplete')
        profile = case/'profile'
        (profile/'Default').mkdir(parents=True)
        (profile/'Default/Preferences').write_text(json.dumps({
            'helium': {'completed_onboarding': completed,
                       'services': {'enabled': False, 'browser_updates': False}}
        }))
        row = {'completed_onboarding': completed}
        for phase in ('fresh', 'saved'):
            active = profile/'DevToolsActivePort'
            active.unlink(missing_ok=True)
            with (case/f'{phase}.log').open('w') as log:
                browser = subprocess.Popen([
                    str(build/'Lune.app/Contents/MacOS/Lune'),
                    '--remote-debugging-port=0',
                    f'--user-data-dir={profile}', '--disable-background-networking',
                    '--use-mock-keychain', '--password-store=basic',
                    '--custom-update-server-url=http://127.0.0.1:1/',
                    '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1'
                ], stdout=log, stderr=subprocess.STDOUT)
                for attempt in range(900):
                    if browser.poll() is not None:
                        raise RuntimeError(f'{phase}: browser exited early')
                    if active.exists() and active.read_text().splitlines():
                        break
                    time.sleep(.1)
                else:
                    raise RuntimeError('No DevTools port')
                debug_port = int(active.read_text().splitlines()[0])
                session = wd('POST', '/session', {'capabilities': {'alwaysMatch': {
                    'goog:chromeOptions': {'debuggerAddress': f'127.0.0.1:{debug_port}'}
                }}})
                sid = '/session/'+session['sessionId']
                time.sleep(1)
                targets = requests.get(f'http://127.0.0.1:{debug_port}/json/list',
                                       timeout=10).json()
                urls = [target['url'] for target in targets if target['type'] == 'page']
                row[phase+'_urls'] = [url.replace(saved_url, '<saved-tab>') for url in urls]
                row[phase+'_has_saved_tab'] = saved_url in urls
                assert row[phase+'_has_saved_tab'] == (phase == 'saved'), row
                row[phase+'_has_setup_tab'] = any('://setup' in url for url in urls)
                if not completed:
                    assert row[phase+'_has_setup_tab'], row
                if phase == 'fresh':
                    handle = wd('POST', sid+'/window/new', {'type': 'tab'})['handle']
                    wd('POST', sid+'/window', {'handle': handle})
                    wd('POST', sid+'/url', {'url': saved_url})
                try:
                    wd('POST', sid+'/goog/cdp/execute', {'cmd': 'Browser.close', 'params': {}})
                except (RuntimeError, requests.RequestException):
                    pass
                browser.wait(timeout=30)
                assert browser.returncode == 0, browser.returncode
                prefs = json.loads((profile/'Default/Preferences').read_text())
                assert prefs['profile']['exit_type'] == 'Normal', prefs['profile']
                shown = prefs.get('browser', {}).get('session_restore_infobar_times_shown', 0)
                row[phase+'_notice_count'] = shown
                assert shown == (0 if phase == 'fresh' else 1), row
                try:
                    wd('DELETE', sid)
                except (RuntimeError, requests.RequestException):
                    pass
        row['passed'] = True
        results.append(row)
        print(json.dumps(row), flush=True)
        (evidence/'report.json').write_text(json.dumps(results, indent=2)+'\n')
finally:
    if browser is not None and browser.poll() is None:
        browser.terminate()
        browser.wait(timeout=15)
    driver.terminate()
    driver.wait(timeout=15)
    driver_log.close()
    server.shutdown()
