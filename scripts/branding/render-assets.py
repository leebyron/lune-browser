#!/usr/bin/env python3
"""Regenerate shared vectors, macOS iconsets, browser PNGs and website fallbacks."""
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    output = ROOT / 'out/branding'
    cache = ROOT / '.work/branding/module-cache'
    cache.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, 'scripts/branding/generate-assets.py'], cwd=ROOT, check=True)
    subprocess.run(['swift', '-module-cache-path', str(cache),
                    'scripts/branding/render-icon.swift'], cwd=ROOT, check=True)
    for mode in ('light', 'dark'):
        subprocess.run(['iconutil', '-c', 'icns', str(output / f'Lune-{mode}.iconset'),
                        '-o', str(output / f'app-{mode}.icns')], check=True)
    sizes = (16, 32, 48, 64, 128, 256)
    images = [(output / f'internal/product_logo_{size}.png').read_bytes() for size in sizes]
    offset = 6 + 16 * len(images)
    directory = []
    for size, image in zip(sizes, images):
        directory.append(struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0,
                                     1, 32, len(image), offset))
        offset += len(image)
    website = ROOT / 'website/public'
    (website / 'favicon.ico').write_bytes(struct.pack('<HHH', 0, 1, len(images))
                                        + b''.join(directory) + b''.join(images))
    shutil.copyfile(output / 'internal/product_logo_32.png', website / 'favicon-32.png')
    shutil.copyfile(output / 'apple-touch-icon.png', website / 'apple-touch-icon.png')


if __name__ == '__main__':
    main()
