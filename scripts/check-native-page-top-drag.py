#!/usr/bin/env python3
"""Verify page-top dragging with Quartz input and actual WindowServer bounds."""

import argparse
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import platform
import re
import subprocess
import threading
import time
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from browser_test_profiles import temporary_profile


PREF = 'helium.browser.page_top_window_drag'
LABEL = 'Allow window dragging from the top of webpages'
PAGE = """<!doctype html><meta charset=utf-8><title>Page-top drag fixture</title>
<style>
body { margin: 0; height: 200vh; }
header { height: 52px; position: relative; }
#blank { height: 100%; width: 180px; position: absolute; left: 160px; }
#text, #link, #custom, #frame { position: absolute; top: 23px; }
#text { left: 355px; font: 16px sans-serif; }
#frame { left: 460px; width: 70px; height: 30px; border: 0; top: 19px; }
#link { left: 535px; }
#custom { left: 740px; width: 80px; height: 25px; cursor: default; background: #eef; }
</style>
<header role=banner>
  <span id=blank></span>
  <span id=text>Select this text</span>
  <iframe id=frame srcdoc="<body style='margin:0'>Frame<script>
    addEventListener('pointerdown', () => ++parent.count.frame)
  </script>"></iframe>
  <a id=link href="#link">Open link</a>
  <div id=custom></div>
</header>
<script>
window.count = {blank: 0, link: 0, moves: 0, releases: 0, frame: 0,
                presses: 0, passiveMotion: 0, claimed: 0, blankReleases: 0};
const blank = document.querySelector('#blank');
blank.addEventListener('click', () => ++count.blank);
blank.addEventListener('pointerup', () => ++count.blankReleases);
document.addEventListener('mousedown', () => ++count.presses, {passive: true});
window.addEventListener('pointermove', event => {
  if (event.buttons === 1 && event.target === blank) ++count.passiveMotion;
}, {passive: true});
// Frameworks can attach handlers to a common ancestor and act on individual
// widgets only. The same point can belong to the page when the handler claims it.
document.querySelector('header').addEventListener('mousedown', event => {
  if (event.target === blank && window.claim === 'press') {
    event.preventDefault();
    ++count.claimed;
  }
});
document.querySelector('header').addEventListener('pointermove', event => {
  if (event.target !== blank || event.buttons !== 1) return;
  if (window.claim === 'motion') {
    event.preventDefault();
    ++count.claimed;
  } else if (window.claim === 'capture') {
    blank.setPointerCapture(event.pointerId);
    ++count.claimed;
  } else if (window.claim === 'delay') {
    window.claim = null;
    const until = performance.now() + 220;
    while (performance.now() < until) {}
    ++count.claimed;
  }
});
document.querySelector('#link').addEventListener('click', event => {
  event.preventDefault();
  ++count.link;
});
const custom = document.querySelector('#custom');
custom.addEventListener('pointerdown', event => custom.setPointerCapture(event.pointerId));
custom.addEventListener('pointermove', event => {
  if (custom.hasPointerCapture(event.pointerId)) ++count.moves;
});
custom.addEventListener('pointerup', () => ++count.releases);
</script>
"""

FIND_TOGGLE = """
function find(root) {
  const toggle = root.querySelector('#pageTopWindowDrag');
  if (toggle) return toggle;
  for (const element of root.querySelectorAll('*')) {
    if (!element.shadowRoot) continue;
    const child = find(element.shadowRoot);
    if (child) return child;
  }
  return null;
}
const toggle = find(document);
"""


class FixturePage(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = PAGE.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


def wait_for(read, description, timeout=20):
    stop = time.monotonic() + timeout
    while time.monotonic() < stop:
        value = read()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError(f'Timed out waiting for {description}')


@contextmanager
def process(command, log_path):
    with log_path.open('w') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            yield child
        finally:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()


class Driver:
    def __init__(self, port, debug_address):
        self.url = f'http://127.0.0.1:{port}'
        self.session = ''
        result = self.request('POST', '/session', {'capabilities': {'alwaysMatch': {
            'goog:chromeOptions': {'debuggerAddress': debug_address},
        }}})
        self.session = '/session/' + result['sessionId']

    def request(self, method, path, data=None):
        body = json.dumps(data).encode() if data is not None else None
        request = Request(self.url + self.session + path, data=body, method=method,
                          headers={'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)['value']
        except HTTPError as error:
            raise RuntimeError(error.read().decode()) from error

    def script(self, script, *args, asynchronous=False):
        path = '/execute/async' if asynchronous else '/execute/sync'
        return self.request('POST', path, {'script': script, 'args': args})

    def cdp(self, command, **params):
        return self.request('POST', '/goog/cdp/execute',
                            {'cmd': command, 'params': params})

    def get_pref(self):
        return self.script(
            'chrome.settingsPrivate.getPref(arguments[0], arguments[1]);',
            PREF, asynchronous=True)['value']

    def switch(self, handle):
        self.request('POST', '/window', {'handle': handle})


def drag_setting(driver, settings):
    driver.switch(settings)
    wait_for(lambda: driver.script(FIND_TOGGLE + 'return toggle?.pref?.key;') == PREF,
             'the page-top drag setting')
    label = driver.script(FIND_TOGGLE + 'return toggle.label;')
    assert label == LABEL, label
    return driver.get_pref()


def set_drag_enabled(driver, settings, page, enabled):
    assert drag_setting(driver, settings) is not enabled
    x, y = driver.script(FIND_TOGGLE + """
      toggle.scrollIntoView({block: 'center'});
      const bounds = toggle.shadowRoot.querySelector('cr-toggle').getBoundingClientRect();
      return [bounds.x + bounds.width / 2, bounds.y + bounds.height / 2];
    """)
    driver.cdp('Input.dispatchMouseEvent', type='mousePressed', x=x, y=y,
               button='left', buttons=1, clickCount=1)
    driver.cdp('Input.dispatchMouseEvent', type='mouseReleased', x=x, y=y,
               button='left', clickCount=1)
    wait_for(lambda: driver.get_pref() is enabled, 'the backend preference to change')
    driver.switch(page)


def run_gestures(driver, mouse, pid, report, settings, page, loopback, local_file):
    def gesture(name, point, *options, delta=0):
        observed = json.loads(subprocess.check_output(
            [str(mouse), str(pid), *(str(v) for v in point), *options], text=True))
        observed.update(name=name, counters=driver.script('return window.count;'),
                        selection=driver.script('return getSelection().toString();'))
        report['gestures'].append(observed)
        dx = observed['after'][0] - observed['before'][0]
        dy = observed['after'][1] - observed['before'][1]
        assert abs(dx - delta) <= 1 and abs(dy) <= 1, (delta, observed)
        return observed

    assert drag_setting(driver, settings) is True
    report['default_enabled'] = True
    driver.switch(page)
    blank = (220, 28)
    assert gesture('subthreshold click', blank, 'slip')['counters']['blank'] == 1
    background = gesture('blank span with passive and delegated listeners',
                         blank, 'drag', delta=40)['counters']
    assert background['blank'] == 1
    assert background['presses'] == 2 and background['passiveMotion'] > 0
    gesture('rapid drag and reverse direction', (220, 27), 'drag', 'rapid', 'left',
            delta=-40)
    gesture('last point in band', (220, 51), 'drag', delta=40)
    gesture('first point outside band', (220, 52), 'drag')
    gesture('Command bypass', blank, 'drag', 'command')
    assert gesture('text selection', (359, 29), 'drag')['selection']
    custom = gesture('scripted drag with pointer capture', (755, 30), 'drag')
    assert custom['counters']['moves'] > 0 and custom['counters']['releases'] == 1
    assert gesture('embedded webpage input', (476, 30), 'drag')['counters']['frame'] == 1
    gesture('drag after page input', blank, 'drag', 'left', delta=-40)

    for mode, name in (
        ('press', 'delegated mousedown cancellation'),
        ('motion', 'delegated pointermove cancellation'),
        ('capture', 'delegated pointer capture on first motion'),
        ('delay', 'late renderer response'),
    ):
        releases = driver.script('window.claim = arguments[0]; count.claimed = 0;'
                                 'return count.blankReleases;', mode)
        counters = gesture(name, blank, 'drag')['counters']
        assert counters['claimed'] > 0 and counters['blankReleases'] == releases + 1
    driver.script('window.claim = null;')
    driver.script('document.querySelector("#blank").setAttribute("role", "button");')
    gesture('ARIA button with default cursor', blank, 'drag')
    driver.script('document.querySelector("#blank").removeAttribute("role");')
    driver.script('document.querySelector("#blank").style.cursor = "grab";')
    gesture('page grab cursor', blank, 'drag')
    driver.script('document.querySelector("#blank").style.removeProperty("cursor");')

    for url, name in (
        (local_file.as_uri(), 'same fixture over file'),
        ('data:text/html;charset=utf-8,' + quote(PAGE), 'same fixture over data'),
    ):
        driver.request('POST', '/url', {'url': url})
        assert driver.script('return !!window.count;')
        gesture(name, blank, 'drag', delta=40)

    driver.request('POST', '/url', {'url': 'chrome://media-engagement/'})
    wait_for(lambda: driver.script('return !!document.querySelector("h1");'),
             'Media Engagement heading')
    gesture('Media Engagement above the heading', (520, 12), 'drag', 'left', delta=-40)
    assert driver.script('return document.elementFromPoint(520, 28)?.localName;') == 'h1'
    gesture('Media Engagement beside the heading text', (520, 28), 'drag', delta=40)

    driver.request('POST', '/url', {'url': loopback})
    wait_for(lambda: driver.script('return !!window.count;'), 'the loopback page to reload')
    set_drag_enabled(driver, settings, page, False)
    gesture('disabled in the same window', blank, 'drag')
    set_drag_enabled(driver, settings, page, True)

    # A link preview can add another native window. Run this click after all
    # drag assertions so it cannot obscure or redirect any of their input.
    point = driver.script("""
      const r = document.querySelector('#link').getBoundingClientRect();
      return [r.x + r.width / 2, r.y + r.height / 2];
    """)
    assert gesture('link click', point)['counters']['link'] == 1
    set_drag_enabled(driver, settings, page, False)


@contextmanager
def browser_session(output, options, profile, report_path):
    active_port = profile / 'DevToolsActivePort'
    active_port.unlink(missing_ok=True)
    driver_log = report_path.with_suffix('.chromedriver.log')
    with process([output / 'chromedriver', '--port=0', '--allowed-ips=127.0.0.1'],
                 driver_log), process(options, report_path.with_suffix('.browser.log')) as child:
        debug = wait_for(lambda: active_port.read_text().splitlines() if active_port.exists() else None,
                         'the browser’s temporary debugging endpoint')
        port = wait_for(lambda: re.search(r'successfully on port (\d+)', driver_log.read_text()),
                        'ChromeDriver to bind')
        yield child, Driver(port[1], f'127.0.0.1:{debug[0]}')


def check(output, report_path, report):
    app = output / 'Lune.app'
    browser = app / 'Contents/MacOS/Lune'
    framework = app / 'Contents/Frameworks/Lune Framework.framework/Lune Framework'
    with framework.open('rb') as handle:
        report['framework_sha256'] = hashlib.file_digest(handle, 'sha256').hexdigest()
    report['browser_architecture'] = subprocess.check_output(
        ['lipo', '-archs', str(browser)], text=True).strip()
    report['host_architecture'] = platform.machine()
    with (ThreadingHTTPServer(('127.0.0.1', 0), FixturePage) as server,
          temporary_profile('lune-page-top-drag-') as directory):
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/'
        profile = Path(directory)
        local_file = profile / 'drag-fixture.html'
        local_file.write_text(PAGE)
        (profile / 'Default').mkdir()
        preferences = profile / 'Default/Preferences'
        preferences.write_text(json.dumps({'helium': {
            'completed_onboarding': True,
            'services': {'enabled': False, 'browser_updates': False},
            'browser': {
                'zen_mode_top_chrome_pinned': False,
                'top_controls_hover_disabled': True,
                'zen_mode_sidebar_pinned': False,
            },
        }}))
        mouse = profile / 'post-gesture'
        swift = Path(__file__).parent / 'native-checks/page-top-drag-mouse.swift'
        subprocess.run(['xcrun', 'swiftc', '-module-cache-path', str(profile / 'swift-cache'),
                        str(swift), '-o', str(mouse)], check=True)
        options = [str(browser), f'--user-data-dir={profile}', '--remote-debugging-port=0',
                   '--no-first-run', '--no-default-browser-check', '--use-mock-keychain',
                   '--disable-background-networking', '--disable-sync',
                   '--window-position=100,85', '--window-size=1100,700',
                   '--custom-update-server-url=http://127.0.0.1:9/',
                   '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1']
        try:
            with browser_session(output, options + [url], profile, report_path) as (child, driver):
                page = driver.request('GET', '/window')
                wait_for(lambda: driver.script('return document.readyState === "complete" && !!window.count;'),
                         'the loopback page to load')
                settings = driver.request('POST', '/window/new', {'type': 'tab'})['handle']
                driver.switch(settings)
                driver.request('POST', '/url', {'url': 'chrome://settings/appearance'})
                driver.switch(page)
                run_gestures(driver, mouse, child.pid, report, settings, page, url, local_file)
                wait_for(lambda: json.loads(preferences.read_text()).get('helium', {}).get(
                    'browser', {}).get('page_top_window_drag') is False, 'the off preference on disk')
            restart_report = report_path.with_name(report_path.stem + '-restart.json')
            with browser_session(output, options + ['--headless=new', 'about:blank'],
                                 profile, restart_report) as (_, driver):
                settings = driver.request('GET', '/window')
                driver.request('POST', '/url', {'url': 'chrome://settings/appearance'})
                assert drag_setting(driver, settings) is False
                report['off_persisted_after_restart'] = True
        finally:
            server.shutdown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = {'passed': False, 'gestures': []}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    try:
        check(args.output.resolve(strict=True), args.report, report)
        report['passed'] = True
    finally:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f"PASS: {len(report['gestures'])} Quartz gestures and live Settings checks")


if __name__ == '__main__':
    main()
