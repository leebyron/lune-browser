import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/release'))
import publish


class ProductionPublicationTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        data = dict(version='26.1109.1', tag='v26.1109.1', source_commit='a'*40,
                    assets={}, downloads={})
        (root/'release.json').write_text(json.dumps(data))
        (root/'SHA256SUMS').write_text('')
        (root/'source.tar.gz').write_bytes(b'fixture')
        (root/'source-assets.json').write_text(json.dumps(dict(
            orchestrator_commit=data['source_commit'], source_kit='source.tar.gz', archives=[])))
        (root/'acceptance.json').write_text('{}')
        (root/'upload-receipt.json').write_text(json.dumps(data))
        args = SimpleNamespace(directory=root, source_checkout=root/'frozen',
            source_directory=root, archives=root, notes_file=root/'notes.md',
            acceptance=root/'acceptance.json', channel='stable', checkout=root/'public')
        return data, args

    def test_upload_stays_unpublished_and_uses_production_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, args = self.fixture(tmp)
            assets = [dict(name=p.name, digest='sha256:'+publish.sha(p)) for p in (
                args.directory/'release.json', args.directory/'SHA256SUMS')]
            with patch('publish.manifest', return_value=data) as manifest, \
                 patch('publish.fresh'), patch('publish.git', return_value='b'*40), \
                 patch('publish.public_source', return_value={'commit': data['source_commit']}), \
                 patch('publish.release', return_value={'assets': assets}), \
                 patch('publish.gh', return_value='[]') as gh:
                publish.upload(args)
            manifest.assert_called_once_with(args.directory, args.source_checkout)
            calls = [c.args for c in gh.call_args_list]
            creation = next(c for c in calls if c[:2] == ('release','create'))
            self.assertIn('--draft', creation)
            self.assertNotIn('--prerelease', creation)
            self.assertFalse(any(c[:2] == ('release','edit') for c in calls))
            receipt = json.loads((args.directory/'upload-receipt.json').read_text())
            self.assertEqual(receipt['source_commit'], data['source_commit'])
            self.assertEqual(receipt['publisher_commit'], 'b'*40)
            self.assertEqual(set(receipt['assets']), {a['name'] for a in assets})
            self.assertNotIn('source.tar.gz', receipt['assets'])
            self.assertEqual(receipt['public_source']['commit'], data['source_commit'])

    def test_inaccessible_public_source_blocks_draft_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, args = self.fixture(tmp)
            with patch('publish.manifest', return_value=data), \
                 patch('publish.public_source', side_effect=ValueError('Public source ref missing')), \
                 patch('publish.gh') as gh:
                with self.assertRaisesRegex(ValueError, 'Public source ref missing'):
                    publish.upload(args)
                gh.assert_not_called()

    def test_public_source_checks_release_and_component_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'manifests').mkdir()
            ref = 'refs/tags/inputs/test/macos'
            lock = dict(repository='https://github.com/leebyron/lune-browser.git',
                        components={'macos': dict(ref=ref, commit='c'*40)})
            (root/'manifests/browser.lock.json').write_text(json.dumps(lock))
            data = dict(tag='v26.1109.2', source_commit='a'*40)
            rows = 'b'*40+'\trefs/tags/v26.1109.2\n'+'a'*40+'\trefs/tags/v26.1109.2^{}\n'+'c'*40+'\t'+ref+'\n'
            with patch('publish.subprocess.check_output', side_effect=['{"private":false}', rows]):
                self.assertEqual(publish.public_source(data, root)['commit'], 'a'*40)
            with patch('publish.subprocess.check_output', side_effect=['{"private":false}', rows.replace('c'*40,'d'*40)]):
                with self.assertRaisesRegex(ValueError, 'ref missing or changed'):
                    publish.public_source(data, root)
            with patch('publish.subprocess.check_output', return_value='{"private":true}'):
                with self.assertRaisesRegex(ValueError, 'not publicly accessible'):
                    publish.public_source(data, root)

    def test_missing_native_acceptance_cannot_publish_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, args = self.fixture(tmp)
            with patch('publish.manifest', return_value=data), \
                 patch('publish.release', return_value={'draft': True, 'prerelease': False, 'assets': []}), \
                 patch('publish.validate_acceptance', side_effect=ValueError('Native Intel required')), \
                 patch('publish.gh') as gh, patch('publish.subprocess.run') as run:
                with self.assertRaisesRegex(ValueError, 'Native Intel'):
                    publish.promote(args)
            gh.assert_not_called()
            run.assert_not_called()

    def test_source_asset_change_blocks_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, args = self.fixture(tmp)
            receipt = dict(data, assets={'source.tar.gz': dict(size=7, sha256='correct')})
            (args.directory/'upload-receipt.json').write_text(json.dumps(receipt))
            with patch('publish.manifest', return_value=data), \
                 patch('publish.release', return_value={'draft': True, 'assets': [
                     dict(name='source.tar.gz', size=7, digest='sha256:changed')]}), \
                 patch('publish.gh') as gh:
                with self.assertRaisesRegex(ValueError, 'Published asset mismatch'):
                    publish.promote(args)
            gh.assert_not_called()

    def test_freshness_failure_keeps_accepted_draft_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, args = self.fixture(tmp)
            def git(root, *argv):
                return {'status': '', 'branch': 'main', 'remote':
                        f'https://github.com/{publish.REPOSITORY}.git'}.get(argv[0], '')
            with patch('publish.manifest', return_value=data), \
                 patch('publish.release', return_value={'draft': True, 'prerelease': False, 'assets': []}), \
                 patch('publish.validate_acceptance'), patch('publish.git', side_effect=git), \
                 patch('publish.subprocess.run'), patch('publish.gh', return_value='[]') as gh, \
                 patch('publish.fresh', side_effect=ValueError('Freshness blocks publication')):
                with self.assertRaisesRegex(ValueError, 'Freshness blocks'):
                    publish.promote(args)
            self.assertFalse(any(c.args[:2] == ('release', 'edit') for c in gh.call_args_list))

    def test_staging_channel_is_rejected(self):
        with patch('sys.argv', ['publish.py','promote','--directory','x','--channel','staging',
                               '--acceptance','x','--checkout','x']):
            with self.assertRaises(SystemExit) as error:
                publish.main()
        self.assertEqual(error.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
