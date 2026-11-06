"""Release failures must never produce an offer for the wrong or changed artifact."""
import base64
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('appcast', Path(__file__).resolve().parents[1] / 'scripts/release/appcast.py')
appcast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(appcast)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'archive.dmg'
        self.path.write_bytes(b'fixture archive')
        self.candidate = dict(signed=True, packaged=True, arch='arm64', build=2,
                              chromium_version='158.0.8127.18',
                              filename='Lune-158.0.8127.18-2-macos-arm64.dmg',
                              minimum_system_version='13.0', size=self.path.stat().st_size,
                              sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),
                              ed_signature=base64.b64encode(bytes(64)).decode())

    def test_changed_bytes_cannot_enter_feed(self):
        appcast.validate_candidate(self.candidate, self.path)
        self.path.write_bytes(b'different bytes')
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            appcast.validate_candidate(self.candidate, self.path)

    def test_incomplete_release_is_rejected(self):
        for field in ('signed', 'packaged'):
            candidate = copy.deepcopy(self.candidate)
            candidate[field] = False
            with self.assertRaises(ValueError):
                appcast.validate_candidate(candidate, self.path)

    def test_wrong_architecture_asset_is_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['arch'] = 'x86_64'
        with self.assertRaisesRegex(ValueError, 'architecture'):
            appcast.validate_candidate(candidate, self.path)

    def test_feed_version_key_and_platform_are_explicit(self):
        c = self.candidate
        url = 'https://github.com/leebyron/lune-downloads/releases/download/build-2/' + c['filename']
        xml = ET.fromstring(appcast.make_feed(c, url))
        item = xml.find('channel/item')
        self.assertEqual(item.find(f'{{{appcast.SPARKLE}}}version').text, '2')
        self.assertEqual(item.find(f'{{{appcast.SPARKLE}}}hardwareRequirements').text, 'arm64')
        self.assertEqual(item.find('enclosure').get(f'{{{appcast.SPARKLE}}}edSignature'), c['ed_signature'])
        for bad in ('http://example.org/' + c['filename'], 'https://example.org/latest.dmg', url + '?token=secret'):
            with self.assertRaises(ValueError):
                appcast.make_feed(c, bad)


if __name__ == '__main__':
    unittest.main()
