import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/release'))
import run_publisher


class PublisherEnvironmentTests(unittest.TestCase):
    def test_configured_signer_survives_without_inheriting_shell_utilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = root / 'tools'
            tools.mkdir()
            links = root / 'shell'
            links.mkdir()
            for tool in ('gh', 'gpg'):
                executable = tools / tool
                executable.write_text('#!/bin/sh\nexit 0\n')
                executable.chmod(0o755)
                (links / tool).symlink_to(executable)
            original = dict(HOME=tmp, PATH=str(links), GNUPGHOME=str(root / 'key-home'),
                            GPG_TTY='/dev/tty', GH_TOKEN='fixture-token',
                            UNRELATED_SECRET='must-not-propagate')
            with patch.dict(os.environ, original, clear=True):
                env = run_publisher.publisher_env()
            self.assertEqual(env['GNUPGHOME'], original['GNUPGHOME'])
            self.assertEqual(env['GPG_TTY'], original['GPG_TTY'])
            self.assertEqual(env['GH_TOKEN'], original['GH_TOKEN'])
            self.assertEqual(env['PATH'].split(os.pathsep),
                             ['/usr/bin', '/bin', '/usr/sbin', '/sbin', str(tools.resolve())])
            self.assertNotIn('UNRELATED_SECRET', env)
            with patch.dict(os.environ, original, clear=True):
                self.assertNotIn('GH_TOKEN', run_publisher.build_env())
                self.assertNotIn('GNUPGHOME', run_publisher.build_env())

    def test_missing_publisher_tool_stops_before_launch(self):
        with patch('run_publisher.shutil.which', return_value=None), \
                patch('run_publisher.os.execve') as launch:
            with self.assertRaisesRegex(ValueError, 'requires gh'):
                run_publisher.main()
            launch.assert_not_called()

    def test_launcher_forwards_publication_arguments_and_environment(self):
        env = {'PATH': '/usr/bin'}
        args = ['run_publisher.py', 'promote', '--channel', 'stable']
        with patch.object(sys, 'argv', args), \
                patch('run_publisher.publisher_env', return_value=env), \
                patch('run_publisher.os.execve') as launch:
            run_publisher.main()
        launch.assert_called_once_with(sys.executable, [sys.executable,
            str(run_publisher.ROOT / 'scripts/release/publish.py'), *args[1:]], env)
