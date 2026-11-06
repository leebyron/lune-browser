#!/usr/bin/env python3
"""Check Lune logo coverage against upstream and the prepared Chromium source."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import re
import xml.etree.ElementTree as ET


def mappings(path):
    return dict(line.split()[::-1] for line in path.read_text().splitlines()
                if line.strip() and not line.lstrip().startswith('#'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('platform', type=Path)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    resources = args.platform / 'resources'
    upstream = mappings(args.platform / 'helium-chromium/resources/helium_resources.txt')
    lune = mappings(resources / 'lune_resources.txt')
    required = {dest for dest, asset in upstream.items()
                if asset.startswith(('branding/', 'generated/product_icon/'))}
    required |= {'components/helium_onboarding/public/favicon.png',
                 'components/helium_onboarding/public/lune.svg'}
    missing = required - lune.keys()
    if missing:
        raise SystemExit(f'Upstream logo destinations lack Lune overrides: {sorted(missing)}')
    hashes = {}
    for dest, asset in lune.items():
        if not asset.startswith('lune/'):
            raise SystemExit(f'Unexpected Lune asset source: {asset}')
        expected = (resources / asset).read_bytes()
        if (args.source / dest).read_bytes() != expected:
            raise SystemExit(f'Prepared resource differs from Lune input: {dest}')
        hashes[dest] = hashlib.sha256(expected).hexdigest()
    onboarding = args.source / 'components/helium_onboarding/src'
    for page in onboarding.rglob('*.svelte'):
        if any(token in page.read_text() for token in ('HeliumLogo', 'browserIcons.helium')):
            raise SystemExit(f'Embedded upstream browser logo remains: {page}')
    mono = ET.parse(resources / 'lune/product_logo_mono.svg').getroot()
    webui = (args.source / 'ui/webui/resources/cr_elements/icons.html.ts').read_text()
    paths = re.findall(r'<g id="chrome-product" viewBox="0 0 300 300">\s*<path d="([^"]+)"', webui)
    if len(paths) != 2 or any(path != mono[0].get('d') for path in paths):
        raise SystemExit('Shared WebUI browser icons do not match the Lune monochrome mark')
    for name in ('app-Info.plist', 'helper-alerts-Info.plist'):
        info = plistlib.loads((args.source / 'chrome/app' / name).read_bytes())
        if 'CFBundleIconName' in info or info.get('CFBundleIconFile') != 'app.icns':
            raise SystemExit(f'Unexpected icon selection in {name}')
    if '"chrome_asset_catalog"' in (args.source / 'chrome/BUILD.gn').read_text():
        raise SystemExit('Upstream macOS icon catalog is still a bundle input')
    print(json.dumps({'passed': True, 'resource_count': len(hashes),
                      'resources': hashes, 'shared_webui_icon_count': len(paths),
                      'runtime_verified': False}, indent=2))


if __name__ == '__main__':
    main()
