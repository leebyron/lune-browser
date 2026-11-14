"""Exercise command timing without building Chromium or changing its environment."""
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/time-development.py'


class DevelopmentTimingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.report = self.root / 'reports/timings.jsonl'

    def tearDown(self):
        self.tmp.cleanup()

    def run_timer(self, *command):
        return subprocess.run([
            sys.executable, str(SCRIPT), '--report', str(self.report),
            '--iteration', 'preview-1', '--phase', 'checks', '--', *command,
        ], cwd=self.root, capture_output=True, text=True)

    def records(self):
        return [json.loads(line) for line in self.report.read_text().splitlines()]

    def test_preserves_arguments_output_and_failure_status_while_appending(self):
        command = [sys.executable, '-c', 'import sys; print(sys.argv[1])',
                   'literal $HOME; `no-shell`']
        result = self.run_timer(*command)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), command[-1])
        failed = self.run_timer(sys.executable, '-c', 'raise SystemExit(7)')
        self.assertEqual(failed.returncode, 7)
        first, second = self.records()
        self.assertEqual(first['command'], command)
        self.assertEqual(first['cwd'], str(self.root.resolve()))
        self.assertEqual(first['arch'], 'arm64')
        self.assertGreaterEqual(first['seconds'], 0)
        self.assertLessEqual(first['started_at'], first['finished_at'])
        self.assertEqual(second['returncode'], 7)
        self.assertEqual(second['exit_code'], 7)

    def test_records_launch_failure(self):
        result = self.run_timer(str(self.root / 'missing-command'))
        self.assertEqual(result.returncode, 127)
        record, = self.records()
        self.assertIn('launch_error', record)
        self.assertEqual(record['exit_code'], 127)

    def test_signal_failure_is_not_reported_as_success(self):
        result = self.run_timer(sys.executable, '-c',
                                'import os, signal; os.kill(os.getpid(), signal.SIGTERM)')
        self.assertEqual(result.returncode, 128 + signal.SIGTERM)
        record, = self.records()
        self.assertEqual(record['returncode'], -signal.SIGTERM)

    def test_unwritable_report_does_not_execute_command(self):
        self.report.mkdir(parents=True)
        result = self.run_timer(sys.executable, '-c',
                                'from pathlib import Path; Path("ran").touch()')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'ran').exists())


if __name__ == '__main__':
    unittest.main()
