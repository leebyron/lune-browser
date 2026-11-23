#!/usr/bin/env python3
"""Check quiet session restoration after clean and forced exits.

Launch without ChromeDriver's enable-automation/no-first-run flags, which would
bypass startup notices. Attach only after startup and force-quit only the
disposable browser process.
"""
import argparse
import http.server
import json
from pathlib import Path
import signal
import socket
import subprocess
import threading
import time

import requests
from browser_test_profiles import new_profile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
parser.add_argument('evidence', type=Path)
parser.add_argument('--disable-gpu', action='store_true',
                    help='Use software rendering for the test process.')
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
origin = f'http://127.0.0.1:{server.server_port}'
saved_urls = {origin+'/saved-a', origin+'/saved-b'}
added_url = origin+'/after-recovery'
startup_settings_url = 'chrome://settings/onStartup'
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


def page_targets(port):
    targets = requests.get(f'http://127.0.0.1:{port}/json/list',
                           timeout=10).json()
    return [target for target in targets if target['type'] == 'page']


def wait_for_session_write(profile, since):
    preferences = profile/'Default/Preferences'
    for _ in range(100):
        if (json.loads(preferences.read_text()).get('profile', {}).get('exit_type')
                == 'Crashed' and
                any(file.stat().st_mtime_ns >= since
                    for folder in ('Sessions', 'Sessions_Encrypted')
                    for file in (profile/'Default'/folder).glob('Session_*'))):
            return
        time.sleep(.1)
    raise RuntimeError('Session write did not reach disk before force quit')


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
        case.mkdir(parents=True)
        profile = new_profile('lune-restore-notice-')
        (profile/'Default').mkdir(parents=True)
        (profile/'Default/Preferences').write_text(json.dumps({
            'helium': {'completed_onboarding': completed,
                       'services': {'enabled': False, 'browser_updates': False}}
        }))
        row = {'completed_onboarding': completed, 'gpu_disabled': args.disable_gpu}
        for phase in ('fresh', 'saved', 'crashed', 'crashed-again', 'clean-again'):
            active = profile/'DevToolsActivePort'
            active.unlink(missing_ok=True)
            with (case/f'{phase}.log').open('w') as log:
                session_changed_at = time.time_ns()
                browser = subprocess.Popen([
                    str(build/'Lune.app/Contents/MacOS/Lune'),
                    '--remote-debugging-port=0',
                    f'--user-data-dir={profile}', '--disable-background-networking',
                    *(['--disable-gpu'] if args.disable_gpu else []),
                    '--use-mock-keychain', '--password-store=basic',
                    '--enable-features=SessionRestoreInfobar',
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
                def cdp(command, **params):
                    return wd('POST', sid+'/goog/cdp/execute',
                              {'cmd': command, 'params': params})

                def open_page(url, new_window_type=None):
                    if new_window_type:
                        handle = wd('POST', sid+'/window/new',
                                    {'type': new_window_type})['handle']
                        wd('POST', sid+'/window', {'handle': handle})
                    wd('POST', sid+'/url', {'url': url})

                expected = set() if phase == 'fresh' else set(saved_urls)
                if phase in ('crashed-again', 'clean-again'):
                    expected.add(added_url)
                if phase == 'clean-again' and completed:
                    # This profile explicitly chose New Tab before the force quit.
                    expected.clear()
                restoring_settings = completed and phase in ('crashed', 'crashed-again')
                expected_urls = expected | {startup_settings_url} if restoring_settings else expected
                for _ in range(50):
                    targets = page_targets(debug_port)
                    urls = [target['url'] for target in targets]
                    if expected_urls.issubset(urls):
                        break
                    time.sleep(.1)
                row[phase+'_urls'] = [url.replace(origin, '<fixture>') for url in urls]
                histogram = cdp('Browser.getHistogram',
                                name='Startup.CrashBubbleShown')['histogram']
                row[phase+'_crash_bubble'] = histogram['sum']
                fixture_urls = [url for url in urls if url.startswith(origin+'/')]
                assert sorted(fixture_urls) == sorted(expected), row
                assert histogram['sum'] == 0, row
                assert any('://setup' in url for url in urls) == (not completed), row
                if restoring_settings:
                    assert sorted(urls) == sorted(expected_urls), row
                if saved_urls.issubset(expected):
                    fixture_windows = {
                        cdp('Browser.getWindowForTarget', targetId=target['id'])['windowId']
                        for target in targets if target['url'] in saved_urls
                    }
                    assert len(fixture_windows) == 2, row

                if phase == 'fresh':
                    first, second = sorted(saved_urls)
                    open_page(first, None if completed else 'tab')
                    open_page(second, 'window')
                if phase == 'saved' and completed:
                    session_changed_at = time.time_ns()
                    open_page(startup_settings_url, 'tab')
                    result = wd('POST', sid+'/execute/async', {
                        'script': 'chrome.settingsPrivate.setPref("session.restore_on_startup", '
                                  '5, arguments[arguments.length - 1]);',
                        'args': [],
                    })
                    assert result is True, row

                force_quit = phase in ('saved', 'crashed')
                if force_quit:
                    if phase == 'crashed':
                        session_changed_at = time.time_ns()
                        open_page(added_url, 'tab')
                    wait_for_session_write(profile, session_changed_at)
                    browser.kill()
                else:
                    try:
                        cdp('Browser.close')
                    except (RuntimeError, requests.RequestException):
                        pass
                browser.wait(timeout=30)
                assert browser.returncode == (-signal.SIGKILL if force_quit else 0)
                prefs = json.loads((profile/'Default/Preferences').read_text())
                row[phase+'_exit_type'] = prefs['profile']['exit_type']
                assert row[phase+'_exit_type'] == ('Crashed' if force_quit else 'Normal'), row
                shown = prefs.get('browser', {}).get('session_restore_infobar_times_shown', 0)
                row[phase+'_notice_count'] = shown
                assert shown == 0, row
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
