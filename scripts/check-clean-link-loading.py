#!/usr/bin/env python3
"""Check navigation and URL copy in an isolated Lune profile."""

import argparse
from contextlib import suppress
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, ProxyHandler, build_opener

from browser_test_profiles import temporary_profile


FIND_CONTROL = """
    const find = (selector, root = document) => {
      const match = root.querySelector(selector);
      if (match) return match;
      for (const element of root.querySelectorAll('*')) {
        if (element.shadowRoot) {
          const nested = find(selector, element.shadowRoot);
          if (nested) return nested;
        }
      }
      return null;
    };
"""


def check_cold_external_url(output, profile, origin, seen, with_ublock):
    default = Path(profile) / 'Default'
    default.mkdir()
    (default / 'Preferences').write_text(json.dumps({'helium': {
        'completed_onboarding': True,
        'services': {'user_consented': False, 'ublock_assets': False},
        'ublock': {'install_allowed': with_ublock, 'enabled': with_ublock},
    }}))
    app = output / 'Lune.app'
    profile_arg = f'--user-data-dir={profile}'
    route = '/cold'
    target = route + '?keep=1&fbclid=cold'
    isolation = ('--disable-features=HeliumTrackingQueryCleanup' if with_ublock
                 else '--disable-extensions')

    def launched_browser_pids():
        commands = subprocess.check_output(['ps', '-axo', 'pid=,command='], text=True)
        browser = f'{app}/Contents/MacOS/Lune'
        return [int(line.split(maxsplit=1)[0]) for line in commands.splitlines()
                if browser + ' ' in line and profile_arg in line]

    try:
        subprocess.run(['/usr/bin/open', '-g', '-n', '-a', app, origin + target,
                        '--args', '--headless=new', '--no-first-run',
                        '--no-default-browser-check', '--disable-background-networking',
                        '--use-mock-keychain', '--password-store=basic', '--no-proxy-server',
                        '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1',
                        f'--custom-update-server-url={origin}/no-update.xml',
                        profile_arg, isolation], check=True)
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            actual = next((row[1] for row in seen if urlsplit(row[1]).path == route), None)
            if actual:
                expected = target if with_ublock else route + '?keep=1'
                assert actual == expected, (actual, expected)
                return {
                    'passed': True,
                    'mode': 'uBlock only' if with_ublock else 'Lune only',
                    'first_request': actual,
                }
            time.sleep(0.15)
        raise AssertionError('Cold external URL never reached the fixture')
    finally:
        for pid in launched_browser_pids():
            with suppress(ProcessLookupError):
                os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + 6
        while launched_browser_pids() and time.monotonic() < deadline:
            time.sleep(0.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--disabled', action='store_true')
    parser.add_argument('--clipboard', action='store_true')
    parser.add_argument('--privacy-controls', action='store_true',
                        help='Exercise the tracking settings page and domain exclusions.')
    parser.add_argument('--with-ublock', action='store_true')
    parser.add_argument('--request-coverage', action='store_true',
                        help='Compare destination and referrer cleanup in isolation.')
    parser.add_argument('--cold-external', action='store_true',
                        help='Use Launch Services on native hardware to check a cold external URL.')
    parser.add_argument('--refresh-rules', type=Path,
                        help='Serve a saved Helium tracking list through an isolated loopback mirror.')
    parser.add_argument('--setup-consent', choices=('next', 'defaults'),
                        help='Grant filter-list consent through a fresh profile’s Setup UI.')
    args = parser.parse_args()
    if args.setup_consent and not args.refresh_rules:
        parser.error('--setup-consent requires --refresh-rules')
    if args.request_coverage and (args.refresh_rules or args.with_ublock != args.disabled):
        parser.error('Use --request-coverage alone or with --with-ublock --disabled')
    if args.cold_external and not args.request_coverage:
        parser.error('--cold-external requires --request-coverage')
    output = args.output.resolve()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    seen = []
    update_headers = []
    rules = args.refresh_rules.read_bytes() if args.refresh_rules else b''
    list_route = '/ubo/adguard-spyware-url/fixture/v1/privacy-removeparam.txt'
    generation = {'parameter': 'lune_fixture_alpha', 'unsupported': None, 'source': None,
                  'offline': False}

    class Fixture(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            self.do_GET()

        def do_GET(self):
            seen.append((self.command, self.path, self.headers.get('Referer'),
                         self.headers.get('Sec-Purpose')))
            route = urlsplit(self.path).path
            if route.startswith('/ubo/'):
                update_headers.append((route, self.headers.get('Cookie'),
                                       self.headers.get('Authorization'),
                                       self.headers.get('Referer')))
                if generation['offline']:
                    self.send_response(503)
                    self.end_headers()
                    return
            if route == '/ubo/assets.json':
                origin = f'http://127.0.0.1:{self.server.server_port}'
                source = generation['source'] or origin + list_route
                catalog = {'adguard-spyware-url': {'contentURL': source}}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                with suppress(BrokenPipeError, ConnectionResetError):
                    self.wfile.write(json.dumps(catalog).encode())
                return
            if route == list_route:
                content = rules + b'\n$removeparam=' + generation['parameter'].encode() + b'\n'
                if generation['unsupported']:
                    content += generation['unsupported'].encode() + b'\n'
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                with suppress(BrokenPipeError, ConnectionResetError):
                    self.wfile.write(content)
                return
            if route == '/worker/script.js':
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(b"""
                    self.addEventListener('activate', event => {
                      event.waitUntil(clients.claim());
                    });
                    self.addEventListener('fetch', event => {
                      const url = new URL(event.request.url);
                      if (url.pathname === '/worker/synthetic') {
                        event.respondWith(new Response(url.href));
                      } else if (url.pathname === '/worker/forward') {
                        event.respondWith(fetch(event.request).then(() => new Response(url.href)));
                      }
                    });
                """)
                return
            if route == '/worker-redirect':
                self.send_response(302)
                self.send_header('Location', '/worker/forward?keep=2&fbclid=redirect')
                self.end_headers()
                return
            if self.path.startswith('/redirect?'):
                self.send_response(302)
                self.send_header('Location',
                                 f'http://localhost:{self.server.server_port}'
                                 '/hop?fbclid=hop&q=%2f%2B+%20')
                self.end_headers()
                return
            if self.path.startswith('/hop?'):
                self.send_response(302)
                self.send_header('Location',
                                 '/landing?gclid=final&q=%2f%2B+%20#details')
                self.end_headers()
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(b'<!doctype html><title>Lune clean links</title>')

    opener = build_opener(ProxyHandler({}))
    with socket.socket() as port_socket:
        port_socket.bind(('127.0.0.1', 0))
        port = port_socket.getsockname()[1]

    def request(method, path, data=None, timeout=30):
        req = Request(f'http://127.0.0.1:{port}{path}', method=method,
                      data=json.dumps(data).encode() if data is not None else None,
                      headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=timeout) as response:
            return json.load(response)['value']

    with ThreadingHTTPServer(('127.0.0.1', 0), Fixture) as server, \
            temporary_profile(prefix='lune-clean-links-') as profile, \
            args.report.with_suffix('.driver.log').open('w') as log:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f'http://127.0.0.1:{server.server_port}'
        redirect_origin = f'http://localhost:{server.server_port}'
        if args.cold_external:
            try:
                report = check_cold_external_url(output, profile, origin, seen, args.with_ublock)
                args.report.write_text(json.dumps(report, indent=2) + '\n')
            finally:
                server.shutdown()
            return
        env = {key: os.environ[key] for key in
               ('HOME', 'USER', 'LOGNAME', 'PATH', 'TMPDIR', 'LC_ALL', 'DEVELOPER_DIR')
               if key in os.environ}
        process = subprocess.Popen([output / 'chromedriver', f'--port={port}',
                                    '--allowed-ips=127.0.0.1'],
                                   stdout=log, stderr=subprocess.STDOUT, env=env)
        session = None
        try:
            for _ in range(60):
                if process.poll() is not None:
                    raise RuntimeError('ChromeDriver exited')
                try:
                    if request('GET', '/status', timeout=2).get('ready'):
                        break
                except URLError:
                    pass
                time.sleep(0.5)
            else:
                raise RuntimeError('ChromeDriver did not become ready')

            options = [
                '--headless=new', '--no-first-run', '--no-default-browser-check',
                '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',
                f'--custom-update-server-url={origin}/no-update.xml',
                f'--user-data-dir={profile}',
            ]
            prefs = {'net.network_prediction_options': 0}
            if args.with_ublock and not args.refresh_rules:
                prefs.update({'helium.ublock.install_allowed': True,
                              'helium.ublock.enabled': True,
                              'helium.services.ublock_assets': False})
            else:
                options.append('--disable-extensions')
            if args.refresh_rules:
                prefs['helium.services.origin_override'] = origin
                if args.setup_consent:
                    options.append('--window-size=1100,800')
                else:
                    prefs.update({
                        'helium.completed_onboarding': True,
                        'helium.services.enabled': True,
                        'helium.services.user_consented': False,
                        'helium.services.ublock_assets': False,
                        'helium.services.bangs': False,
                        'helium.services.spellcheck_files': False,
                        'helium.services.ext_proxy': False,
                    })
            if args.disabled:
                options.append('--disable-features=HeliumTrackingQueryCleanup')

            def start_browser(initial_prefs):
                settings = {
                    'binary': str(output / 'Lune.app/Contents/MacOS/Lune'),
                    'args': options,
                    'excludeSwitches': (['disable-background-networking']
                                        if args.refresh_rules else []),
                }
                if initial_prefs is not None:
                    settings['prefs'] = initial_prefs
                capabilities = {'goog:chromeOptions': settings}
                if args.refresh_rules and args.setup_consent != 'defaults':
                    settings['perfLoggingPrefs'] = {'traceCategories': 'mojom'}
                    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
                return request('POST', '/session', {'capabilities': {'alwaysMatch': capabilities}},
                               timeout=120)

            created = start_browser(prefs)
            session = '/session/' + created['sessionId']

            def navigate(url):
                request('POST', session + '/url', {'url': url}, timeout=65)
                return request('GET', session + '/url')

            def execute(script, *script_args):
                return request('POST', session + '/execute/sync',
                               {'script': script, 'args': script_args})

            def cdp(command, parameters):
                return request('POST', session + '/goog/cdp/execute',
                               {'cmd': command, 'params': parameters})

            def read_clipboard():
                return request('POST', session + '/execute/async', {
                    'script': """const done = arguments[0];
                    navigator.clipboard.readText().then(done, error => done(String(error)));""",
                    'args': [],
                })

            def copy_current_url(current, expected):
                visible_url = request('GET', session + '/url')
                assert visible_url == redirect_origin + current, visible_url
                for key_type in ('rawKeyDown', 'keyUp'):
                    cdp('Input.dispatchKeyEvent', {
                        'type': key_type, 'modifiers': 12, 'key': 'C',
                        'code': 'KeyC', 'windowsVirtualKeyCode': 67,
                        'nativeVirtualKeyCode': 8,
                    })
                copied = read_clipboard()
                assert copied == redirect_origin + expected, (copied, expected)
                assert request('GET', session + '/url') == redirect_origin + current
                return copied

            def wait_for(predicate, reason, timeout=None):
                deadline = time.monotonic() + (timeout or (30 if args.refresh_rules else 12))
                while time.monotonic() < deadline:
                    if predicate():
                        return
                    time.sleep(0.2)
                raise AssertionError(reason)

            def get_pref(name):
                return request('POST', session + '/execute/async', {
                    'script': """const done = arguments[1];
                        chrome.settingsPrivate.getPref(arguments[0], pref => done(pref.value));""",
                    'args': [name],
                })

            if args.privacy_controls:
                bundled_target = origin + '/bundled-fallback?item=1'
                assert navigate(bundled_target + '&pjclid=fixture') == bundled_target
                navigate('chrome://settings/privacy')
                wait_for(lambda: execute(FIND_CONTROL + """
                    const row = find('#trackingParametersLinkRow');
                    return row && getComputedStyle(row, '::before').maskImage.startsWith('url');
                """), 'Tracking parameters row or icon was missing')
                execute(FIND_CONTROL + "find('#trackingParametersLinkRow').click();")
                wait_for(lambda: execute(FIND_CONTROL + """
                    const toggle = find('#cleanTrackingLinksToggle');
                    return toggle?.pref?.value === true && toggle.getBoundingClientRect().height > 0;
                """), 'Tracking parameters subpage did not show its enabled toggle')
                assert request('GET', session + '/url').endswith('/privacy/tracking-parameters')
                typography = execute(FIND_CONTROL + """
                    const heading = find('.excluded-domains-heading');
                    const label = find('#cleanTrackingLinksToggle').shadowRoot
                        .querySelector('#labelWrapper > .label');
                    const typography = element => {
                      const style = getComputedStyle(element);
                      return [style.fontSize, style.fontWeight, style.color];
                    };
                    return [typography(heading), typography(label)];
                """)
                assert typography[0] == typography[1], typography
                execute(FIND_CONTROL + "find('#cleanTrackingLinksToggle').click();")
                wait_for(lambda: get_pref('helium.clean_tracking_links') is False,
                         'Tracking cleanup toggle did not turn off')
                original = '/privacy-toggle?item=1&fbclid=tracking'
                assert navigate(redirect_origin + original) == redirect_origin + original
                settings = 'chrome://settings/privacy/tracking-parameters'
                navigate(settings)
                wait_for(lambda: execute(FIND_CONTROL +
                    "return find('#cleanTrackingLinksToggle')?.pref?.value === false;"),
                    'Tracking cleanup opt-out was lost on reopening the settings page')
                execute(FIND_CONTROL + "find('#cleanTrackingLinksToggle').click();")
                wait_for(lambda: get_pref('helium.clean_tracking_links') is True,
                         'Tracking cleanup toggle did not turn on')

                excluded_pref = 'helium.tracking_query_excluded_domains'
                def add_domain(domain):
                    execute(FIND_CONTROL + "find('#excludedDomainInput').value = arguments[0];",
                            domain)
                    wait_for(lambda: execute(FIND_CONTROL +
                        "return !find('#addExcludedDomain')?.disabled;"), 'Add button stayed disabled')
                    execute(FIND_CONTROL + "find('#addExcludedDomain').click();")

                add_domain('https://localhost/path')
                wait_for(lambda: execute(FIND_CONTROL +
                    "return find('#excludedDomainInput')?.invalid === true;"),
                    'Invalid domain input did not show an error')
                assert get_pref(excluded_pref) == []
                add_domain('LOCALHOST.')
                wait_for(lambda: get_pref(excluded_pref) == ['localhost'],
                         'Domain was not normalized and saved')
                assert navigate(redirect_origin + original) == redirect_origin + original
                assert navigate(origin + original) == origin + '/privacy-toggle?item=1'
                navigate(redirect_origin + original)
                cdp('Browser.grantPermissions', {'origin': redirect_origin, 'permissions': [
                    'clipboardReadWrite', 'clipboardSanitizedWrite']})
                assert copy_current_url(original, original) == redirect_origin + original
                execute("fetch('/excluded-referrer');")
                wait_for(lambda: any(path == '/excluded-referrer' and
                                     referrer == redirect_origin + original
                                     for _, path, referrer, _ in seen),
                         'Excluded domain did not keep the tracking parameter in the referrer')
                request('DELETE', session)
                session = None
                created = start_browser(None)
                session = '/session/' + created['sessionId']
                assert navigate(redirect_origin + original) == redirect_origin + original
                navigate(settings)
                wait_for(lambda: execute(FIND_CONTROL +
                    "return !!find('.remove-excluded-domain');"), 'Saved domain was not visible')
                execute(FIND_CONTROL + "find('.remove-excluded-domain').click();")
                wait_for(lambda: get_pref(excluded_pref) == [], 'Removed domain remained in prefs')
                assert navigate(redirect_origin + original) == redirect_origin + '/privacy-toggle?item=1'
                args.report.write_text(json.dumps({'passed': True, 'requests': seen}, indent=2) + '\n')
                return

            if args.refresh_rules:
                def set_pref(name, value):
                    navigate('chrome://settings/privacy')
                    assert request('POST', session + '/execute/async', {
                        'script': """const done = arguments[2];
                        chrome.settingsPrivate.setPref(arguments[0], arguments[1], '', done);""",
                        'args': [name, value],
                    }) is True, name

                observed = []
                context_updates = {}

                def capture(parameter, cleaned):
                    navigate(redirect_origin + '/native-copy')
                    cdp('Browser.grantPermissions', {
                        'origin': redirect_origin,
                        'permissions': ['clipboardReadWrite', 'clipboardSanitizedWrite'],
                    })
                    state = f'/native-copy?keep=1&fbclid=local&{parameter}=downloaded'
                    expected = ('/native-copy?keep=1' if cleaned else
                                f'/native-copy?keep=1&{parameter}=downloaded')
                    execute("history.replaceState(null, '', arguments[0]);", state)
                    try:
                        copied = copy_current_url(state, expected)
                    except AssertionError as error:
                        print(f'Clipboard state for {parameter}: {error}', flush=True)
                        return False
                    observed.append([parameter, cleaned, copied])
                    return True

                def request_count():
                    return sum(urlsplit(path).path == list_route for _, path, _, _ in seen)

                def report_refresh():
                    args.report.write_text(json.dumps({
                        'passed': True, 'browser': created['capabilities']['browserVersion'],
                        'asset_requests': request_count(), 'clipboard': observed, 'requests': seen,
                        'setup_consent': args.setup_consent, 'update_headers': update_headers,
                        'context_updates': context_updates,
                    }, indent=2) + '\n')

                def count_context_updates():
                    method = b'network::mojom::NetworkContext::SetTrackingQueryCleanup'
                    # The generated Mojo bindings include this stable method
                    # hash even in builds that omit the readable method name.
                    method_hash = int.from_bytes(sha256(method).digest()[:4], 'big')
                    events = request('POST', session + '/log', {'type': 'performance'})
                    traces = (json.loads(event['message'])['message']['params']
                              for event in events)
                    return sum(trace.get('args', {}).get('chrome_mojo_event_info', {}).get(
                               'ipc_hash') == method_hash for trace in traces)

                def checked_at():
                    navigate('chrome://prefs-internals/helium.tracking_query_asset')
                    return json.loads(execute('return document.body.textContent'))['checked']

                def refresh():
                    set_pref('helium.services.ublock_assets', False)
                    set_pref('helium.services.ublock_assets', True)

                navigate(origin + '/update-cookie')
                execute("document.cookie = 'fixture_cookie=browser_only; path=/';")
                assert 'fixture_cookie' in execute('return document.cookie')

                if args.setup_consent:
                    navigate('chrome://setup/')

                    def setup_element(selector):
                        return execute('return !!document.querySelector(arguments[0])',
                                       selector)

                    def setup_click(selector):
                        wait_for(lambda: setup_element(selector), f'Setup missing {selector}')
                        execute('document.querySelector(arguments[0]).click()', selector)

                    wait_for(lambda: setup_element('.welcome-actions .primary'),
                             'Setup did not load')
                    assert all(not path.startswith('/ubo/') for _, path, _, _ in seen), seen
                    if args.setup_consent == 'defaults':
                        setup_click('.welcome-actions .ghost')
                        wait_for(lambda: 'setup' not in request('GET', session + '/url'),
                                 'Use Defaults did not finish Setup')
                        navigate('chrome://settings/privacy')
                        assert get_pref('helium.global_privacy_control') is True
                        assert get_pref('enable_do_not_track') is True
                    else:
                        setup_click('.welcome-actions .primary')
                        wait_for(lambda: setup_element('#search-engines-page.visible'),
                                 'Search engine step did not load')
                        setup_click('#setup-buttons button:last-child')
                        wait_for(lambda: setup_element('#privacy-page.visible'),
                                 'Privacy step did not load before Services')

                        def wait_checked(pref, checked):
                            wait_for(lambda: execute("""
                                return document.getElementById(arguments[0] + '-toggle').checked
                                    === arguments[1];
                            """, pref, checked), f'{pref} did not become {checked}')

                        def click_description(pref):
                            selector = f'[id="{pref}-description"]'
                            element = request('POST', session + '/element',
                                              {'using': 'css selector', 'value': selector})
                            try:
                                request('POST', session + '/element/' +
                                        next(iter(element.values())) + '/click', {})
                            except HTTPError as error:
                                message = json.load(error)['value']['message']
                                raise AssertionError(f'Could not click {selector}: {message}') from error

                        privacy_prefs = ('ublock.enabled', 'clean_tracking_links', 'noise.enabled',
                                         'global_privacy_control', 'enable_do_not_track')
                        for pref in privacy_prefs:
                            wait_checked(pref, True)
                        assert execute("""
                            return document.getElementById('clean_tracking_links-description')
                                .textContent.includes('pre-bundled filter list');
                        """)
                        assert execute("""
                            const description = document.getElementById('global_privacy_control-description');
                            return description.textContent.trim() ===
                                'Send a Global Privacy Control signal to limit the sale or sharing of your data.' &&
                                description.previousElementSibling.textContent.trim() ===
                                    'Opt out of websites sharing your information';
                        """)
                        for pref in privacy_prefs:
                            click_description(pref)
                            wait_checked(pref, False)
                            if pref in ('clean_tracking_links', 'noise.enabled'):
                                click_description(pref)
                                wait_checked(pref, True)
                        execute("document.getElementById('global_privacy_control-toggle').focus();")
                        for key_type in ('rawKeyDown', 'keyUp'):
                            cdp('Input.dispatchKeyEvent', {
                                'type': key_type, 'key': ' ', 'code': 'Space',
                                'windowsVirtualKeyCode': 32,
                            })
                        wait_checked('global_privacy_control', True)
                        hit = execute("""
                            const row = document.getElementById('global_privacy_control-toggle')
                                .closest('.compact-preference');
                            row.scrollIntoView({block: 'nearest'});
                            const rect = row.getBoundingClientRect();
                            const x = rect.left + 6;
                            const y = rect.top + rect.height / 2;
                            return {x, y, isPadding: document.elementFromPoint(x, y) === row};
                        """)
                        assert hit.pop('isPadding'), hit
                        for event_type in ('mousePressed', 'mouseReleased'):
                            cdp('Input.dispatchMouseEvent', {
                                **hit, 'type': event_type, 'button': 'left', 'clickCount': 1,
                            })
                        wait_checked('global_privacy_control', False)
                        setup_click('#setup-buttons button:last-child')
                        wait_for(lambda: setup_element('#services-page.visible'),
                                 'Services step did not load')
                        service_prefs = execute("""
                            return [...document.querySelectorAll('#services-page input[role="switch"]')]
                                .map(input => [input.id.replace(/-toggle$/, ''), input.checked]);
                        """)
                        assert len(service_prefs) == 6, service_prefs
                        assert dict(service_prefs)['services.ublock_assets'] is True, service_prefs
                        for pref, initial in service_prefs:
                            click_description(pref)
                            wait_checked(pref, not initial)
                            click_description(pref)
                            wait_checked(pref, initial)
                        assert not setup_element('#services-page input[id="ublock.enabled-toggle"]')
                        assert all(not path.startswith('/ubo/') for _, path, _, _ in seen), seen
                        setup_click('#setup-buttons button:last-child')
                        wait_for(lambda: setup_element('#data-import-page.visible'),
                                 'Import step did not load')
                        navigate('chrome://settings/privacy')
                        assert get_pref('helium.global_privacy_control') is False
                        assert get_pref('enable_do_not_track') is False
                else:
                    assert capture('lune_fixture_alpha', False)
                    assert not update_headers, seen
                    set_pref('helium.services.ublock_assets', True)
                    assert capture('lune_fixture_alpha', False)
                    assert not update_headers, seen
                    set_pref('helium.services.user_consented', True)
                wait_for(lambda: request_count() >= 1,
                         'Lune did not download the list after consent')
                wait_for(lambda: capture('lune_fixture_alpha', True),
                         'The first list did not reach native URL copy')
                if args.setup_consent == 'defaults':
                    # Use Defaults also enables the component extension. The
                    # native copy result proves Lune installed its own rules.
                    report_refresh()
                    return
                context_updates['initial_rules'] = count_context_updates()
                assert context_updates['initial_rules'] > 0, 'Network context update trace missing'

                initial_check = checked_at()
                before = request_count()
                # A new preference value restarts the refresh timer while
                # resolving to the same catalog and keeping the list eligible.
                set_pref('helium.services.origin_override', origin + '/')
                wait_for(lambda: request_count() > before, 'Identical list was not fetched')
                wait_for(lambda: checked_at() != initial_check,
                         'Successful identical refresh did not advance the timestamp')
                context_updates['identical_refresh'] = count_context_updates()
                assert context_updates['identical_refresh'] == 0, context_updates

                generation['parameter'] = 'lune_fixture_beta'
                before = request_count()
                refresh()
                wait_for(lambda: request_count() > before, 'Lune did not refresh the list')
                wait_for(lambda: capture('lune_fixture_beta', True),
                         'The refreshed rules did not reach native URL copy')
                assert capture('lune_fixture_alpha', False)

                execute("history.replaceState(null, '', '/native-copy?lune_fixture_beta=referrer');"
                        "fetch('/refresh-referrer');")
                wait_for(lambda: any(path == '/refresh-referrer' and
                                    referrer == redirect_origin + '/native-copy'
                                    for _, path, referrer, _ in seen),
                         'The refreshed rules did not reach the network service')

                open_with_tracking = '/native-load?keep=1&lune_fixture_beta=track'
                assert navigate(redirect_origin + open_with_tracking) == (
                    redirect_origin + '/native-load?keep=1')
                assert [path for _, path, _, _ in seen if path.startswith('/native-load?')] == [
                    '/native-load?keep=1']
                set_pref('helium.clean_tracking_links', False)
                assert navigate(redirect_origin + open_with_tracking) == (
                    redirect_origin + open_with_tracking)
                generation.update(parameter='lune_fixture_rejected',
                                  unsupported='@@*$removeparam,native_unsupported_fixture_option')
                before = request_count()
                set_pref('helium.clean_tracking_links', True)
                wait_for(lambda: request_count() > before, 'Malformed list never served')
                assert capture('lune_fixture_beta', True)
                assert capture('lune_fixture_rejected', False)

                for origin_override, unsupported in [
                    (origin, '!#include missing-exceptions.txt'),
                    (origin + '/', '$removeparam=|legacy'),
                ]:
                    generation['unsupported'] = unsupported
                    before = request_count()
                    set_pref('helium.services.origin_override', origin_override)
                    wait_for(lambda: request_count() > before,
                             'List containing unsupported syntax was never served')
                    assert capture('lune_fixture_beta', True)
                    assert capture('lune_fixture_rejected', False)

                generation['source'] = redirect_origin + list_route
                before = len(update_headers)
                before_list = request_count()
                refresh()
                wait_for(lambda: len(update_headers) > before, 'Foreign URL catalog never served')
                assert capture('lune_fixture_beta', True)
                assert request_count() == before_list, 'Lune followed a foreign list URL'

                # A fresh validated snapshot is usable on restart before any
                # network request, even when the service is unavailable.
                generation['offline'] = True
                request('DELETE', session)
                session = None
                before = len(update_headers)
                created = start_browser(None)
                session = '/session/' + created['sessionId']
                assert capture('lune_fixture_beta', True)
                assert len(update_headers) == before, 'Fresh cache downloaded again on restart'

                set_pref('helium.services.ublock_assets', False)
                before = len(update_headers)
                wait_for(lambda: capture('lune_fixture_beta', False),
                         'Turning filter updates off did not restore bundled rules')
                assert len(update_headers) == before
                bundled_target = redirect_origin + '/bundled-toggle?keep=1&fbclid=track'
                assert navigate(bundled_target) == redirect_origin + '/bundled-toggle?keep=1'
                count_context_updates()
                set_pref('helium.clean_tracking_links', False)
                assert navigate(bundled_target) == bundled_target
                context_updates['bundled_opt_out'] = count_context_updates()
                assert context_updates['bundled_opt_out'] > 0, context_updates
                navigate(redirect_origin + '/native-copy')
                original = '/native-copy?fbclid=original'
                execute("history.replaceState(null, '', arguments[0]);", original)
                copy_current_url(original, original)
                assert all(not (cookie or auth or referrer)
                           for _, cookie, auth, referrer in update_headers), update_headers
                report_refresh()
                return

            if args.with_ublock:
                navigate('chrome-extension://blockjmkbacgjkknlgpkjjiijinjdanf/dashboard.html')
                wait_for(lambda: execute(
                    'return document.body && !document.body.classList.contains("notReady") '
                    '&& !!document.getElementById("dashboard-nav")'),
                    'Bundled uBlock Origin was not ready to filter')
            if args.request_coverage:
                expected = '/ordinary?keep=1'
                actual = navigate(redirect_origin + expected + '&fbclid=destination')
                direct = [row[1] for row in seen if row[1].startswith('/ordinary?')]
                assert actual == redirect_origin + expected and direct == [expected], seen
                execute("history.pushState(null, '', '/history?keep=1&fbclid=referrer');"
                        "fetch('/referrer-check');")
                wait_for(lambda: any(row[1] == '/referrer-check' for row in seen),
                         'No same-origin follow-up request')
                referrer = next(row[2] for row in seen if row[1] == '/referrer-check')
                expected_referrer = '/history?keep=1'
                if args.with_ublock:
                    expected_referrer += '&fbclid=referrer'
                assert referrer == redirect_origin + expected_referrer, seen
                args.report.write_text(json.dumps({
                    'passed': True,
                    'mode': 'uBlock only' if args.with_ublock else 'Lune only',
                    'destination': direct[0],
                    'followup_referrer': referrer.removeprefix(redirect_origin),
                }, indent=2) + '\n')
                return

            if args.with_ublock:
                signed = '/signed?fbclid=signature-input&X-Amz-Signature=abc'
                expected = '/signed?X-Amz-Signature=abc'
                actual = navigate(origin + signed)
                assert actual == origin + expected, (actual, seen)
                signed_requests = [path for _, path, _, _ in seen if path.startswith('/signed?')]
                assert signed_requests == [expected], signed_requests
                args.report.write_text(json.dumps({
                    'passed': True, 'browser': created['capabilities']['browserVersion'],
                    'cleanup_disabled': args.disabled, 'with_ublock': True,
                    'requests': seen,
                }, indent=2) + '\n')
                return

            for _ in range(5):
                navigate(origin + '/ready')
                if request('GET', session + '/title') == 'Lune clean links':
                    break
                time.sleep(0.5)

            actual = navigate(origin + '/redirect?fbclid=first&utm_source=mail')
            expected = (
                ['/redirect?fbclid=first&utm_source=mail',
                 '/hop?fbclid=hop&q=%2f%2B+%20',
                 '/landing?gclid=final&q=%2f%2B+%20']
                if args.disabled else
                ['/redirect?utm_source=mail', '/hop?q=%2f%2B+%20',
                 '/landing?q=%2f%2B+%20']
            )
            redirect_paths = [path for _, path, _, _ in seen
                              if path.startswith(('/redirect?', '/hop?', '/landing?'))]
            assert redirect_paths == expected, (redirect_paths, expected)
            assert actual == redirect_origin + expected[-1] + '#details', actual

            clipboard = {}
            if args.clipboard:
                cdp('Browser.grantPermissions', {
                    'origin': redirect_origin,
                    'permissions': ['clipboardReadWrite', 'clipboardSanitizedWrite'],
                })
            execute("history.pushState(null, '', '/push?item=7&fbclid=push');")
            assert request('GET', session + '/url').endswith('/push?item=7&fbclid=push')
            if args.clipboard:
                pushed = '/push?item=7&fbclid=push'
                clipboard['pushState'] = copy_current_url(
                    pushed, pushed if args.disabled else '/push?item=7')
            execute("history.replaceState(null, '', '/replace?item=7&fbclid=replace');")
            assert request('GET', session + '/url').endswith('/replace?item=7&fbclid=replace')
            assert not any(path.startswith(('/push?', '/replace?')) for _, path, _, _ in seen)
            if args.clipboard:
                replaced = '/replace?item=7&fbclid=replace&utm_source=mail'
                execute("history.replaceState(null, '', arguments[0]);", replaced)
                clipboard['replaceState'] = copy_current_url(
                    replaced, replaced if args.disabled else '/replace?item=7')
                execute("history.replaceState(null, '', '/replace?item=7&fbclid=replace');")
            execute("fetch('/resource?fbclid=page-request');")
            wait_for(lambda: any(path == '/resource?fbclid=page-request'
                                 for _, path, _, _ in seen),
                     'Expected the page-initiated resource to keep its request target')
            resource = next(entry for entry in seen
                            if entry[1] == '/resource?fbclid=page-request')
            expected_referrer = ('/replace?item=7&fbclid=replace' if args.disabled
                                 else '/replace?item=7')
            assert resource[2] == redirect_origin + expected_referrer, resource

            execute("const a = document.createElement('a'); a.href = arguments[0];"
                    "document.body.append(a); a.click();", '/clicked?item=7&fbclid=ref')
            wait_for(lambda: any(path.startswith('/clicked?') for _, path, _, _ in seen),
                     'No user-visible link navigation')
            clicked = [entry for entry in seen if entry[1].startswith('/clicked?')]
            expected_clicked = (
                [('/clicked?item=7&fbclid=ref', '/replace?item=7&fbclid=replace')]
                if args.disabled else [('/clicked?item=7', '/replace?item=7')]
            )
            assert [(path, referer.removeprefix(redirect_origin))
                    for _, path, referer, _ in clicked] == expected_clicked, clicked
            wait_for(lambda: request('GET', session + '/url') ==
                     redirect_origin + expected_clicked[0][0], 'Cleaned link did not commit')

            original_window = request('GET', session + '/window')
            execute("const a = document.createElement('a'); a.href = arguments[0];"
                    "a.id = 'new-tab'; a.textContent = 'Open link'; a.target = '_blank';"
                    "document.body.append(a);", '/new-tab?item=8&fbclid=new')
            element = request('POST', session + '/element',
                              {'using': 'css selector', 'value': '#new-tab'})
            request('POST', session + '/element/' + next(iter(element.values())) + '/click', {})
            wait_for(lambda: len(request('GET', session + '/window/handles')) == 2,
                     'Link did not open in a second tab')
            new_window = next(handle for handle in request('GET', session + '/window/handles')
                              if handle != original_window)
            request('POST', session + '/window', {'handle': new_window})
            expected_new = '/new-tab?item=8&fbclid=new' if args.disabled else '/new-tab?item=8'
            wait_for(lambda: request('GET', session + '/url') == redirect_origin + expected_new,
                     'New-tab link did not commit the expected URL')
            request('POST', session + '/refresh', {})
            new_tab_requests = [path for _, path, _, _ in seen if path.startswith('/new-tab?')]
            assert new_tab_requests == [expected_new, expected_new], new_tab_requests
            request('DELETE', session + '/window')
            request('POST', session + '/window', {'handle': original_window})

            signed = '/signed?fbclid=signature-input&X-Amz-Signature=abc'
            signed_result = navigate(origin + signed)
            assert signed_result == origin + signed, (signed_result, seen[-6:])
            assert any(path == signed for _, path, _, _ in seen)
            execute("const f = document.createElement('form'); f.action = arguments[0];"
                    "f.method = 'POST'; document.body.append(f); f.submit();",
                    '/form?fbclid=post')
            wait_for(lambda: any(method == 'POST' and path == '/form?fbclid=post'
                                 for method, path, _, _ in seen),
                     'POST query was changed or the form request never arrived')
            navigate(origin + '/ready')
            execute("const f = document.createElement('iframe'); f.src = arguments[0];"
                    "document.body.append(f);", '/frame?fbclid=frame')
            wait_for(lambda: any(path == '/frame?fbclid=frame' for _, path, _, _ in seen),
                     'Frame query was changed or the request never arrived')
            execute("const rule = document.createElement('script');"
                    "rule.type = 'speculationrules';"
                    "rule.textContent = JSON.stringify({prefetch:[{source:'list',"
                    "urls:[arguments[0]],eagerness:'immediate'}]});"
                    "document.head.append(rule);", '/speculative?fbclid=prefetch&q=ok')
            wait_for(lambda: any(path.startswith('/speculative?') for _, path, _, _ in seen),
                     'Speculation Rules prefetch did not reach fixture')
            speculative = [entry for entry in seen if entry[1].startswith('/speculative?')]
            expected_prefetch = '/speculative?fbclid=prefetch&q=ok' if args.disabled else '/speculative?q=ok'
            assert {path for _, path, _, _ in speculative} == {expected_prefetch}, speculative
            assert any('prefetch' in (purpose or '') for _, _, _, purpose in speculative), speculative

            navigate(origin + '/worker/register')
            registered = request('POST', session + '/execute/async', {
                'script': """const done = arguments[0];
                    navigator.serviceWorker.register('/worker/script.js')
                        .then(() => navigator.serviceWorker.ready)
                        .then(() => done(true), error => done(String(error)));""",
                'args': [],
            })
            assert registered is True, registered
            wait_for(lambda: execute('return !!navigator.serviceWorker.controller'),
                     'Service worker did not take control')
            for clean, tracking_id, forwarded, redirected in [
                ('/worker/synthetic?keep=1', 'local', False, False),
                ('/worker/forward?keep=1', 'forward', True, False),
                ('/worker/forward?keep=2', 'redirect', True, True),
            ]:
                original = f'{clean}&fbclid={tracking_id}'
                entry = '/worker-redirect' if redirected else original
                target = original if args.disabled else clean
                before = len(seen)
                committed = navigate(origin + entry)
                assert committed == origin + target, (committed, target)
                worker_url = execute('return document.body.textContent.trim()')
                assert worker_url == committed, worker_url
                forwarded_paths = [path for _, path, _, _ in seen[before:]
                                   if path.startswith('/worker/forward?')]
                assert forwarded_paths == ([target] if forwarded else []), forwarded_paths

            args.report.write_text(json.dumps({
                'passed': True, 'browser': created['capabilities']['browserVersion'],
                'cleanup_disabled': args.disabled, 'requests': seen,
                'page_url_clipboard': clipboard,
                'with_ublock': args.with_ublock,
            }, indent=2) + '\n')
        finally:
            if session:
                try:
                    request('DELETE', session, timeout=5)
                except (URLError, TimeoutError):
                    pass
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            server.shutdown()


if __name__ == '__main__':
    main()
