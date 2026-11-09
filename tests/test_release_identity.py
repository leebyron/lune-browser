from datetime import date
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/release'))
import model
import appcast


class ReleaseIdentityTests(unittest.TestCase):
    def test_calendar_and_numeric_update_order(self):
        self.assertEqual(model.version_parts('26.1109.1'), (date(2026, 11, 9), 1))
        versions = ['2', '26.0101.1', '26.1109.2', '26.1109.10', '27.0101.1']
        self.assertEqual(sorted(versions, key=model.version_key), versions)
        for bad in ['26.0230.1', '26.1109.0', '26.1109.01', '26.119.1', '26.1109.1-beta']:
            with self.assertRaises(ValueError): model.version_parts(bad)

    def test_date_version_feed_uses_only_exact_github_asset(self):
        c = dict(version='26.1109.1', arch='arm64', chromium_version='158.0.8127.18',
                 filename=model.filename('26.1109.1', 'arm64'), size=42, ed_signature='fixture',
                 minimum_system_version='13.0')
        url = f"{model.DOWNLOADS}/v{c['version']}/{c['filename']}"
        xml = appcast.make_feed(c, url).decode()
        self.assertIn('<sparkle:version>26.1109.1</sparkle:version>', xml)
        self.assertIn('<sparkle:shortVersionString>26.1109.1</sparkle:shortVersionString>', xml)
        for bad in [f"{model.LATEST}/{c['filename']}", url.replace('/v26.1109.1/', '/v26.1108.1/'),
                    url.replace('leebyron/lune-downloads', 'someone/else')]:
            with self.assertRaises(ValueError): appcast.make_feed(c, bad)

    def test_frozen_release_input_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for name in ('manifests/browser.lock.json', 'config/product.json', 'config/release-recipe.json'):
                p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text('{}')
                files[name] = model.sha(p)
            record = dict(schema_version=1, version='26.1109.1', date='2026-11-09', sequence=1,
                          timezone='America/Los_Angeles', architectures=list(model.ARCHES), tag='v26.1109.1', files=files)
            path = root / 'manifests/releases/26.1109.1.json'; path.parent.mkdir(); path.write_text(json.dumps(record))
            with patch('model.git', return_value=''):
                model.load_record('26.1109.1', root)
                (root / 'config/product.json').write_text('{"changed":true}')
                with self.assertRaisesRegex(ValueError, 'input changed'):
                    model.load_record('26.1109.1', root)


class AllocationTests(unittest.TestCase):
    def test_serialized_allocation_rejects_reuse_backdating_and_skips(self):
        from reserve import check_allocation
        check_allocation('26.1109.1', set())
        check_allocation('26.1109.2', {'26.1109.1'})
        check_allocation('27.0101.1', {'26.1109.2'})
        for version in ('26.1109.1', '26.1108.1', '26.1109.3', '26.1110.2'):
            with self.assertRaises(ValueError):
                check_allocation(version, {'26.1109.1'})


class SourceInventoryTests(unittest.TestCase):
    def test_inventory_tracks_sources_and_symlinks_but_excludes_outputs(self):
        from prepare import inventory
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'source.cc').write_text('source')
            (root / 'alias.cc').symlink_to('source.cc')
            (root / 'out').mkdir()
            (root / 'out/generated.cc').write_text('generated')
            files, links = inventory(root)
            self.assertEqual(files, {'source.cc': model.sha(root / 'source.cc')})
            self.assertEqual(links, {'alias.cc': 'source.cc'})


if __name__ == '__main__':
    unittest.main()
