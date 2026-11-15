"""Host-owned storage must fail closed without coupling other Macs to a disk."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('storage_lune',
    Path(__file__).parents[1] / 'scripts/lune.py')
lune = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lune)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.mount = self.root / 'disk'
        self.mount.mkdir()
        self.config = dict(schema_version=1, mountpoint=str(self.mount),
            volume_uuid='12345678-1234-1234-1234-123456789ABC',
            cache_root=str(self.mount / 'work'), sccache_dir=str(self.mount / 'sccache'),
            sccache_cache_size='200G')
        self.info = dict(VolumeUUID=self.config['volume_uuid'], MountPoint=str(self.mount),
                         FilesystemType='apfs', WritableVolume=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_unconfigured_host_keeps_its_existing_layout(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(Path, 'home', return_value=self.root):
            self.assertIsNone(lune.storage_config())
            with patch.object(lune, 'check_storage') as check:
                lune.configure_workspace('arm64')
                check.assert_not_called()

    def test_explicit_missing_or_invalid_configuration_is_rejected(self):
        config_path = self.root / 'storage.json'
        with patch.dict(os.environ, {'LUNE_BUILD_STORAGE': str(config_path)}):
            with self.assertRaisesRegex(ValueError, 'Missing host'):
                lune.storage_config()
            for key, value in [('schema_version', 2), ('cache_root', 'relative'),
                               ('volume_uuid', 'disk1s1'), ('volume_uuid', '-' * 36),
                               ('volume_uuid', 1), ('sccache_cache_size', '0'),
                               ('sccache_cache_size', 200)]:
                config_path.write_text(json.dumps(dict(self.config, **{key: value})))
                with self.subTest(key=key), self.assertRaises(ValueError):
                    lune.storage_config()

    def test_missing_mount_stops_before_disk_access_or_directory_creation(self):
        with patch.object(Path, 'is_mount', return_value=False), \
                patch.object(lune.subprocess, 'check_output') as info:
            with self.assertRaisesRegex(ValueError, 'not mounted'):
                lune.check_storage(self.config)
            info.assert_not_called()
            self.assertFalse(Path(self.config['cache_root']).exists())

    def test_same_name_wrong_volume_readonly_and_wrong_filesystem_are_rejected(self):
        for changed in [dict(VolumeUUID='other'), dict(MountPoint='/wrong'),
                        dict(WritableVolume=False), dict(FilesystemType='exfat')]:
            with self.subTest(changed=changed), patch.object(Path, 'is_mount', return_value=True), \
                    patch.object(lune.subprocess, 'check_output',
                        return_value=plistlib.dumps(dict(self.info, **changed))):
                with self.assertRaisesRegex(ValueError, 'mismatch'):
                    lune.check_storage(self.config)

    def test_symlink_escape_from_expected_volume_is_rejected(self):
        Path(self.config['cache_root']).symlink_to(self.root)
        with patch.object(Path, 'is_mount', return_value=True), \
                patch.object(lune.subprocess, 'check_output', return_value=plistlib.dumps(self.info)):
            with self.assertRaisesRegex(ValueError, 'escapes'):
                lune.check_storage(self.config)

    def test_clean_build_environment_uses_only_selected_host_cache_settings(self):
        with patch.object(lune, 'storage_config', return_value=self.config), \
                patch.object(lune, 'check_storage'), \
                patch.dict(os.environ, {'UNRELATED_SECRET': 'secret', 'SCCACHE_DIR': '/wrong'}, clear=True):
            env = lune.build_env()
            self.assertEqual(env['SCCACHE_DIR'], self.config['sccache_dir'])
            self.assertEqual(env['SCCACHE_CACHE_SIZE'], '200G')
            self.assertNotIn('UNRELATED_SECRET', env)

    def test_checkouts_keep_separate_outputs_and_existing_sources_are_preserved(self):
        targets = []
        for name in ('interactive', 'runner'):
            checkout = self.root / name
            checkout.mkdir()
            with patch.object(lune, 'ROOT', checkout), \
                    patch.object(lune, 'storage_config', return_value=self.config), \
                    patch.object(lune, 'check_storage'):
                lune.configure_workspace('arm64')
                link = checkout / '.work/arm64'
                self.assertTrue(link.is_symlink())
                targets.append(link.resolve())
                existing = checkout / '.work/x86_64'
                existing.mkdir()
                (existing / 'pending.patch').write_text('unpublished')
                lune.configure_workspace('x86_64')
                self.assertFalse(existing.is_symlink())
                self.assertEqual((existing / 'pending.patch').read_text(), 'unpublished')
        self.assertNotEqual(*targets)

    def test_free_space_is_measured_on_actual_target_filesystem(self):
        target = self.mount / 'sources'
        target.mkdir()
        with patch.object(lune, 'storage_config', return_value=None), \
                patch.object(shutil, 'disk_usage', return_value=shutil._ntuple_diskusage(300*2**30, 1, 250*2**30)) as usage:
            lune.check_build_space(target / 'not-created', preparing=True)
            usage.assert_called_once_with(target)
        with patch.object(lune, 'storage_config', return_value=None), \
                patch.object(shutil, 'disk_usage', return_value=shutil._ntuple_diskusage(300*2**30, 1, 79*2**30)):
            with self.assertRaisesRegex(ValueError, '80 GiB'):
                lune.check_build_space(target)

    def test_named_task_workspaces_cannot_escape_the_repository(self):
        with patch.object(lune, 'storage_config', return_value=None):
            for name in ('..', '../outside', '/absolute', 'one/two', '.hidden'):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'single directory'):
                    lune.storage(argparse.Namespace(workspace=name))

    def test_named_task_workspace_uses_host_configuration(self):
        checkout = self.root / 'project'
        checkout.mkdir()
        with patch.object(lune, 'ROOT', checkout), \
                patch.object(lune, 'storage_config', return_value=self.config), \
                patch.object(lune, 'check_storage'):
            lune.storage(argparse.Namespace(workspace='feature-review'))
        target = checkout / '.work/feature-review'
        self.assertTrue(target.is_symlink())
        self.assertTrue(target.resolve().is_relative_to(self.mount))


if __name__ == '__main__':
    unittest.main()
