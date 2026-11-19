#!/usr/bin/env python3
"""Verify independent tab order preferences with native macOS shortcuts."""

import argparse
import base64
from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time

import websocket

from browser_test_profiles import temporary_profile


CTRL_PREF = 'helium.browser.mru_tab_cycling'
BRACKET_PREF = 'helium.browser.bracket_tab_cycling_mru'
SWITCHER_PREF = 'helium.browser.visual_tab_switcher'
TOGGLE_IDS = ['tabCyclingMRU', 'bracketTabCyclingMRU']
RECENCY = 'CDGFAEB'


def wait_for(read, description, seconds=10):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = read()
        if value:
            return value
        time.sleep(0.08)
    raise RuntimeError(f'Timed out waiting for {description}')


@contextmanager
def browser_process(command, log):
    with log.open('wb') as output:
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
        try:
            yield process
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


class DevTools:
    def __init__(self, socket):
        self.socket = socket
        self.sequence = 0

    def send(self, method, params=None, session=None):
        self.sequence += 1
        payload = dict(id=self.sequence, method=method, params=params or {})
        if session:
            payload['sessionId'] = session
        self.socket.send(json.dumps(payload))
        while True:
            message = json.loads(self.socket.recv())
            if message.get('id') == self.sequence:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message['result']

    def attach(self, target):
        return self.send('Target.attachToTarget',
                         dict(targetId=target, flatten=True))['sessionId']

    def evaluate(self, session, script):
        result = self.send('Runtime.evaluate',
                           dict(expression=script, awaitPromise=True, returnByValue=True),
                           session)
        if 'exceptionDetails' in result:
            raise RuntimeError(result['exceptionDetails'])
        return result['result'].get('value')


def install_fixture(profile):
    key = subprocess.run(
        ['/usr/bin/openssl', 'genrsa', '2048'], capture_output=True, check=True).stdout
    public_key = subprocess.run(
        ['/usr/bin/openssl', 'rsa', '-pubout', '-outform', 'DER'],
        input=key, capture_output=True, check=True).stdout
    extension_id = ''.join(chr(ord('a') + int(n, 16))
                           for n in hashlib.sha256(public_key).hexdigest()[:32])
    extension = profile / 'extension'
    extension.mkdir()
    (extension / 'fixture.html').write_text('<!doctype html><title>Shortcut test controller</title>')
    (extension / 'manifest.json').write_text(json.dumps(dict(
        manifest_version=3, name='Local tab shortcut fixture', version='1',
        key=base64.b64encode(public_key).decode(), permissions=['tabs', 'tabGroups'])))
    return extension, f'chrome-extension://{extension_id}/fixture.html'


def run_cases(cdp, controller, settings, keys, pid, report):
    def control(script):
        return cdp.evaluate(controller, script)

    def pref(key):
        return cdp.evaluate(settings, f"""new Promise(resolve =>
            chrome.settingsPrivate.getPref({json.dumps(key)}, pref => resolve(pref?.value)))""")

    def set_pref(key, value):
        assert cdp.evaluate(settings, f"""new Promise(resolve =>
            chrome.settingsPrivate.setPref({json.dumps(key)}, {json.dumps(value)}, '', resolve))""")
        assert pref(key) is value, key

    def in_settings(script):
        return cdp.evaluate(settings, """(() => {
            function locate(id, root = document) {
                const toggle = root.querySelector('#' + id);
                if (toggle) return toggle;
                for (const node of root.querySelectorAll('*')) {
                    const nested = node.shadowRoot && locate(id, node.shadowRoot);
                    if (nested) return nested;
                }
            }
        """ + script + '})()')

    def ready_toggles():
        rows = in_settings(f"""
            return {json.dumps(TOGGLE_IDS)}.map(id => {{
                const toggle = locate(id);
                return toggle?.pref?.key ? [toggle.pref.key, toggle.label] : null;
            }});
        """)
        return rows if all(rows) else None

    wait_for(lambda: cdp.evaluate(settings, 'Boolean(window.chrome?.settingsPrivate)'),
             'Appearance settings')
    toggles = wait_for(ready_toggles, 'the two tab cycling settings')
    assert [row[0] for row in toggles] == [CTRL_PREF, BRACKET_PREF], toggles
    assert 'Ctrl+Tab' in toggles[0][1] and '⌘⇧[' in toggles[1][1], toggles
    assert pref(CTRL_PREF) is True and pref(BRACKET_PREF) is False
    report['settings'] = toggles
    report['defaults'] = dict(control_recent=True, bracket_recent=False)

    # Keep the extension and Settings in a separate window from the tabs under test.
    urls = [f'data:text/html,<title>{name}</title>{name}' for name in 'ABCDEFG']
    fixture = control(f'chrome.windows.create({{url: {json.dumps(urls)}}})')['id']
    def fixture_tabs():
        rows = control(f'chrome.tabs.query({{windowId: {fixture}}})')
        return rows if {tab['title'] for tab in rows} == set('ABCDEFG') else None

    tabs = wait_for(fixture_tabs, 'the seven fixture tabs')
    ids = {tab['title']: tab['id'] for tab in tabs}
    assert len(ids) == len(urls), tabs

    def active():
        return control(
            f'chrome.tabs.query({{windowId: {fixture}, active: true}}).then(([tab]) => tab.title)')

    def select(name):
        control(f'chrome.tabs.update({ids[name]}, {{active: true}})')
        wait_for(lambda: active() == name, f'tab {name} to activate')

    def key_case(label, family, direction, expected, *, setup=RECENCY, count=1):
        for name in setup:
            select(name)
        control(f'chrome.windows.update({fixture}, {{focused: true}})')
        subprocess.run([keys, str(pid), family, direction, str(count)], check=True)
        try:
            wait_for(lambda: active() == expected, f'{label} to activate {expected}', seconds=3)
        except RuntimeError as error:
            raise AssertionError(f'{label}: expected {expected}, active tab is {active()}') from error
        report['cases'].append(dict(case=label, selected=expected))

    key_case('Default Control forward uses recency', 'control', 'next', 'E')
    key_case('Default Control backward uses recency', 'control', 'previous', 'G')
    key_case('Default brackets move down', 'bracket', 'next', 'C')
    key_case('Default brackets move up', 'bracket', 'previous', 'A')

    set_pref(CTRL_PREF, False)
    assert pref(BRACKET_PREF) is False
    key_case('Sequential Control includes tabs outside the recent five', 'control', 'next', 'C')
    key_case('Sequential Control moves backward', 'control', 'previous', 'A')
    key_case('Changing Control leaves bracket order independent', 'bracket', 'next', 'C')

    in_settings("locate('bracketTabCyclingMRU').shadowRoot.querySelector('cr-toggle').click();")
    wait_for(lambda: pref(BRACKET_PREF) is True, 'the bracket Settings toggle to take effect')
    assert pref(CTRL_PREF) is False
    key_case('Bracket recency moves forward', 'bracket', 'next', 'E')
    key_case('Bracket recency moves backward', 'bracket', 'previous', 'C')
    key_case('Held Command advances within one recency cycle', 'bracket', 'next', 'A', count=2)
    key_case('Changing brackets leaves Control sequential', 'control', 'next', 'C')

    set_pref(CTRL_PREF, True)
    key_case('Both settings can use recency', 'control', 'next', 'E')
    set_pref(SWITCHER_PREF, False)
    key_case('Control recency with the visual switcher off', 'control', 'next', 'E')
    set_pref(CTRL_PREF, False)
    key_case('Sequential Control with the visual switcher off', 'control', 'next', 'C')

    set_pref(BRACKET_PREF, False)
    group = control(f'chrome.tabs.group({{tabIds: [{ids["C"]}]}})')
    control(f'chrome.tabGroups.update({group}, {{collapsed: true}})')
    key_case('Bracket cycling skips a collapsed group', 'bracket', 'next', 'D', setup='B')
    control(f'chrome.tabs.update({ids["F"]}, {{pinned: true}})')
    key_case('Bracket cycling uses pinned sidebar position', 'bracket', 'previous', 'F', setup='A')
    key_case('Bracket cycling wraps at the top', 'bracket', 'previous', 'G', setup='F')
    control(f'chrome.tabs.move({ids["G"]}, {{index: 2}})')
    key_case('Bracket cycling follows a reordered tab', 'bracket', 'next', 'G', setup='A')
    set_pref(BRACKET_PREF, True)


def check(output, report_path, report):
    app = output / 'Lune.app'
    binary = app / 'Contents/MacOS/Lune'
    framework = app / 'Contents/Frameworks/Lune Framework.framework/Lune Framework'
    with framework.open('rb') as stream:
        report['framework_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
    report['browser_architecture'] = subprocess.check_output(
        ['lipo', '-archs', str(binary)], text=True).strip()
    report['host_architecture'] = platform.machine()

    with temporary_profile('lune-tab-cycling-') as directory:
        profile = Path(directory)
        (profile / 'Default').mkdir()
        preferences = profile / 'Default/Preferences'
        preferences.write_text(json.dumps({
            'helium': {
                'completed_onboarding': True,
                'services': {'enabled': False, 'browser_updates': False},
            },
        }))
        extension, controller_url = install_fixture(profile)
        keys = profile / 'post-tab-shortcut'
        swift = Path(__file__).parent / 'native-checks/tab-cycling-keys.swift'
        subprocess.run(['xcrun', 'swiftc', '-module-cache-path', str(profile / 'swift-cache'),
                        str(swift), '-o', str(keys)], check=True)

        options = [binary, f'--user-data-dir={profile}', '--remote-debugging-port=0',
                   '--no-first-run', '--no-default-browser-check', '--use-mock-keychain',
                   '--disable-background-networking', '--disable-sync',
                   f'--load-extension={extension}', f'--disable-extensions-except={extension}',
                   '--custom-update-server-url=http://127.0.0.1:9/',
                   '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1']
        with browser_process(options, report_path.with_suffix('.browser.log')) as process:
            active_port = profile / 'DevToolsActivePort'

            def debugging_port():
                if process.poll() is not None:
                    raise RuntimeError(f'Browser exited with status {process.returncode} before launch')
                if active_port.exists():
                    lines = active_port.read_text().splitlines()
                    if len(lines) == 2:
                        return lines

            debug = wait_for(debugging_port, 'the disposable browser', seconds=120)
            with closing(websocket.create_connection(
                f'ws://127.0.0.1:{debug[0]}{debug[1]}', suppress_origin=True, timeout=20
            )) as socket:
                cdp = DevTools(socket)
                controller = cdp.attach(cdp.send(
                    'Target.createTarget', {'url': controller_url})['targetId'])
                settings = cdp.attach(cdp.send(
                    'Target.createTarget', {'url': 'chrome://settings/appearance'})['targetId'])
                wait_for(lambda: cdp.evaluate(controller, 'Boolean(window.chrome?.tabs)'),
                         'the fixture extension')
                run_cases(cdp, controller, settings, keys, process.pid, report)

                def saved_prefs():
                    browser = json.loads(preferences.read_text())['helium'].get('browser', {})
                    return (browser.get('mru_tab_cycling') is False and
                            browser.get('bracket_tab_cycling_mru') is True)

                wait_for(saved_prefs, 'both saved shortcut settings')
                report['independent_values_persisted'] = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    report = {'passed': False, 'cases': []}
    try:
        check(args.output.resolve(strict=True), args.report, report)
        report['passed'] = True
    finally:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f"PASS: {len(report['cases'])} native shortcut cases")


if __name__ == '__main__':
    main()
