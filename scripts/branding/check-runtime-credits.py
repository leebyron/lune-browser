#!/usr/bin/env python3
"""Verify packaged translations in an isolated, localized macOS Lune process.

Requires the matching ChromeDriver and prepared source. No system language or
normal browser profile is changed; external DNS and real Keychain use are disabled.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import tempfile
import time
from urllib.request import Request, build_opener, ProxyHandler
import xml.etree.ElementTree as ET


# GRIT fingerprints for the deliberately unchanged Helium partner messages.
PARTNER_IDS = {'title': '6479851256956179247', 'tooltip': '3911753348406844666'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--locale', default='fr', choices=['fr', 'de'])
    args = parser.parse_args()
    output = args.output.resolve()
    binary = output / 'Lune.app/Contents/MacOS/Lune'
    driver_binary = output / 'chromedriver'
    version = dict(line.split('=', 1) for line in
                   (args.source / 'chrome/VERSION').read_text().splitlines() if '=' in line)
    expected_version = '.'.join(version[key] for key in ('MAJOR', 'MINOR', 'BUILD', 'PATCH'))
    catalog = ET.parse(args.source /
                       f'chrome/app/resources/generated_resources_{args.locale}.xtb').getroot()
    expected = {}
    for key, fingerprint in PARTNER_IDS.items():
        translation = catalog.find(f"translation[@id='{fingerprint}']")
        if translation is None:
            raise RuntimeError(f'Missing prepared translation for {key}')
        expected[key] = ''.join(translation.itertext())
        if 'Helium' not in expected[key] or 'Lune' in expected[key]:
            raise RuntimeError(f'Prepared attribution is incorrect: {expected[key]}')
    report = {'locale_requested': args.locale, 'test_host_architecture': platform.machine(),
              'expected_version': expected_version, 'expected_translations': expected,
              'release_validated': False}
    opener = build_opener(ProxyHandler({}))

    def request(port, method, path, data=None, timeout=30):
        req = Request(f'http://127.0.0.1:{port}' + path, method=method,
                      data=None if data is None else json.dumps(data).encode(),
                      headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=timeout) as response:
            return json.load(response)['value']

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='lune-localized-test-') as profile:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME', 'PATH', 'TMPDIR')
               if key in os.environ}
        with args.report.with_suffix('.browser.log').open('w') as browser_log, \
                args.report.with_suffix('.driver.log').open('w') as driver_log:
            # Cocoa reads this pair directly from argv. ChromeDriver normalizes
            # switches, so start the browser ourselves and attach via loopback.
            browser = subprocess.Popen([
                str(binary), '-AppleLanguages', f'({args.locale})',
                '--headless=new', '--no-first-run', '--no-default-browser-check',
                '--enable-automation', '--test-type=webdriver',
                '--password-store=basic', '--use-mock-keychain',
                '--disable-background-networking', '--remote-debugging-port=0',
                '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',
                f'--user-data-dir={profile}'], env=env,
                stdout=browser_log, stderr=subprocess.STDOUT)
            driver = None
            session = None
            try:
                active_port = Path(profile) / 'DevToolsActivePort'
                for _ in range(120):
                    if browser.poll() is not None:
                        raise RuntimeError('Browser exited during startup')
                    if active_port.exists():
                        break
                    time.sleep(0.5)
                else:
                    raise RuntimeError('No browser debug port')
                debug_port = int(active_port.read_text().splitlines()[0])
                driver = subprocess.Popen([
                    str(driver_binary), f'--port={port}', '--allowed-ips=127.0.0.1'],
                    env=env, stdout=driver_log, stderr=subprocess.STDOUT)
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    if driver.poll() is not None:
                        raise RuntimeError('ChromeDriver exited during startup')
                    try:
                        if request(port, 'GET', '/status', timeout=2)['ready']:
                            break
                    except OSError:
                        pass
                    time.sleep(0.5)
                else:
                    raise RuntimeError('No ChromeDriver connection')
                value = request(port, 'POST', '/session', {'capabilities': {'alwaysMatch': {
                    'pageLoadStrategy': 'none',
                    'goog:chromeOptions': {'debuggerAddress': f'127.0.0.1:{debug_port}'}}}})
                session = '/session/' + value['sessionId']
                report['browser_version'] = value['capabilities']['browserVersion']
                if report['browser_version'] != expected_version:
                    raise RuntimeError('Browser version does not match prepared source')
                report['app_architecture'] = subprocess.check_output(
                    ['/usr/bin/lipo', '-archs', binary], text=True).strip()
                request(port, 'POST', session + '/url', {'url': 'chrome://setup/'})
                for _ in range(60):
                    result = request(port, 'POST', session + '/execute/sync', {
                        'script': '''return globalThis.loadTimeData?.data?.partnerTitle &&
                            document.querySelector('#upstream-credit') ? {
                            locale: loadTimeData.getString('language'),
                            title: loadTimeData.getString('partnerTitle'),
                            tooltip: loadTimeData.getString('partnerTooltip'),
                            welcome: loadTimeData.getString('welcomeGreeting'),
                            credit: document.querySelector('#upstream-credit').textContent.trim()
                        } : null;''', 'args': []})
                    if result:
                        break
                    time.sleep(0.5)
                else:
                    raise RuntimeError('Onboarding did not render localized strings and attribution')
                report['onboarding'] = result
                if result['locale'] != args.locale:
                    raise RuntimeError(f'Browser did not select {args.locale}: {result}')
                if any(result[key] != text for key, text in expected.items()):
                    raise RuntimeError(f'Packaged translations differ from prepared source: {result}')
                for key in ('title', 'tooltip', 'credit'):
                    if 'Helium' not in result[key] or 'Lune' in result[key]:
                        raise RuntimeError(f'Incorrect upstream attribution: {result}')
                if 'Lune' not in result['welcome']:
                    raise RuntimeError(f'Localized product greeting lost Lune branding: {result}')
                report['passed'] = True
            except Exception as error:
                report.update(passed=False, error=str(error))
                raise
            finally:
                if session:
                    try:
                        request(port, 'DELETE', session, timeout=10)
                    except Exception:
                        pass
                for process in (driver, browser):
                    if process is not None:
                        process.terminate()
                        try:
                            process.wait(timeout=15)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
