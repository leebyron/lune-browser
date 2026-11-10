import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/release'))
import model
import freshness

class FreshnessTests(unittest.TestCase):
    def test_freshness_distinguishes_lag_ahead_and_unknown(self):
        row = dict(channel='Stable', platform='Mac', version='158.0.8127.18')
        self.assertEqual(freshness.compare('158.0.8127.18', [row])[1], 'current')
        self.assertEqual(freshness.compare('157.0.8127.18', [row])[1], 'behind')
        self.assertEqual(freshness.compare('159.0.0.1', [row])[1], 'ahead')
        with self.assertRaises(ValueError): freshness.compare('158.0.8127.18', [dict(row, platform='Win')])
        with patch('freshness.subprocess.check_output', side_effect=OSError('offline')):
            result = freshness.check('158.0.8127.18')
        self.assertEqual(result['result'], 'unknown')
        self.assertFalse(result['allowed'])


class DeliveryTests(unittest.TestCase):
    def test_one_asset_per_architecture_with_version_specific_urls(self):
        import base64
        import delivery
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); dirs=[]
            for arch in model.ARCHES:
                d=root/arch;d.mkdir();dirs.append(d)
                name=model.filename('26.1109.1',arch);(d/name).write_bytes(arch.encode())
                c=dict(version='26.1109.1',arch=arch,filename=name,signed=True,packaged=True,
                       chromium_version='158.0.8127.18',minimum_system_version='13.0',
                       sha256=model.sha(d/name),size=(d/name).stat().st_size,
                       ed_signature=base64.b64encode(bytes(64)).decode(),
                       orchestrator_commit='a'*40,core_commit='b'*40,platform_commit='c'*40,
                       lock_sha256='d'*64,release_record_sha256='e'*64)
                (d/'candidate.json').write_text(json.dumps(c))
            evidence = dict(version='26.1109.1', source_commit='a'*40, architectures={
                arch: dict(sha256=model.sha(root/arch/model.filename('26.1109.1',arch)),
                    install=True, browse=True, profile_persistence=True, signed_app=True,
                    installed_update=True) for arch in model.ARCHES})
            with patch('delivery.load_record',return_value={}):
                data=delivery.prepare(dirs,root/'public',evidence)
            for arch in model.ARCHES:
                row=data['downloads'][arch]
                self.assertEqual(row['filename'], f'Lune-macos-{arch}.dmg')
                self.assertEqual((root/'public'/row['filename']).read_bytes(), arch.encode())
                self.assertEqual(row['url'], f"{model.DOWNLOADS}/v26.1109.1/{row['filename']}")
                self.assertNotIn('alias', row)
            self.assertEqual(len(list((root/'public').glob('*.dmg'))), 2)
            import publish
            with patch('publish.load_record', return_value={}), patch('publish.git', return_value='a'*40):
                self.assertEqual(publish.manifest(root/'public'), data)
                changed = copy.deepcopy(data)
                changed['assets']['duplicate.dmg'] = changed['assets']['Lune-macos-arm64.dmg']
                (root/'public/release.json').write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'Exactly one DMG'):
                    publish.manifest(root/'public')
            with self.assertRaises(ValueError):delivery.prepare([dirs[0],dirs[0]],root/'bad',evidence)
            with self.assertRaises(ValueError):delivery.prepare(dirs,root/'public',evidence)


class PromotionTests(unittest.TestCase):
    def test_release_lookup_includes_drafts_on_later_pages(self):
        import publish
        draft = dict(tag_name='v26.1109.1', draft=True, assets=[])
        pages = [[dict(tag_name='build-2', draft=False)], [draft]]
        with patch('publish.gh', return_value=json.dumps(pages)) as api:
            self.assertEqual(publish.release('v26.1109.1'), draft)
        api.assert_called_once_with('api', f'repos/{model.REPOSITORY}/releases',
                                    '--paginate', '--slurp')

    def test_release_lookup_rejects_missing_or_ambiguous_tags(self):
        import publish
        row = dict(tag_name='v26.1109.1', draft=True)
        for pages in [[], [[row], [row]]]:
            with self.subTest(pages=pages), patch('publish.gh', return_value=json.dumps(pages)):
                with self.assertRaisesRegex(ValueError, 'exactly one visible release'):
                    publish.release('v26.1109.1')

    def test_native_acceptance_is_required_only_for_stable(self):
        data = dict(version='26.1109.1', source_commit='a' * 40,
                    downloads={arch: {'sha256': arch} for arch in model.ARCHES})
        acceptance = dict(version=data['version'], source_commit=data['source_commit'],
                          architectures={arch: dict(sha256=arch, install=True, browse=True,
                          profile_persistence=True, signed_app=True, installed_update=True)
                          for arch in model.ARCHES})
        model.validate_acceptance(data, acceptance, 'staging')
        with self.assertRaisesRegex(ValueError, 'Native Intel'):
            model.validate_acceptance(data, acceptance, 'stable')
        acceptance['architectures']['x86_64'].update(native_hardware=True,
            devices=['Intel test Mac'], owner_confirmation='Accepted by owner')
        model.validate_acceptance(data, acceptance, 'stable')
        for field, value in [('sha256', 'different'), ('installed_update', False)]:
            changed = copy.deepcopy(acceptance)
            changed['architectures']['arm64'][field] = value
            with self.assertRaises(ValueError):
                model.validate_acceptance(data, changed, 'stable')


    def test_owner_can_defer_native_intel_without_waiving_local_checks(self):
        data = dict(version='26.1109.1', source_commit='a' * 40,
                    downloads={arch: {'sha256': arch} for arch in model.ARCHES})
        acceptance = dict(version=data['version'], source_commit=data['source_commit'],
            architectures={arch: dict(sha256=arch, install=True, browse=True,
                profile_persistence=True, signed_app=True, installed_update=True,
                native_hardware=False) for arch in model.ARCHES},
            native_intel_deferral=dict(owner_approved=True, testing_pending=True,
                owner_instruction='Publish now; fix any problems in a new version.'))
        model.validate_acceptance(data, acceptance, 'stable')
        for field, value in [('owner_approved', False), ('testing_pending', False),
                             ('owner_instruction', ''), ('owner_instruction', True)]:
            changed = copy.deepcopy(acceptance)
            changed['native_intel_deferral'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                model.validate_acceptance(data, changed, 'stable')
        for arch in model.ARCHES:
            for field, value in [('sha256', 'wrong'), ('signed_app', False),
                                 ('installed_update', False), ('browse', False),
                                 ('install', False), ('profile_persistence', False)]:
                changed = copy.deepcopy(acceptance)
                changed['architectures'][arch][field] = value
                with self.subTest(arch=arch, field=field), self.assertRaises(ValueError):
                    model.validate_acceptance(data, changed, 'stable')


class ManualFixtureTests(unittest.TestCase):
    def prepare(self, root):
        import base64
        import appcast
        data = dict(version='26.1109.1', downloads={}, assets={})
        for arch in model.ARCHES:
            name = model.filename(data['version'], arch)
            dmg = root / name
            dmg.write_bytes(arch.encode())
            row = dict(filename=name, size=dmg.stat().st_size, sha256=model.sha(dmg),
                       url=f'{model.DOWNLOADS}/v{data["version"]}/{name}')
            candidate = dict(row, arch=arch, version=data['version'],
                             chromium_version='158.0.8127.18',
                             minimum_system_version='13.0',
                             ed_signature=base64.b64encode(bytes(64)).decode())
            feed = root / f'appcast-{arch}.xml'
            feed.write_bytes(appcast.make_feed(candidate, row['url']))
            data['downloads'][arch] = row
            data['assets'][feed.name] = dict(size=feed.stat().st_size, sha256=model.sha(feed))
        (root / 'release.json').write_text(json.dumps(data))
        return data

    def test_local_feed_preserves_signature_and_serves_only_selected_assets(self):
        import manual_update_fixture as fixture
        import threading
        from urllib.request import build_opener, ProxyHandler
        from urllib.error import HTTPError
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.prepare(root)
            for case, offered in [('update', 'x86_64'), ('wrong-architecture', 'arm64')]:
                with self.subTest(case=case):
                    server, base, _ = fixture.make_server(root, 'x86_64', case)
                    thread = threading.Thread(target=server.serve_forever)
                    thread.start()
                    opener = build_opener(ProxyHandler({}))
                    try:
                        with opener.open(base + 'mac/appcast-x86_64.xml') as response:
                            xml = ET.fromstring(response.read())
                        enclosure = xml.find('./channel/item/enclosure')
                        original = ET.fromstring((root / f'appcast-{offered}.xml').read_bytes())
                        expected = original.find('./channel/item/enclosure')
                        self.assertEqual(enclosure.get(f'{{{fixture.SPARKLE}}}edSignature'),
                                         expected.get(f'{{{fixture.SPARKLE}}}edSignature'))
                        self.assertEqual(xml.findtext(f'./channel/item/{{{fixture.SPARKLE}}}hardwareRequirements'),
                                         'arm64' if offered == 'arm64' else None)
                        with opener.open(enclosure.get('url')) as response:
                            self.assertEqual(response.read(), offered.encode())
                        for forbidden in ('release.json', '../release.json', ''):
                            with self.assertRaises(HTTPError) as error:
                                opener.open(base + forbidden)
                            self.assertEqual(error.exception.code, 404)
                    finally:
                        server.shutdown()
                        thread.join()
                        server.server_close()
            self.assertEqual(json.loads((root / 'release.json').read_text()), data)

    def test_changed_archive_or_feed_blocks_serving(self):
        import manual_update_fixture as fixture
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for changed in ('Lune-macos-x86_64.dmg', 'appcast-x86_64.xml'):
                self.prepare(root)
                (root / changed).write_bytes(b'changed')
                with self.assertRaises(ValueError):
                    fixture.make_server(root, 'x86_64', 'update')


if __name__ == '__main__':
    unittest.main()
