#!/usr/bin/env python3
"""Generate architecture-specific appcasts from signed, notarized DMG evidence.

Only generates local output. Publishing immutable downloads and checking their
public readback must precede promotion of these feeds.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

SPARKLE = 'http://www.andymatuschak.org/xml-namespaces/sparkle'
ET.register_namespace('sparkle', SPARKLE)


def validate_candidate(candidate, path):
    if not candidate.get('signed') or not candidate.get('packaged'):
        raise ValueError('Only signed and notarized packages may enter a feed')
    if candidate['arch'] not in ('arm64', 'x86_64'):
        raise ValueError('Unsupported architecture')
    if type(candidate['build']) is not int or candidate['build'] < 1:
        raise ValueError('Invalid release build number')
    expected = f"Lune-{candidate['chromium_version']}-{candidate['build']}-macos-{candidate['arch']}.dmg"
    if candidate['filename'] != expected or Path(expected).name != expected:
        raise ValueError('Artifact name does not match its release/architecture')
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', candidate['minimum_system_version']):
        raise ValueError('Invalid minimum macOS version')
    if len(base64.b64decode(candidate['ed_signature'], validate=True)) != 64:
        raise ValueError('Invalid signature encoding')
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != candidate['sha256'] or path.stat().st_size != candidate['size']:
        raise ValueError('Final signed artifact bytes changed')


def make_feed(candidate, url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.username or parsed.password or not parsed.netloc:
        raise ValueError('An HTTPS download URL is required')
    if parsed.path.rsplit('/', 1)[-1] != candidate['filename'] or parsed.query or parsed.fragment:
        raise ValueError('Use an immutable URL for the exact release asset')
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = f"Lune for macOS ({candidate['arch']})"
    ET.SubElement(channel, 'link').text = 'https://lune.computer'
    ET.SubElement(channel, 'description').text = 'Lune browser updates'
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = f"Lune {candidate['chromium_version']} (build {candidate['build']})"
    ET.SubElement(item, f'{{{SPARKLE}}}version').text = str(candidate['build'])
    ET.SubElement(item, f'{{{SPARKLE}}}shortVersionString').text = candidate['chromium_version']
    ET.SubElement(item, f'{{{SPARKLE}}}minimumSystemVersion').text = candidate['minimum_system_version']
    if candidate['arch'] == 'arm64':
        ET.SubElement(item, f'{{{SPARKLE}}}hardwareRequirements').text = 'arm64'
    ET.SubElement(item, 'enclosure', {
        'url': url, 'length': str(candidate['size']), 'type': 'application/octet-stream',
        f'{{{SPARKLE}}}edSignature': candidate['ed_signature'],
    })
    ET.indent(rss)
    return ET.tostring(rss, encoding='utf-8', xml_declaration=True) + b'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--download-url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    candidate = json.loads((args.directory / 'candidate.json').read_text())
    validate_candidate(candidate, args.directory / candidate['filename'])
    if args.output.exists():
        raise ValueError('Output exists; do not overwrite a promoted feed')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(make_feed(candidate, args.download_url))


if __name__ == '__main__':
    main()
