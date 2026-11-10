#!/usr/bin/env python3
"""Serve exact release bytes on loopback for manual native-Mac update acceptance.

Requires Python 3.9+, with no third-party dependencies. Does not launch an app,
edit its profile, publish a feed, or record a test as passed.
"""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

SPARKLE = 'http://www.andymatuschak.org/xml-namespaces/sparkle'
ET.register_namespace('sparkle', SPARKLE)


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def fixture(directory, arch, case):
    """Validate the source feed and archive before changing only its local URL."""
    data = json.loads((directory / 'release.json').read_text())
    offered_arch = 'arm64' if case == 'wrong-architecture' else arch
    if case == 'wrong-architecture' and arch != 'x86_64':
        raise ValueError('Wrong-architecture fixture requires a native Intel test Mac')
    row = data['downloads'][offered_arch]
    name = row['filename']
    if name not in (f"Lune-macos-{offered_arch}.dmg",
                    f"Lune-{data['version']}-macos-{offered_arch}.dmg"):
        # Keep prior release fixtures usable without changing their binaries.
        raise ValueError('Unexpected release artifact name')
    dmg = directory / name
    if dmg.stat().st_size != row['size'] or digest(dmg) != row['sha256']:
        raise ValueError('Release DMG does not match its immutable identity')
    feed_name = f'appcast-{offered_arch}.xml'
    expected = data['assets'][feed_name]
    source = directory / feed_name
    if source.stat().st_size != expected['size'] or digest(source) != expected['sha256']:
        raise ValueError('Release feed differs from its manifest')
    xml = ET.fromstring(source.read_bytes())
    item = xml.find('./channel/item')
    enclosure = item.find('enclosure')
    if (item.findtext(f'{{{SPARKLE}}}version') != data['version']
            or enclosure.get('url') != row['url']
            or enclosure.get('length') != str(row['size'])):
        raise ValueError('Feed does not identify the release DMG')
    if offered_arch == 'arm64' and item.findtext(f'{{{SPARKLE}}}hardwareRequirements') != 'arm64':
        raise ValueError('Apple silicon feed must require arm64 hardware')
    return data, dmg, xml


def make_server(directory, arch, case):
    data, dmg, xml = fixture(directory, arch, case)
    feed_path = f'/mac/appcast-{arch}.xml'
    archive_path = '/' + dmg.name
    payload = b''

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == feed_path:
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            elif self.path == archive_path:
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(dmg.stat().st_size))
                self.end_headers()
                with dmg.open('rb') as stream:
                    shutil.copyfileobj(stream, self.wfile)
            else:
                self.send_error(404)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    base = f'http://127.0.0.1:{server.server_port}/'
    xml.find('./channel/item/enclosure').set('url', base + dmg.name)
    payload = ET.tostring(xml, encoding='utf-8', xml_declaration=True)
    return server, base, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    parser.add_argument('--case', choices=['update', 'wrong-architecture'], default='update')
    args = parser.parse_args()
    server, base, data = make_server(args.directory.resolve(), args.arch, args.case)
    print(f"Local {args.case} fixture for Lune {data['version']}; no public channel is changed.", flush=True)
    print(f'Launch the separate build-2 test app with --custom-update-server-url={base}', flush=True)
    print('Use a disposable --user-data-dir, enable browser updates, and check About.', flush=True)
    print('For wrong-architecture, native Intel must reject the arm64 offer and retain build 2.', flush=True)
    print('Keep this terminal open; press Control-C after quitting the test app.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
