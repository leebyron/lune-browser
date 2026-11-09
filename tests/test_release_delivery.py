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
    def test_both_architectures_and_identical_alias_bytes(self):
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
                self.assertEqual((root/'public'/row['filename']).read_bytes(),(root/'public'/row['alias']).read_bytes())
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



if __name__ == '__main__':
    unittest.main()
