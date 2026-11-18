#!/usr/bin/env python3
"""Exercise setup service gates and first-install consent in a built Lune browser.

Usage: check-setup-services.py OUTPUT_DIR EVIDENCE_DIR [--extension-fixture DIR]

Uses fresh disposable profiles, a loopback-only ChromeDriver, and blocked external
hostname resolution. The optional fixture directory contains a signed KeePassXC
CRX, its manifest.json and icon.png; its bytes are hashed in the report. Native
extension prompts are intentionally not bypassed: follow the
printed instructions using the UI. No password-manager account or vault is used.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import hashlib
import json
import shutil
import socket
import subprocess
import threading
import time
from browser_test_profiles import new_profile

UBLOCK = 'blockjmkbacgjkknlgpkjjiijinjdanf'
PASSWORD_MANAGER = 'oboonakemofpalcgghocfoadofidjkkk'
HELIUM = ['ext_proxy', 'bangs', 'ublock_assets', 'component_updates']
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
parser.add_argument('evidence', type=Path)
parser.add_argument('--extension-fixture', type=Path)
parser.add_argument('--only', choices=['all', 'configuration', 'extension'], default='all')
args = parser.parse_args()
build = args.output.resolve()
out = args.evidence.resolve()
out.mkdir(parents=True, exist_ok=True)
report = {'suite': args.only, 'binary_sha256': hashlib.sha256((build / 'Lune.app/Contents/MacOS/Lune').read_bytes()).hexdigest(), 'cases': {}}
profiles = []
requests = []
mode = 'success'
server = None
session = None
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
log = (out / 'driver.log').open('w')
driver = subprocess.Popen([str(build / 'chromedriver'), f'--port={port}', '--allowed-ips=127.0.0.1', '--verbose'], stdout=log, stderr=subprocess.STDOUT)


def wd(method, path, data=None):
    req = Request(f'http://127.0.0.1:{port}' + path, method=method,
                  data=None if data is None else json.dumps(data).encode(),
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=180) as response:
            return json.load(response)['value']
    except HTTPError as error:
        raise RuntimeError(error.read().decode()) from error


def js(script, asynchronous=False):
    return wd('POST', session + ('/execute/async' if asynchronous else '/execute/sync'), {'script': script, 'args': []})


def wait(predicate, timeout=20):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = predicate()
        if value:
            return value
        time.sleep(.1)
    raise AssertionError(f'Timed out after {timeout}s')


def wait_js(script, timeout=20):
    return wait(lambda: js(script), timeout)


def rpc(method, *values):
    return js("const done=arguments[arguments.length-1],id='test-'+Math.random(),old=cr.webUIResponse;cr.webUIResponse=(i,ok,value)=>{if(i===id){cr.webUIResponse=old;done({ok,value})}else old(i,ok,value)};chrome.send(" + json.dumps(method) + ',[id,...' + json.dumps(values) + ']);', True)


def prefs():
    result = rpc('getPrefs')
    assert result['ok'], result
    return result['value']


def extensions():
    result = rpc('getExtensions')
    assert result['ok'], result
    return result['value']


def click(selector, trusted=False):
    if trusted:
        element = wd('POST', session + '/element', {'using': 'css selector', 'value': selector})
        element_id = element['element-6066-11e4-a52e-4f735466cecf']
        wd('POST', session + f'/element/{element_id}/click', {})
    else:
        js('document.querySelector(' + json.dumps(selector) + ').click()')


def step(name):
    wait_js('return !!document.querySelector(' + json.dumps('#' + name + '-page.visible') + ')')


def next_step(name):
    click('#setup-buttons button:last-child')
    step(name)


def nav_setup():
    wd('POST', session + '/url', {'url': 'chrome://setup/'})
    wait_js("return !!document.querySelector('.welcome-actions .primary')")
    wait(lambda: 'ublock.enabled' in prefs())


def start(name, profile=None):
    global session, setup_handle, inspector_handle
    if profile is None:
        profile = new_profile('lune-services-' + name + '-')
        profiles.append(profile)
        (profile / 'Default').mkdir(parents=True)
        (profile / 'Default/Preferences').write_text('{}\n')
    result = wd('POST', '/session', {'capabilities': {'alwaysMatch': {
        # Close-warning coverage is performed manually outside ChromeDriver.
        'unhandledPromptBehavior': {'default': 'ignore', 'beforeUnload': 'ignore'},
        'goog:chromeOptions': {'binary': str(build / 'Lune.app/Contents/MacOS/Lune'),
            'excludeSwitches': ['disable-background-networking'], 'args': [
            '--disable-gpu', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows',
            '--use-mock-keychain', '--password-store=basic', '--window-size=1200,900',
            '--log-file=' + str(profile / (name + '-browser.log')),
            '--custom-update-server-url=http://127.0.0.1:1/',
            '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',
            f'--user-data-dir={profile}']}}}})
    session = '/session/' + result['sessionId']
    setup_handle = wd('GET', session + '/window')
    inspector_handle = wd('POST', session + '/window/new', {'type': 'tab'})['handle']
    wd('POST', session + '/window', {'handle': setup_handle})
    nav_setup()
    return profile


def close():
    global session
    if session:
        wd('DELETE', session)
        session = None


def privacy():
    click('.welcome-actions .primary')
    step('search-engines')
    next_step('privacy')


def services():
    privacy()
    next_step('services')


def blocker_absent():
    assert UBLOCK not in extensions(), extensions()
    assert prefs()['ublock.install_allowed'] is False


def set_pref(key, value):
    response = rpc('setPref', key, value)
    assert response['ok'], response


def all_helium_off():
    values = prefs()
    assert not values['services.enabled'], values
    assert all(not values['services.' + key] for key in HELIUM), values
    return {key: value for key, value in values.items() if key.startswith('services.')}


def phase(text):
    (out / 'interactive-state.json').write_text(json.dumps({'phase': text, 'port': port, 'session': session, 'setup_handle': setup_handle}, indent=2) + '\n')
    print(text, flush=True)


def passed(name, data=True):
    report['cases'][name] = data
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS:', name, flush=True)


def varint(number):
    result = bytearray()
    while number > 127:
        result.append((number & 127) | 128)
        number >>= 7
    result.append(number)
    return bytes(result)


def field(number, value):
    data = value.encode()
    return varint(number * 8 + 2) + varint(len(data)) + data


try:
    def driver_ready():
        try:
            return wd('GET', '/status')['ready']
        except (OSError, URLError):
            return False

    wait(driver_ready)
    if args.only in ('all', 'configuration'):
        profile = start('pending')
        blocker_absent()
        privacy()
        assert js('return document.getElementById("ublock.enabled-toggle").checked')
        blocker_absent()
        click('input[id="ublock.enabled-toggle"]')
        wait(lambda: not prefs()['ublock.enabled'])
        blocker_absent()
        click('input[id="ublock.enabled-toggle"]')
        wait(lambda: prefs()['ublock.enabled'])
        blocker_absent()
        click('#setup-buttons button:first-child')
        step('search-engines')
        blocker_absent()
        assert not rpc('setPref', 'ublock.install_allowed', True)['ok']
        close()
        start('pending-restart', profile)
        blocker_absent()
        passed('no_install_before_confirmation_even_after_toggles_back_and_restart')
        close()

        profile = start('off')
        privacy()
        click('input[id="ublock.enabled-toggle"]')
        wait(lambda: not prefs()['ublock.enabled'])
        next_step('services')
        next_step('data-import')
        blocker_absent()
        next_step('password-manager')
        next_step('finish')
        click('#setup-buttons button:last-child')
        wait_js("return location.href.includes('newtab') || location.href.includes('new-tab-page')")
        nav_setup()
        assert prefs()['completed_onboarding']
        blocker_absent()
        close()
        start('off-restart', profile)
        blocker_absent()
        assert not prefs()['ublock.enabled']
        passed('off_confirmation_and_completed_setup_do_not_install_on_restart')
        close()

        profile = start('skip-privacy')
        click('.setup-progress > button:last-child')
        step('finish')
        click('#setup-buttons button:last-child')
        wait_js("return location.href.includes('newtab') || location.href.includes('new-tab-page')")
        nav_setup()
        blocker_absent()
        close()
        start('skip-restart', profile)
        blocker_absent()
        passed('skipping_privacy_does_not_authorize_install')
        close()

        profile = start('next-on')
        privacy()
        blocker_absent()
        next_step('services')
        assert not prefs()['services.user_consented']
        wait(lambda: extensions().get(UBLOCK) is True)
        assert prefs()['ublock.install_allowed']
        close()
        start('on-restart', profile)
        assert extensions()[UBLOCK]
        passed('next_with_blocker_on_installs_and_persists')
        close()

        # Older profiles predate the consent marker. Preserve their existing blocker.
        preference_file = profile / 'Default/Preferences'
        legacy = json.loads(preference_file.read_text())
        legacy['helium'].pop('ublock', None)
        preference_file.write_text(json.dumps(legacy))
        start('legacy-installed', profile)
        assert extensions()[UBLOCK]
        privacy()
        click('input[id="ublock.enabled-toggle"]')
        next_step('services')
        assert not prefs()['services.user_consented']
        assert extensions()[UBLOCK] is False
        close()
        start('legacy-disabled', profile)
        assert extensions()[UBLOCK] is False and not prefs()['ublock.enabled']
        passed('legacy_install_and_disabled_state_preserved')
        close()

        for name, action in [('defaults', 'defaults'), ('forward-dot', 'dot')]:
            start(name)
            blocker_absent()
            if action == 'defaults':
                click('.welcome-actions .ghost')
                wait_js("return location.href.includes('newtab') || location.href.includes('new-tab-page')")
                nav_setup()
            else:
                privacy()
                click('.setup-progress > button:nth-child(6)')
                step('password-manager')
            wait(lambda: extensions().get(UBLOCK) is True)
            passed(name + '_confirms_install')
            close()

        profile = start('all-helium-off')
        services()
        for key in HELIUM:
            click(f'input[id="services.{key}-toggle"]')
        expected = all_helium_off()
        # Local blocker, browser updates and suggestions never count as Helium use.
        assert prefs()['ublock.enabled'] and prefs()['services.browser_updates']
        next_step('data-import')
        expected = all_helium_off()
        assert extensions()[UBLOCK]
        next_step('password-manager')
        assert js("return document.querySelector('.one-time-notice').textContent.includes('one-time')")
        close()
        start('all-off-restart', profile)
        assert all_helium_off() == expected
        passed('all_helium_off_disables_master_and_persists', expected)
        services()
        for key in HELIUM:
            click(f'input[id="services.{key}-toggle"]')
            wait(lambda: prefs()['services.enabled'])
            values = prefs()
            assert all(values['services.' + candidate] == (candidate == key)
                       for candidate in HELIUM), values
            click(f'input[id="services.{key}-toggle"]')
            wait(lambda: not prefs()['services.enabled'])
            all_helium_off()
        passed('each_service_can_independently_enable_the_master_without_enabling_others')
        close()

    if args.extension_fixture and args.only in ('all', 'extension'):
        fixture = args.extension_fixture.resolve()
        report['fixture_hashes'] = {name: hashlib.sha256((fixture / name).read_bytes()).hexdigest() for name in ['keepassxc.crx', 'manifest.json', 'icon.png']}

        class Service(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                self.do_GET()

            def do_GET(self):
                requests.append({'method': self.command, 'path': self.path, 'mode': mode})
                if self.command == 'POST':
                    self.rfile.read(int(self.headers.get('Content-Length', 0)))
                path = urlparse(self.path).path
                if mode == 'failure':
                    self.send_error(503)
                    return
                if path == '/ext/cws_snippet':
                    body = field(1, PASSWORD_MANAGER) + field(2, (fixture / 'manifest.json').read_text()) + field(3, 'KeePassXC-Browser') + field(4, 'Password manager installation test') + field(5, origin + '/icon.png')
                    mime = 'application/x-protobuf'
                elif path == '/icon.png':
                    body, mime = (fixture / 'icon.png').read_bytes(), 'image/png'
                elif path == '/ext':
                    body, mime = (fixture / 'keepassxc.crx').read_bytes(), 'application/x-chrome-extension'
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header('Content-Type', mime)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = ThreadingHTTPServer(('127.0.0.1', 0), Service)
        origin = f'http://127.0.0.1:{server.server_port}'
        threading.Thread(target=server.serve_forever, daemon=True).start()
        profile = start('password-manager')
        set_pref('services.origin_override', origin)
        services()
        for key in HELIUM:
            click(f'input[id="services.{key}-toggle"]')
        next_step('data-import')
        next_step('password-manager')
        expected = all_helium_off()
        time.sleep(1)
        assert not requests, requests
        assert not rpc('installExtension', PASSWORD_MANAGER, False)['ok']
        assert not rpc('installExtension', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', True)['ok']
        assert not requests
        mode = 'failure'
        assert not rpc('installExtension', PASSWORD_MANAGER, True)['ok']
        assert all_helium_off() == expected
        requests.clear()
        mode = 'success'
        js("window.installResult=null;const old=cr.webUIResponse;cr.webUIResponse=(id,ok,value)=>{if(id==='cancel-test'){window.installResult={ok,value};cr.webUIResponse=old}else old(id,ok,value)};chrome.send('installExtension',['cancel-test'," + json.dumps(PASSWORD_MANAGER) + ',true]);')
        assert not rpc('installExtension', 'nngceckbapebfimnlniiiahkandclblb', False)['ok']
        phase('Cancel the KeePassXC installation prompt')
        wait_js('return window.installResult', 180)
        result = js('return window.installResult')
        assert not result['ok'] and result['value']['code'] == 10, result
        assert all_helium_off() == expected
        assert not any(urlparse(item['path']).path == '/ext' for item in requests)
        passed('cancel_leaves_services_off_and_downloads_no_package')
        requests.clear()
        js("[...document.querySelectorAll('.pm-option')].find(e=>e.innerText.includes('KeePassXC')).querySelector('button').click()")
        phase('Accept the KeePassXC installation prompt')
        wait_js("return [...document.querySelectorAll('.pm-option')].find(e=>e.innerText.includes('KeePassXC')).querySelector('button').textContent.includes('Installed')", 180)
        assert extensions()[PASSWORD_MANAGER]
        assert all_helium_off() == expected
        assert any(urlparse(item['path']).path == '/ext' for item in requests)
        installed_requests = list(requests)
        count = len(requests)
        assert not rpc('installExtension', 'nngceckbapebfimnlniiiahkandclblb', False)['ok']
        wd('POST', session + '/window', {'handle': inspector_handle})
        wd('POST', session + '/url', {'url': 'chrome://extensions/'})
        wait_js('return !!chrome.developerPrivate')
        browser_log = profile / 'password-manager-browser.log'
        log_offset = browser_log.stat().st_size
        js('chrome.developerPrivate.autoUpdate(()=>{void chrome.runtime.lastError});')
        # Disabled-service requests are rejected locally. Do not wait through
        # the updater's exponential network-error retries to test this gate.
        def update_blocked():
            with browser_log.open() as stream:
                stream.seek(log_offset)
                return any('Blocked URL in TrkProtocolHandler' in line and
                           'helium-services-are-disabled' in line and
                           PASSWORD_MANAGER in line for line in stream)
        wait(update_blocked)
        time.sleep(2)
        assert len(requests) == count, requests
        passed('extension_update_attempt_is_blocked_locally_without_service_requests')
        wd('POST', session + '/window', {'handle': setup_handle})
        close()
        start('installed-restart', profile)
        assert extensions()[PASSWORD_MANAGER]
        assert all_helium_off() == expected
        passed('one_time_install_survives_restart_without_enabling_services_or_updates', installed_requests)
        close()
    else:
        report['extension_installation'] = 'not run; pass --extension-fixture to exercise native prompts'

    report['passed'] = True
finally:
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    close()
    driver.terminate()
    driver.wait(timeout=10)
    log.close()
    if server:
        server.shutdown()
        server.server_close()
    for profile in profiles:
        for browser_log in profile.glob('*-browser.log'):
            shutil.copy2(browser_log, out / browser_log.name)
        shutil.rmtree(profile)
