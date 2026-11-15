"""Check profile storage isolation, restart persistence and lifecycle cleanup."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
spec = importlib.util.spec_from_file_location('browser_test_profiles',
                                            SCRIPTS / 'browser_test_profiles.py')
profiles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profiles)


class BrowserProfileTests(unittest.TestCase):
    def tearDown(self):
        profiles.cleanup_profiles()

    def test_macos_ignores_external_temp_environment(self):
        with patch.object(profiles.sys, 'platform', 'darwin'), \
                patch.dict(os.environ, {'TMPDIR': '/Volumes/BuildDisk/tmp'}), \
                patch.object(profiles.tempfile, 'TemporaryDirectory') as create:
            profiles.temporary_profile('lune-onboarding-')
        create.assert_called_once_with(prefix='lune-onboarding-', dir=Path('/private/tmp'))

    def test_profiles_are_unique_and_keep_state_until_cleanup(self):
        first = profiles.new_profile('lune-restart-')
        second = profiles.new_profile('lune-restart-')
        self.assertNotEqual(first, second)
        self.assertEqual(first.stat().st_mode & 0o777, 0o700)
        (first / 'Preferences').write_text('persisted')
        self.assertEqual((first / 'Preferences').read_text(), 'persisted')
        profiles.cleanup_profiles()
        self.assertFalse(first.exists())
        self.assertFalse(second.exists())

    def test_context_cleans_up_after_failure(self):
        with self.assertRaises(RuntimeError):
            with profiles.temporary_profile() as directory:
                path = Path(directory)
                self.assertTrue(path.is_dir())
                raise RuntimeError('test failed')
        self.assertFalse(path.exists())

    def test_process_exit_removes_profile_but_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as evidence:
            marker = Path(evidence) / 'report.json'
            marker.write_text('retained')
            code = ('from browser_test_profiles import new_profile; '
                    'p = new_profile(); (p / "Preferences").write_text("persisted"); '
                    'print(p, flush=True)')
            result = subprocess.run([sys.executable, '-c', code], check=True,
                                    capture_output=True, text=True,
                                    env=dict(os.environ, PYTHONPATH=str(SCRIPTS)))
            path = Path(result.stdout.strip())
            self.assertFalse(path.exists())
            self.assertEqual(marker.read_text(), 'retained')

    def test_existing_explicit_cleanup_is_safe(self):
        path = profiles.new_profile()
        shutil.rmtree(path)
        profiles.cleanup_profiles()

    def test_prefix_cannot_redirect_the_profile(self):
        for prefix in ('/Volumes/BuildDisk/profile-', '../profile-', '.', '..'):
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                profiles.new_profile(prefix)

    def test_release_sessions_reject_external_profile_locations_before_launch(self):
        with patch.object(profiles.sys, 'platform', 'darwin'):
            with self.assertRaisesRegex(ValueError, 'new_profile'):
                profiles.require_temporary_profile('/Volumes/BuildDisk/evidence/profile')
            self.assertEqual(profiles.require_temporary_profile('/private/tmp/lune-profile'),
                             Path('/private/tmp/lune-profile'))
