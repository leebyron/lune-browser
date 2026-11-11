#!/usr/bin/env python3
"""Exercise the packaged suggestion service with loopback fixtures and a disposable profile."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, build_opener, ProxyHandler

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('build', type=Path)
parser.add_argument('evidence', type=Path)
parser.add_argument('--interactive', action='store_true')
parser.add_argument('--app', type=Path, help='Optional distinctly named native preview app')
args = parser.parse_args()
build = args.build.resolve()
out = args.evidence.resolve()
out.mkdir(parents=True, exist_ok=True)
requests = []

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        q = parse_qs(url.query).get('q', [''])[0]
        if url.path.startswith('/suggest'):
            requests.append({'path': url.path, 'q': q})
            if q == 'slow':
                time.sleep(.8)
            if q == 'limited':
                self.send_response(429)
                self.send_header('Retry-After', '60')
                self.end_headers()
                return
            if q == 'malformed':
                body = b'not json'
            elif q == 'empty':
                body = json.dumps([q, []]).encode()
            else:
                body = json.dumps([q, [q + ' related', f'http://127.0.0.1:{server.server_port}/top-hit'],
                    ['', 'Fixture top hit'], [], {'google:suggesttype': ['QUERY', 'NAVIGATION']}]).encode()
            content_type = 'application/json'
        else:
            body = b'<!doctype html><title>Search suggestion fixture</title><h1>Search suggestion fixture</h1>'
            content_type = 'text/html'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
opener = build_opener(ProxyHandler({}))
def wd(method, path, data=None):
    req = Request(f'http://127.0.0.1:{port}{path}', method=method,
                  data=None if data is None else json.dumps(data).encode(),
                  headers={'Content-Type': 'application/json'})
    with opener.open(req, timeout=90) as response:
        value = json.load(response)['value']
    if isinstance(value, dict) and 'error' in value:
        raise RuntimeError(value)
    return value

profile = Path(tempfile.mkdtemp(prefix='lune-search-suggestions-'))
(profile / 'Local State').write_text(json.dumps({'internal_only_uis_enabled': True}))
report = {'passed': False, 'checks': {}, 'requests': requests}
driver_log = (out / 'driver.log').open('w')
process = subprocess.Popen([str(build / 'chromedriver'), f'--port={port}', '--allowed-ips=127.0.0.1'],
                           stdout=driver_log, stderr=subprocess.STDOUT)
session = None
try:
    for _ in range(100):
        try:
            if wd('GET', '/status')['ready']:
                break
        except OSError:
            time.sleep(.1)
    flags = ['--no-first-run', '--no-default-browser-check', '--disable-background-networking',
             '--use-mock-keychain', '--password-store=basic',
             '--custom-update-server-url=http://127.0.0.1:1/', f'--user-data-dir={profile}']
    if not args.interactive:
        flags.append('--headless=new')
    def start(launch_flags):
        return '/session/' + wd('POST', '/session', {'capabilities': {'alwaysMatch': {
        'goog:chromeOptions': {'binary': str((args.app.resolve() if args.app else build / 'Lune.app') / 'Contents/MacOS/Lune'), 'args': launch_flags}}}})['sessionId']
    session = start(flags)
    def nav(url):
        wd('POST', session + '/url', {'url': url})
    def js(script, values=None, asynchronous=False):
        return wd('POST', session + '/execute/' + ('async' if asynchronous else 'sync'),
                  {'script': script, 'args': values or []})
    def wait(script, values=None):
        for _ in range(100):
            value = js(script, values)
            if value:
                return value
            time.sleep(.1)
        raise AssertionError(script)
    def pref(enabled):
        nav('chrome://settings/search')
        wait('return !!chrome.settingsPrivate')
        assert js('const done=arguments[arguments.length-1];chrome.settingsPrivate.setPref("search.suggest_enabled",arguments[0],"",done)',
                  [enabled], True)
    nav('chrome://settings/searchEngines')
    wait('return !!document.querySelector("settings-ui")')
    origin = f'http://127.0.0.1:{server.server_port}'
    for keyword, endpoint in [('fixture-default', '/suggest-default'), ('fixture-scope', '/suggest-scope')]:
        js('chrome.send("searchEngineEditStarted",[null]);chrome.send("searchEngineEditCompleted",Array.from(arguments))',
           [keyword, keyword, origin + '/search?q=%s', origin + endpoint + '?q=%s'])
    engines = js('const done=arguments[arguments.length-1];import("chrome://resources/js/cr.js").then(cr=>cr.sendWithPromise("getSearchEnginesList")).then(done)', asynchronous=True)
    fixture = next(e for e in engines['actives'] + engines['others'] + engines['defaults'] if e['keyword'] == 'fixture-default')
    js('chrome.send("setDefaultSearchEngine",[arguments[0],0,false])', [fixture['id']])
    def query(text, keyword=False):
        nav('chrome://omnibox-internals/')
        wait('return !!document.querySelector("omnibox-input")?.shadowRoot')
        js('''const [q,keyword]=arguments;document.querySelector('omnibox-input').dispatchEvent(
          new CustomEvent('query-inputs-changed',{detail:{inputText:q,resetAutocompleteController:true,
          cursorLock:false,cursorPosition:q.length,zeroSuggest:false,preventInlineAutocomplete:true,
          inKeywordMode:keyword,currentUrl:'',pageClassification:0}}));''', [text, keyword])
        return wait('return document.querySelector("omnibox-output").responsesHistory.flat().find(r=>r.done&&r.inputText===arguments[0])', [text])
    def remote(response):
        return [m for group in response['resultsByProvider'] for m in group['results']
                if m['type'] in ['search-suggest', 'navsuggest', 'search-suggest-entity']]
    pref(False)
    assert not remote(query('disabled')) and not requests
    report['checks']['opt_out_no_requests'] = True
    pref(True)
    result = remote(query('fixture'))
    assert any(m['destinationUrl'] == f'http://127.0.0.1:{server.server_port}/top-hit' for m in result), result
    assert any('fixture+related' in m['destinationUrl'] or 'fixture%20related' in m['destinationUrl'] for m in result), result
    report['checks']['query_and_navigation_parsing'] = True
    before = len(requests)
    assert remote(query('fixture-scope scoped', True))
    assert requests[before:] and all(r['path'] == '/suggest-scope' for r in requests[before:]), requests[before:]
    report['checks']['explicit_scope_only'] = True
    for text in ['empty', 'malformed', 'limited']:
        assert not remote(query(text)), text
    assert sum(r['q'] == 'limited' for r in requests) == 1
    report['checks']['empty_malformed_rate_limit_fallback'] = True
    before = len(requests)
    query('file:///private/secret')
    assert len(requests) == before
    report['checks']['private_url_not_sent'] = True
    if not args.interactive:
        wd('DELETE', session)
        session = start(flags + ['--incognito'])
        before = len(requests)
        assert not remote(query('private-window'))
        assert len(requests) == before
        report['checks']['private_window_no_requests'] = True
    report['passed'] = True
    if args.interactive:
        nav(origin)
        bridge = {'port': port, 'session': session, 'profile': str(profile), 'origin': origin}
        (out / 'interactive.json').write_text(json.dumps(bridge))
        print(json.dumps(bridge), flush=True)
        while not (out / 'stop').exists():
            (out / 'requests.json').write_text(json.dumps(requests, indent=2))
            time.sleep(.5)
finally:
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    if session:
        wd('DELETE', session)
    process.terminate()
    driver_log.close()
    server.shutdown()
print(json.dumps(report, indent=2))
