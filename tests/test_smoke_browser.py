"""Ensure artwork comparison tolerates metadata removal, never changed artwork."""
import importlib.util
from pathlib import Path
import struct
import unittest
import zlib

spec = importlib.util.spec_from_file_location('smoke', Path(__file__).parents[1] / 'scripts/smoke-browser.py')
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))


def png(pixel, exif=b'', color=b'\0'):
    header = struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'sRGB', color)
            + (chunk(b'eXIf', exif) if exif else b'')
            + chunk(b'IDAT', zlib.compress(b'\0' + pixel)) + chunk(b'IEND', b''))


class ArtworkTests(unittest.TestCase):
    def test_exif_removal_does_not_change_artwork(self):
        pixel = bytes([16, 53, 79, 255])
        self.assertEqual(smoke.artwork_hash(png(pixel, b'metadata')), smoke.artwork_hash(png(pixel)))

    def test_image_or_color_changes_fail_comparison(self):
        original = smoke.artwork_hash(png(bytes([16, 53, 79, 255])))
        self.assertNotEqual(original, smoke.artwork_hash(png(bytes([83, 134, 191, 255]))))
        self.assertNotEqual(original, smoke.artwork_hash(png(bytes([16, 53, 79, 255]), color=b'\1')))

    def test_svg_changes_fail_comparison(self):
        self.assertNotEqual(smoke.artwork_hash(b'<svg>Lune</svg>'), smoke.artwork_hash(b'<svg>Helium</svg>'))

    def test_truncated_chunk_is_rejected(self):
        with self.assertRaises(ValueError):
            smoke.artwork_hash(png(bytes([16, 53, 79, 255]))[:-1])
