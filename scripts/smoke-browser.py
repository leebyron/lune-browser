#!/usr/bin/env python3
"""Smoke-test the built app via its matching ChromeDriver and an isolated profile.

Only loopback and internal pages are loaded. This is not signing, Gatekeeper, or update testing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import socket
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
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


def check_ui(request, path, internal_icons=False):
    """Exercise packaged WebUI and registered defaults in the temporary profile."""
    expected = {
        'helium.browser.layout': 2,
        'helium.browser.vertical_right_aligned': True,
        'helium.browser.vertical_address_bar_in_sidebar': True,
        'helium.browser.zen_mode': True,
        'helium.browser.zen_mode_sidebar_pinned': True,
        'helium.browser.zen_mode_top_chrome_pinned': False,
        'helium.browser.ui_density': 0,
        'helium.browser.rounded_frame_thickness': 4,
        'helium.browser.centered_location_bar': True,
        'helium.browser.show_avatar_button': False,
        'helium.browser.mru_tab_cycling': True,
        'helium.browser.visual_tab_switcher': True,
        'helium.browser.vertical_pinned_tabs_per_row': 4,
        'helium.command_bar.enabled': True,
        'helium.link_peek.enabled': False,
        'vertical_tabs.expand_on_hover': True,
    }

    def js(script, asynchronous=False, args=None):
        return request('POST', path + '/execute/' + ('async' if asynchronous else 'sync'),
                       {'script': script, 'args': args or []})

    def wait_for(script):
        for _ in range(60):
            result = js(script)
            if result:
                return result
            time.sleep(0.5)
        diagnostic = js('''return {url: location.href, title: document.title,
            body: document.body?.innerText.slice(0, 2000),
            chromeKeys: Object.keys(window.chrome || {})};''')
        raise RuntimeError('Packaged WebUI did not reach the expected state: '
                           + script + '\n' + json.dumps(diagnostic))

    icons = {}

    def check_icon(name, selector):
        result = js('''
            const selector = arguments[0], done = arguments[arguments.length - 1];
            const find = root => {
              const own = root.querySelector(selector);
              if (own) return own;
              for (const element of root.querySelectorAll('*')) {
                if (element.shadowRoot) {
                  const found = find(element.shadowRoot); if (found) return found;
                }
              }
            };
            const element = find(document);
            if (!element) { done({error: 'Missing image: ' + selector}); return; }
            const image = new Image();
            image.crossOrigin = 'anonymous';
            image.onerror = () => done({error: 'Could not load ' + image.src});
            image.onload = () => {
              try {
                const canvas = document.createElement('canvas');
                canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
                const ctx = canvas.getContext('2d'); ctx.drawImage(image, 0, 0);
                const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                const colors = {'16,53,79': 0, '0,167,190': 0, '83,134,191': 0};
                for (let i = 0; i < pixels.length; i += 4) {
                  const key = [pixels[i], pixels[i+1], pixels[i+2]].join(',');
                  if (pixels[i+3] === 255 && key in colors) colors[key]++;
                }
                done({src: image.src, width: canvas.width, height: canvas.height, colors});
              } catch (error) { done({error: String(error)}); }
            };
            image.src = element.currentSrc || element.src;
        ''', True, [selector])
        if result.get('error') or not all(result.get('colors', {}).values()) or not result.get('colors'):
            raise RuntimeError(f'{name} does not contain the Pelagic Signal Lune artwork: {result}')
        icons[name] = result

    # WebDriver navigation bypasses the omnibox's helium:// alias fixup.
    request('POST', path + '/url', {'url': 'chrome://settings/help'})
    wait_for('return !!window.chrome?.settingsPrivate;')
    prefs = js('''
        const keys = arguments[0], done = arguments[arguments.length - 1];
        Promise.all(keys.map(key => new Promise(resolve => {
          chrome.settingsPrivate.getPref(key, pref => resolve([key, pref?.value]));
        }))).then(entries => done(Object.fromEntries(entries)));
    ''', True, [list(expected)])
    if prefs != expected:
        raise RuntimeError(f'Fresh-profile defaults differ: expected {expected}, got {prefs}')
    # Width and collapsed state are not exposed through settingsPrivate.
    for key, value in {'vertical_tabs.uncollapsed_width': 200,
                       'vertical_tabs.collapsed_state': False}.items():
        request('POST', path + '/url', {'url': 'chrome://prefs-internals/' + key})
        actual = json.loads(js('return document.body.innerText;'))
        if actual != value:
            raise RuntimeError(f'Fresh-profile {key}: expected {value}, got {actual}')
        prefs[key] = actual
    request('POST', path + '/url', {'url': 'chrome://settings/help'})
    wait_for('return !!window.chrome?.settingsPrivate;')
    # Navigation past the services page records consent. Disable services first,
    # only in this disposable profile, so the test cannot opt into remote services.
    disabled = js('''
        const done = arguments[arguments.length - 1];
        chrome.settingsPrivate.setPref('helium.services.enabled', false, '', done);
    ''', True)
    if disabled is not True:
        raise RuntimeError('Could not disable services in the temporary test profile.')
    credit_script = '''
        const find = root => {
          const own = root.querySelector('#upstream-credit');
          if (own) return {text: own.textContent.trim(), href: own.querySelector('a')?.href};
          for (const element of root.querySelectorAll('*')) {
            if (element.shadowRoot) { const result = find(element.shadowRoot); if (result) return result; }
          }
          return null;
        };
        return find(document);
    '''
    about = wait_for(credit_script)
    if internal_icons:
        check_icon('about', '#productLogo')
    request('POST', path + '/url', {'url': 'chrome://setup/'})
    onboarding = wait_for(credit_script)
    for name, credit in [('About', about), ('onboarding', onboarding)]:
        if ('Built on Helium, with thanks to its authors and contributors.' not in credit['text']
                or credit['href'] != 'https://helium.computer/'):
            raise RuntimeError(f'{name} attribution is incorrect: {credit}')
    wait_for('return !!document.querySelector("#welcome-page:not([inert])");')
    if internal_icons:
        check_icon('welcome', '#welcome-logo img')
    js('document.querySelector("#welcome-buttons button:last-child").click();')
    wait_for('return !!document.querySelector("#services-page.visible");')
    if internal_icons:
        check_icon('services', '#services-page .header-icon img')
    js('document.querySelector("#setup-buttons button:last-child").click();')
    engines = wait_for('''
        const cards = [...document.querySelectorAll('#search-engines-page button')];
        return cards.length ? cards.map(card => ({
          name: [...(card.querySelector('.engine-name')?.childNodes || [])]
            .filter(node => node.nodeType === Node.TEXT_NODE)
            .map(node => node.textContent).join('').trim(),
          text: card.textContent.trim(), selected: card.getAttribute('aria-pressed')
        })) : null;
    ''')
    if (engines[0]['name'] != 'Kagi' or 'Suggested for Lune.' not in engines[0]['text']
            or 'paid subscription after the trial' not in engines[0]['text']
            or not any(engine['name'] == 'DuckDuckGo' for engine in engines)):
        raise RuntimeError(f'Packaged search recommendations are incorrect: {engines}')
    return {'defaults': prefs, 'about_credit': about, 'onboarding_credit': onboarding,
            'search_engines': engines, 'internal_icons': icons, 'native_controls_tested': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_output', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--ui', action='store_true', help='Verify packaged UI strings and new-profile defaults.')
    parser.add_argument('--headed', action='store_true', help='Show the isolated browser window.')
    parser.add_argument('--internal-icons', action='store_true',
                        help='Require complete Lune branding, including packaged WebUI and helper icons.')
    parser.add_argument('--arch', choices=('arm64', 'x86_64'), default='arm64',
                        help='Expected app architecture.')
    parser.add_argument('--chromium-version',
                        help='Expected Chromium version; defaults to the current build lock.')
    args = parser.parse_args()
    if args.internal_icons and not args.ui:
        parser.error('--internal-icons requires --ui')
    root = Path(__file__).resolve().parents[1]
    lock = json.loads((root / 'manifests/browser.lock.json').read_text())
    expected_version = args.chromium_version or lock['chromium_version']
    output = args.build_output.resolve()
    app = output / 'Lune.app'
    with (app / 'Contents/Info.plist').open('rb') as f:
        info = plistlib.load(f)
    if info['CFBundleIdentifier'] != 'computer.lune.browser':
        raise RuntimeError('Unexpected bundle identity.')
    binary = app / 'Contents/MacOS' / info['CFBundleExecutable']
    architecture = subprocess.check_output(['/usr/bin/lipo', '-archs', binary], text=True).strip()
    if architecture != args.arch:
        raise RuntimeError(f'Expected {args.arch} app, got {architecture}.')
    driver = output / 'chromedriver'
    version = subprocess.check_output([driver, '--version'], text=True).strip()
    if not version.startswith(f'ChromeDriver {expected_version} '):
        raise RuntimeError(f'Expected Chromium {expected_version} driver, got {version}.')
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
        try:
            with opener.open(req, timeout=60) as response:
                value = json.load(response)['value']
        except HTTPError as error:
            raise RuntimeError(error.read().decode('utf-8', errors='replace')) from error
        if isinstance(value, dict) and 'error' in value:
            raise RuntimeError(value)
        return value

    report = {'bundle_id': info['CFBundleIdentifier'], 'architecture': architecture,
              'test_host_architecture': platform.machine(),
              'chromium_version': expected_version,
              'driver_version': version, 'app_version': info['CFBundleShortVersionString'],
              'checks': [], 'mode': 'headed' if args.headed else 'headless', 'release_validated': False}
    if args.ui:
        component = lock['components']['macos']['commit']
        expected_icon = subprocess.check_output(['git', 'show', component + ':resources/assets/app.icns'], cwd=root)
        actual_icon = (app / 'Contents/Resources/app.icns').read_bytes()
        if actual_icon != expected_icon or 'CFBundleIconName' in info:
            raise RuntimeError('App icon does not match the pinned Lune artwork or is overridden by an asset catalog.')
        report['icon_sha256'] = hashlib.sha256(actual_icon).hexdigest()
        if args.internal_icons:
            catalogs = list(app.rglob('Assets.car'))
            if catalogs:
                raise RuntimeError(f'Unexpected icon catalogs in Lune bundle: {catalogs}')
            report['icon_bundles'] = []
            for plist in app.rglob('Info.plist'):
                bundle_info = plistlib.loads(plist.read_bytes())
                if 'CFBundleIconName' in bundle_info:
                    raise RuntimeError(f'Asset catalog overrides Lune icon: {plist}')
                if bundle_info.get('CFBundleIconFile') == 'app.icns':
                    if (plist.parent / 'Resources/app.icns').read_bytes() != expected_icon:
                        raise RuntimeError(f'Helper icon differs from Lune: {plist}')
                    report['icon_bundles'].append(str(plist.relative_to(app)))
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
                            *([] if args.headed else ['--headless=new']),
                            '--no-first-run', '--no-default-browser-check',
                            '--disable-background-networking',
                            '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',
                            f'--user-data-dir={profile}']}}}})
                    session = created['sessionId']
                    path = '/session/' + session
                    actual_version = created['capabilities'].get('browserVersion')
                    if actual_version != expected_version:
                        raise RuntimeError(f'Expected Chromium {expected_version} browser, got {actual_version}.')
                    request('POST', path + '/url', {'url': f'http://127.0.0.1:{server.server_port}/{phase}'})
                    title = request('GET', path + '/title')
                    result = request('POST', path + '/execute/sync', {
                        'script': "return {runtime:document.body.dataset.runtime,stored:localStorage.getItem('lune-smoke')};", 'args': []})
                    if title != 'Lune build smoke' or result != {'runtime': 'ok', 'stored': 'persisted'}:
                        raise RuntimeError(f'Browser smoke failed in {phase}: {title!r}, {result!r}')
                    report['checks'].append({'phase': phase, 'title': title, **result})
                    if args.ui and phase == 'write':
                        report['ui'] = check_ui(request, path, args.internal_icons)
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
    except Exception as error:
        report.update(passed=False, error=str(error))
        args.report.write_text(json.dumps(report, indent=2) + '\n')
        raise
    finally:
        server.shutdown()
        server.server_close()
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
