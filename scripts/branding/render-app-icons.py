#!/usr/bin/env python3
"""Compile Lune's macOS icons with Apple's mask, padding and size variants."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    spec = importlib.util.spec_from_file_location('vectors', Path(__file__).with_name('generate-assets.py'))
    vectors = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vectors)
    data = json.loads((ROOT / 'branding/palettes.json').read_text())
    output = ROOT / 'out/branding'
    for mode in ('light', 'dark'):
        name = f'Lune-{mode}'
        source = output / f'{name}.icon'
        assets = source / 'Assets'
        assets.mkdir(parents=True, exist_ok=True)
        left, right = vectors.paths(data['geometry'])
        # No rounded canvas or transparent perimeter: Apple supplies both.
        artwork = ('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" '
                   'viewBox="0 0 1024 1024"><g transform="translate(17 17) scale(3.3)">'
                   f'<path fill="{data[mode]["left"]}" d="{left}"/>'
                   f'<path fill="{data[mode]["right"]}" d="{right}"/></g></svg>\n')
        (assets / 'lunes.svg').write_text(artwork)
        rgb = [int(data[mode]['ground'][i:i+2], 16) / 255 for i in (1, 3, 5)]
        document = {
            'fill': {'solid': 'extended-srgb:' + ','.join(f'{c:.8f}' for c in rgb) + ',1.00000000'},
            'groups': [{
                'layers': [{'glass': False, 'image-name': 'lunes.svg', 'name': 'Lunes'}],
                'shadow': {'kind': 'neutral', 'opacity': 0},
                'translucency': {'enabled': False, 'value': 0},
            }],
            'supported-platforms': {'squares': ['macOS']},
        }
        (source / 'icon.json').write_text(json.dumps(document, indent=2) + '\n')
        compiled = output / f'{name}-compiled'
        compiled.mkdir(exist_ok=True)
        subprocess.run(['xcrun', 'actool', str(source), '--compile', str(compiled),
                        '--platform', 'macosx', '--minimum-deployment-target', '12.0',
                        '--standalone-icon-behavior', 'all',
                        '--app-icon', name, '--output-partial-info-plist',
                        str(compiled / 'info.plist')], check=True)
        shutil.copyfile(compiled / f'{name}.icns', output / f'app-{mode}.icns')
        iconset = output / f'{name}.iconset'
        if iconset.exists():
            shutil.rmtree(iconset)
        subprocess.run(['iconutil', '-c', 'iconset', str(output / f'app-{mode}.icns'),
                        '-o', str(iconset)], check=True)
        shutil.copyfile(iconset / 'icon_512x512@2x.png', output / f'lune-{mode}.png')
        # Use the identical native app icon in the website's interactive Dock.
        shutil.copyfile(iconset / 'icon_128x128@2x.png',
                        ROOT / f'website/public/assets/lune-dock-{mode}.png')


if __name__ == '__main__':
    main()
