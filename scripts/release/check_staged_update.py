#!/usr/bin/env python3
"""Exercise staged update replacement in one running Lune with a loopback appcast.

Pass an updater-enabled, pre-signing Lune.app and its matching ChromeDriver.
The test uses a disposable copy with a unique bundle identifier and an ephemeral
Ed25519 key. Both offered archives contain tiny fixture apps.
"""
import argparse
import base64
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import plistlib
import subprocess
import threading
import time
import uuid
from xml.etree import ElementTree as ET

from check_update import info, run, session
from browser_test_profiles import new_profile
from manual_update_fixture import SPARKLE


def wait_for(predicate, timeout, description):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(.25)
    raise RuntimeError('Timed out waiting for ' + description)


def prepare(root, app, bundle_id, arch, openssl, debug_interval):
    key = root / 'fixture.pem'
    run(openssl, 'genpkey', '-algorithm', 'ED25519', '-out', key)
    public = subprocess.check_output([openssl, 'pkey', '-in', key, '-pubout', '-outform', 'DER'])
    host = root / 'Lune.app'
    run('ditto', app, host)
    plist = host / 'Contents/Info.plist'
    metadata = info(host)
    metadata.update(CFBundleIdentifier=bundle_id, SUPublicEDKey=base64.b64encode(public[-32:]).decode(),
                    SUFeedURL='http://127.0.0.1:1/unused', SUVerifyUpdateBeforeExtraction=True,
                    SUScheduledCheckInterval=60 if debug_interval else 3600,
                    _SUEnableDebugUpdateCheckIntervals=debug_interval)
    plist.write_bytes(plistlib.dumps(metadata))
    run('codesign', '--force', '--deep', '--sign', '-', host)

    served = root / 'served'
    served.mkdir()
    feed = served / 'mac' / f'appcast-{arch}.xml'
    feed.parent.mkdir()
    feeds = []
    for version in ('99.1.2', '99.1.3'):
        bundle = root / version / 'Lune.app'
        binary = bundle / 'Contents/MacOS/Lune'
        binary.parent.mkdir(parents=True)
        # Launch Services starts this executable only after an explicit relaunch.
        marker = json.dumps(str(root / ('launched-' + version)))
        program = f'#include <stdio.h>\nint main(void) {{ FILE *file = fopen({marker}, "w"); return file ? fclose(file) : 1; }}'
        subprocess.run(['xcrun', 'clang', '-arch', arch, '-x', 'c', '-', '-o', binary],
                       input=program, text=True, check=True)
        (bundle / 'Contents/Info.plist').write_bytes(plistlib.dumps({
            'CFBundleIdentifier': bundle_id, 'CFBundleExecutable': 'Lune',
            'CFBundlePackageType': 'APPL', 'CFBundleVersion': version,
            'CFBundleShortVersionString': version, 'SUPublicEDKey': metadata['SUPublicEDKey']}))
        run('codesign', '--force', '--sign', '-', bundle)
        archive = served / f'Lune-{version}.zip'
        run('ditto', '-c', '-k', '--keepParent', bundle, archive)
        signature = subprocess.check_output([openssl, 'pkeyutl', '-sign', '-rawin', '-inkey', key, '-in', archive])
        rss = ET.fromstring('<rss version="2.0"><channel><title>Lune fixture</title><item/></channel></rss>')
        item = rss.find('./channel/item')
        ET.SubElement(item, f'{{{SPARKLE}}}version').text = version
        ET.SubElement(item, 'enclosure', {'url': archive.name, 'length': str(archive.stat().st_size),
                      'type': 'application/zip', f'{{{SPARKLE}}}edSignature': base64.b64encode(signature).decode()})
        feeds.append(rss)
    return host, served, feed, feeds


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app', type=Path, required=True)
    p.add_argument('--driver', type=Path, required=True)
    p.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    p.add_argument('--trigger', choices=['about', 'automatic'], required=True)
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--openssl', default='openssl', help='OpenSSL 3 executable')
    p.add_argument('--debug-interval', action='store_true',
                   help='Use the one-minute test cadence of a Debug Sparkle build')
    p.add_argument('--offer', choices=['newer', 'unchanged', 'download-error', 'bad-signature'], default='newer')
    p.add_argument('--finish', choices=['quit', 'relaunch'], default='quit')
    args = p.parse_args()
    if args.offer == 'bad-signature' and args.finish == 'relaunch':
        p.error('The rejected update has no relaunch action')
    args.directory.mkdir(parents=True, exist_ok=False)
    root = new_profile('lune-staged-install-')
    profile = new_profile('lune-staged-profile-')
    bundle_id = 'computer.lune.fixture.staged-' + uuid.uuid4().hex
    host, served, feed, offers = prepare(root, args.app, bundle_id, args.arch,
                                         args.openssl, args.debug_interval)
    if args.offer == 'bad-signature':
        offers[1].find('./channel/item/enclosure').set(
            f'{{{SPARKLE}}}edSignature', base64.b64encode(bytes(64)).decode())
    events = []
    second_check = threading.Event()
    allow_response = threading.Event()
    start = time.monotonic()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *values, **kwargs):
            super().__init__(*values, directory=served, **kwargs)

        def do_GET(self):
            events.append({'seconds': round(time.monotonic() - start, 3), 'path': self.path})
            if self.path == '/mac/' + feed.name and second_check.is_set() and not allow_response.wait(60):
                self.send_error(503)
                return
            if self.path == '/Lune-99.1.3.zip' and args.offer == 'download-error':
                self.send_error(503)
                return
            super().do_GET()

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    base = f'http://127.0.0.1:{server.server_port}/'
    def publish(offer):
        enclosure = offer.find('./channel/item/enclosure')
        if enclosure is not None:
            enclosure.set('url', base + enclosure.get('url'))
        pending = feed.with_suffix('.tmp')
        pending.write_bytes(ET.tostring(offer))
        pending.replace(feed)

    cadence_control = args.trigger == 'automatic' and args.debug_interval
    empty = ET.fromstring('<rss version="2.0"><channel><title>Lune fixture</title></channel></rss>')
    publish(empty if cadence_control else offers[0])
    threading.Thread(target=server.serve_forever, daemon=True).start()
    report = {'architecture': args.arch, 'trigger': args.trigger, 'bundle_id': bundle_id, 'requests': events,
              'offer': args.offer, 'finish': args.finish,
              'interval_seconds': info(host)['SUScheduledCheckInterval'],
              'baseline_version': info(host)['CFBundleVersion'], 'passed': False}
    try:
        with session(host, args.driver.resolve(), profile, args.directory / 'driver.log',
                     [f'--custom-update-server-url={base}'], headed=args.finish == 'relaunch') as request:
            def navigate(url):
                request('POST', '/url', {'url': url})

            def status():
                result = request('POST', '/execute/sync', {'script': """
                    const find = root => {
                      for (const e of root.querySelectorAll('*')) {
                        if (e.localName === 'settings-about-page') return e;
                        if (e.shadowRoot) { const found = find(e.shadowRoot); if (found) return found; }
                      }
                    };
                    return find(document)?.currentUpdateStatusEvent_?.status;
                    """, 'args': []})
                return result

            navigate('chrome://settings/privacy/services')
            for key in ('user_consented', 'browser_updates', 'enabled'):
                result = request('POST', '/execute/async', {'script': """
                    chrome.settingsPrivate.setPref(arguments[0], true, '', arguments[1]);
                    """, 'args': ['helium.services.' + key]})
                if result is not True:
                    raise RuntimeError('Could not enable ' + key)
            navigate('chrome://settings/help')
            if cadence_control:
                wait_for(lambda: status() == 'updated', 30, 'initial empty feed check')
                publish(offers[0])
            wait_for(lambda: status() == 'nearly_updated', 120, 'first offer to become ready')
            report['first_ready'] = True
            report['first_ready_seconds'] = time.monotonic() - start
            checkpoint = len(events)
            second_check.set()
            if args.offer != 'unchanged':
                publish(offers[1])
            if args.trigger == 'about':
                request('POST', '/refresh', {})
            def received(path):
                return any(event['path'] == path for event in events[checkpoint:])
            timeout = 30 if args.trigger == 'about' else report['interval_seconds'] + 30
            wait_for(lambda: received('/mac/' + feed.name), timeout,
                     'fresh appcast request after first offer was ready')
            # A fresh page can replay the old ready state. Hold the feed
            # response until the new page is listening for the result.
            registered = request('POST', '/execute/async', {'script': """
                const done = arguments[0];
                import('chrome://resources/js/cr.js').then(({addWebUiListener}) => {
                  window.replacementEvents = [];
                  addWebUiListener('update-status-changed', e => replacementEvents.push({status: e.status, message: e.message}));
                  done(true);
                }).catch(e => done(String(e)));
                """, 'args': []})
            if registered is not True:
                raise RuntimeError(f'Cannot observe About notifications: {registered}')
            allow_response.set()
            if args.offer != 'unchanged':
                wait_for(lambda: received('/Lune-99.1.3.zip'), 60, 'second archive request')
            def refresh_finished():
                updates = request('POST', '/execute/sync', {
                    'script': 'return window.replacementEvents;', 'args': []})
                report['replacement_statuses'] = [event['status'] for event in updates]
                if args.offer == 'bad-signature':
                    return any(event['status'] == 'failed' and 'sign' in event.get('message', '').lower()
                               for event in updates)
                return 'nearly_updated' in report['replacement_statuses']
            wait_for(refresh_finished, 120, 'terminal status for the second feed response')
            if args.offer == 'unchanged' and any(e['path'].endswith('.zip') for e in events[checkpoint:]):
                raise RuntimeError('The already staged update was downloaded again')
            expected = '99.1.3' if args.offer == 'newer' else '99.1.2'
            if args.offer == 'bad-signature':
                expected = report['baseline_version']
            if args.finish == 'relaunch':
                request('POST', '/execute/sync', {'script': "chrome.send('relaunch');", 'args': []})
                wait_for(lambda: (root / ('launched-' + expected)).is_file(), 90,
                         'updated app to launch from the explicit relaunch action')
                report['relaunched_version'] = expected
        wait_for(lambda: info(host)['CFBundleVersion'] == expected, 90, 'expected version to install')
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        allow_response.set()
        server.shutdown()
        server.server_close()
        report['installed_version'] = info(host)['CFBundleVersion']
        (args.directory / 'result.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
