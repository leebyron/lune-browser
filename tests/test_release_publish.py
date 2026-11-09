"""Exercise publication failure boundaries without contacting GitHub."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/release'))
import model
import publish


class PublicationBoundaryTests(unittest.TestCase):
    def inputs(self, root):
        assets = {'source-kit.tar.gz': {'sha256': 'a' * 64, 'size': 12}}
        data = dict(version='26.1109.1', tag='v26.1109.1', source_commit='b' * 40,
                    chromium_version='158.0.8127.18', assets=assets,
                    downloads={arch: {'sha256': arch} for arch in model.ARCHES})
        receipt = dict(version=data['version'], source_commit=data['source_commit'], assets=assets)
        (root / 'upload-receipt.json').write_text(json.dumps(receipt))
        acceptance = dict(version=data['version'], source_commit=data['source_commit'],
            architectures={arch: dict(sha256=arch, install=True, browse=True,
                profile_persistence=True, signed_app=True, installed_update=True,
                native_hardware=True, devices=['synthetic test Mac'],
                owner_confirmation='synthetic test fixture') for arch in model.ARCHES})
        acceptance_file = root / 'acceptance.json'
        acceptance_file.write_text(json.dumps(acceptance))
        remote = dict(draft=True, prerelease=False, assets=[dict(name=name,
            digest='sha256:' + row['sha256'], size=row['size']) for name, row in assets.items()])
        args = SimpleNamespace(directory=root, source_checkout=root / 'source',
                               acceptance=acceptance_file, checkout=root / 'public', channel='stable')
        return args, data, remote, acceptance

    def test_unaccepted_native_intel_never_reaches_public_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, data, remote, acceptance = self.inputs(Path(tmp))
            acceptance['architectures']['x86_64']['native_hardware'] = False
            args.acceptance.write_text(json.dumps(acceptance))
            with patch('publish.manifest', return_value=data), patch('publish.release', return_value=remote), \
                    patch('publish.gh') as github, patch('publish.subprocess.run') as command:
                with self.assertRaisesRegex(ValueError, 'Native Intel'):
                    publish.promote(args)
                github.assert_not_called()
                command.assert_not_called()
            self.assertFalse(args.checkout.exists())

    def test_changed_uploaded_source_prevents_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, data, remote, _ = self.inputs(Path(tmp))
            # Source uploads belong to the receipt, even when absent from the
            # binary/feed manifest. A changed source archive must still block.
            data = copy.deepcopy(data)
            data['assets'] = {}
            remote['assets'][0]['digest'] = 'sha256:' + 'c' * 64
            with patch('publish.manifest', return_value=data), patch('publish.release', return_value=remote), \
                    patch('publish.gh') as github, patch('publish.subprocess.run') as command:
                with self.assertRaisesRegex(ValueError, 'asset mismatch'):
                    publish.promote(args)
                github.assert_not_called()
                command.assert_not_called()
            self.assertFalse(args.checkout.exists())

    def test_unknown_chromium_freshness_keeps_draft_and_existing_feed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args, data, remote, _ = self.inputs(root)
            feed = args.checkout / 'updates/stable/mac/appcast-arm64.xml'
            feed.parent.mkdir(parents=True)
            feed.write_bytes(b'last good feed')
            def git(repo, *arguments):
                return {('status', '--porcelain'): '', ('branch', '--show-current'): 'main',
                        ('remote', 'get-url', 'origin'): f'https://github.com/{model.REPOSITORY}.git'}[arguments]
            with patch('publish.manifest', return_value=data), patch('publish.release', return_value=remote), \
                    patch('publish.releases', return_value=[]), patch('publish.git', side_effect=git), \
                    patch('publish.check', return_value=dict(allowed=False, result='unknown')), \
                    patch('publish.gh') as github, patch('publish.subprocess.run') as command:
                with self.assertRaisesRegex(ValueError, 'Freshness blocks production-publication'):
                    publish.promote(args)
                github.assert_not_called()
                command.assert_called_once_with(['git', '-C', args.checkout.resolve(), 'pull', '--ff-only', 'origin', 'main'], check=True)
            self.assertEqual(feed.read_bytes(), b'last good feed')
            reports = list(root.glob('freshness-production-publication-*.json'))
            self.assertEqual(len(reports), 1)
            self.assertEqual(json.loads(reports[0].read_text())['result'], 'unknown')


if __name__ == '__main__':
    unittest.main()
