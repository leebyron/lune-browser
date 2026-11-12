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
        extent = data['geometry']['outer_radius'] + data['geometry']['center_offset']
        scale = data['app_icon']['mark_width'] / (2 * extent)
        inset = 512 - 150 * scale
        layers = []
        # Separate vector layers let Apple shade each floating glass piece.
        # Do not bake bevels, glows, or shadows into the artwork.
        for key, path in zip(('left', 'right'), vectors.paths(data['geometry'])):
            asset = f'lune-{key}.svg'
            artwork = ('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" '
                       f'viewBox="0 0 1024 1024"><g transform="translate({inset:g} {inset:g}) scale({scale:g})">'
                       f'<path fill="{data[mode][key]}" d="{path}"/></g></svg>\n')
            (assets / asset).write_text(artwork)
            layers.append({'glass': True, 'image-name': asset, 'name': f'{key.title()} lune'})
        rgb = [int(data[mode]['ground'][i:i+2], 16) / 255 for i in (1, 3, 5)]
        material = data['app_icon']['material']
        def group(layers, name):
            return {
                'name': name,
                'layers': layers,
                'lighting': 'individual',
                'shadow': {'kind': material['shadow_kind'], 'opacity': material['shadow_opacity']},
                'translucency': {'enabled': True, 'value': material['translucency']},
                'refractivity': {'enabled': True, 'strength': material['refraction_strength'],
                                'depth': material['refraction_depth']},
                'specular': material['specular'],
            }
        groups = ([group([layer], layer['name']) for layer in layers]
                  if material['separate_groups'] else [group(layers, 'Lunes')])
        document = {
            'features': ['refractivity', 'specular-location'],
            'fill': {'solid': 'extended-srgb:' + ','.join(f'{c:.8f}' for c in rgb) + ',1.00000000'},
            'groups': groups,
            'supported-platforms': {'squares': ['macOS']},
        }
        if mode == 'dark':
            # Prevent Dark appearance's automatic neutral background replacement.
            fill = document.pop('fill')
            document['fill-specializations'] = [{'value': fill}, {'appearance': 'dark', 'value': fill}]
        (source / 'icon.json').write_text(json.dumps(document, indent=2) + '\n')
        compiled = output / f'{name}-compiled'
        compiled.mkdir(exist_ok=True)
        subprocess.run(['xcrun', 'actool', str(source), '--compile', str(compiled),
                        '--platform', 'macosx', '--minimum-deployment-target', '13.0',
                        '--standalone-icon-behavior', 'all',
                        '--app-icon', name, '--output-partial-info-plist',
                        str(compiled / 'info.plist')], check=True)
        shutil.copyfile(compiled / f'{name}.icns', output / f'app-{mode}.icns')
        iconset = output / f'{name}.iconset'
        if iconset.exists():
            shutil.rmtree(iconset)
        subprocess.run(['iconutil', '-c', 'iconset', str(output / f'app-{mode}.icns'),
                        '-o', str(iconset)], check=True)
        # Standalone ICNS uses the older compiler rendering. Use the current
        # renderer for both appearances, retaining actool's legacy canvas.
        developer = Path(subprocess.check_output(['xcode-select', '-p'], text=True).strip())
        ictool = developer.parent / 'Applications/Icon Composer.app/Contents/Executables/ictool'
        cache = ROOT / '.work/branding/module-cache'
        cache.mkdir(parents=True, exist_ok=True)
        for image in sorted(iconset.glob('*.png')):
            # Render at each physical size so highlights scale natively.
            size = int(image.stem.split('x')[1].split('@')[0])
            if '@2x' in image.stem:
                size *= 2
            rendered = output / f'{mode}-rendition.png'
            subprocess.run([str(ictool), str(source), '--export-image', '--output-file', str(rendered),
                            '--platform', 'macOS', '--rendition', 'Dark' if mode == 'dark' else 'Default', '--width', str(size),
                            '--height', str(size), '--scale', '1', '--design-generation', str(data['app_icon']['design_generation'])], check=True)
            subprocess.run(['swift', '-module-cache-path', str(cache),
                            str(ROOT / 'scripts/branding/package-app-icon.swift'),
                            str(image), str(rendered)], check=True)
        subprocess.run(['iconutil', '-c', 'icns', str(iconset),
                        '-o', str(output / f'app-{mode}.icns')], check=True)
        shutil.copyfile(iconset / 'icon_512x512@2x.png', output / f'lune-{mode}.png')
        # Use the identical native app icon in the website's interactive Dock.
        shutil.copyfile(iconset / 'icon_128x128@2x.png',
                        ROOT / f'website/public/assets/lune-dock-{mode}.png')


if __name__ == '__main__':
    main()
