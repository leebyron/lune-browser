#!/usr/bin/env python3
"""Check upstream suggestion toggles with an isolated browser profile and loopback data."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, build_opener, ProxyHandler


def check(app, driver, report_path):
    report = {'passed': False, 'app': str(app), 'checks': {}}
    class Page(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b'<!doctype html><title>Lune history probe</title><h1>History fixture</h1>'
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Page)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    opener = build_opener(ProxyHandler({}))
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    process = None
    session = None
    report_path.parent.mkdir(parents=True, exist_ok=True)
    def request(method, path, data=None):
        req = Request(f'http://127.0.0.1:{port}{path}', method=method,
                      data=None if data is None else json.dumps(data).encode(),
                      headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=90) as response:
            result = json.load(response)['value']
        if isinstance(result, dict) and 'error' in result:
            raise RuntimeError(result)
        return result
    try:
        with tempfile.TemporaryDirectory(prefix='lune-autocomplete-') as profile, \
             report_path.with_suffix('.driver.log').open('w') as log:
            # Chromium gates developer WebUIs in official builds. Enable the
            # diagnostic controller only in this disposable profile.
            (Path(profile) / 'Local State').write_text(json.dumps({
                'internal_only_uis_enabled': True}))
            process = subprocess.Popen([str(driver), f'--port={port}', '--allowed-ips=127.0.0.1'],
                                       stdout=log, stderr=subprocess.STDOUT)
            for _ in range(100):
                try:
                    if request('GET', '/status')['ready']:
                        break
                except OSError:
                    time.sleep(.1)
            def start():
                return '/session/' + request('POST', '/session', {'capabilities': {'alwaysMatch': {
                    'goog:chromeOptions': {'binary': str(app / 'Contents/MacOS/Lune'), 'args': [
                        '--headless=new', '--no-first-run', '--no-default-browser-check',
                        '--disable-background-networking', '--use-mock-keychain',
                        '--password-store=basic', '--custom-update-server-url=http://127.0.0.1:1/',
                        f'--user-data-dir={profile}']}}}})['sessionId']
            session = start()
            def nav(url):
                request('POST', session + '/url', {'url': url})
            def js(script, args=None, asynchronous=False):
                return request('POST', session + '/execute/' + ('async' if asynchronous else 'sync'),
                               {'script': script, 'args': args or []})
            def wait(script, args=None):
                for _ in range(100):
                    value = js(script, args)
                    if value:
                        return value
                    time.sleep(.1)
                raise AssertionError('Timed out: ' + script)
            keys = ['helium.omnibox.autocomplete.history_enabled',
                    'helium.omnibox.autocomplete.bookmark_enabled']
            def prefs(values=None):
                nav('chrome://settings/search')
                wait('return !!chrome.settingsPrivate;')
                if values is not None:
                    results = js('''const [keys, values] = arguments; const done = arguments[arguments.length-1];
                      Promise.all(keys.map((key, i) => new Promise(resolve =>
                        chrome.settingsPrivate.setPref(key, values[i], '', resolve)))).then(done);''',
                                 [keys, values], True)
                    assert results == [True, True], results
                return js('''const keys=arguments[0], done=arguments[arguments.length-1];
                    Promise.all(keys.map(key=>new Promise(resolve=>chrome.settingsPrivate.getPref(key,
                      pref=>resolve(pref.value))))).then(done);''', [keys], True)
            assert prefs() == [True, True]
            report['checks']['enabled_by_default'] = True
            wait('''const find=root=>{if(root.querySelector('#localSuggestionsBookmarksToggle'))return true;
                return [...root.querySelectorAll('*')].some(e=>e.shadowRoot&&find(e.shadowRoot));}; return find(document);''')
            report['checks']['packaged_settings_controls'] = True
            nav('chrome://bookmarks/')
            wait('return !!chrome.bookmarks;')
            bookmark_url = f'http://127.0.0.1:{server.server_port}/bookmark-only'
            js('''const done=arguments[arguments.length-1];chrome.bookmarks.create(
                {title:'Lune bookmark probe',url:arguments[0]},done);''', [bookmark_url], True)
            history_url = f'http://127.0.0.1:{server.server_port}/lune-history-probe'
            original_window = request('GET', session + '/window')
            history_window = request('POST', session + '/window/new', {'type': 'tab'})['handle']
            request('POST', session + '/window', {'handle': history_window})
            for _ in range(20):
                report['history_navigation'] = request('POST', session + '/goog/cdp/execute', {
                    'cmd': 'Page.navigate', 'params': {'url': history_url, 'transitionType': 'typed'}})
                time.sleep(.25)
                if js("return document.title === 'Lune history probe';"):
                    break
            else:
                raise AssertionError('History fixture did not load')
            # Close the fixture so an open-tab match cannot masquerade as history.
            request('DELETE', session + '/window')
            request('POST', session + '/window', {'handle': original_window})
            history_query = history_url.removesuffix('probe')
            def query(text):
                nav('chrome://omnibox-internals/')
                wait("return !!document.querySelector('omnibox-input')?.shadowRoot;")
                js('''const q=arguments[0]; document.querySelector('omnibox-input').dispatchEvent(
                  new CustomEvent('query-inputs-changed', {detail:{inputText:q,
                  resetAutocompleteController:true,cursorLock:false,cursorPosition:q.length,
                  zeroSuggest:false,preventInlineAutocomplete:true,inKeywordMode:false,currentUrl:'',
                  pageClassification:0}}));''', [text])
                return wait('''return document.querySelector('omnibox-output').responsesHistory.flat()
                    .find(r=>r.done&&r.inputText===arguments[0]);''', [text])
            def has(response, url):
                report['last_response'] = response
                return any(m['destinationUrl'] == url for group in response['resultsByProvider']
                           for m in group['results'])
            assert has(query('Lune bookmark probe'), bookmark_url)
            assert has(query(history_query), history_url)
            report['checks']['enabled_providers_return_fixtures'] = True
            assert prefs([False, True]) == [False, True]
            assert has(query('Lune bookmark probe'), bookmark_url)
            assert not has(query(history_query), history_url)
            assert prefs([True, False]) == [True, False]
            assert not has(query('Lune bookmark probe'), bookmark_url)
            assert has(query(history_query), history_url)
            report['checks']['independent_provider_toggles'] = True
            assert prefs([False, False]) == [False, False]
            assert not has(query('Lune bookmark probe'), bookmark_url)
            assert not has(query(history_query), history_url)
            response = query('https://example.com/')
            assert any(m['destinationUrl'] == 'https://example.com/'
                       for m in response['combinedResults'])
            report['checks']['disabled_providers_and_direct_url'] = True
            request('DELETE', session)
            session = None
            session = start()
            assert prefs() == [False, False]
            report['checks']['restart_persistence'] = True
            assert prefs([True, True]) == [True, True]
            assert has(query('Lune bookmark probe'), bookmark_url)
            assert has(query(history_query), history_url)
            report['checks']['reenabled_providers'] = True
            request('DELETE', session)
            session = None
            report.pop('last_response', None)
            report.pop('history_navigation', None)
            report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        if session:
            try:
                report['diagnostics'] = request('POST', session + '/execute/sync', {
                    'script': 'return {url:location.href,title:document.title,body:document.body.innerText.slice(0,600)};',
                    'args': []})
            except Exception:
                pass
        raise
    finally:
        if session:
            try:
                request('DELETE', session)
            except Exception:
                pass
        if process:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        server.shutdown()
        server.server_close()
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', type=Path, required=True)
    parser.add_argument('--driver', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    check(args.app.resolve(), args.driver.resolve(), args.report.resolve())
