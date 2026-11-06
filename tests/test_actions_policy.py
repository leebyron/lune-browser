"""Prevent imported workflow paths from silently becoming active again."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'actions_policy', Path(__file__).parents[1] / 'scripts/check-actions-policy.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ActionsPolicyTests(unittest.TestCase):
    def audit(self, extra=(), active=None):
        workflows = [{'path': path, 'state': 'active'} for path in
                     (policy.ACTIVE if active is None else active)]
        with contextlib.redirect_stdout(io.StringIO()):
            return policy.audit(workflows + list(extra))

    def test_disabled_imported_history_is_preserved(self):
        self.assertEqual(self.audit([
            {'path': f'.github/workflows/{name}.yml', 'state': 'disabled_manually'}
            for name in ('ci', 'lint', 'sanity')]), [])

    def test_reenabled_inherited_and_new_workflows_fail(self):
        for name in ('ci', 'lint', 'sanity', 'new-upstream-build'):
            with self.subTest(name=name):
                self.assertTrue(self.audit([
                    {'path': f'.github/workflows/{name}.yml', 'state': 'active'}]))

    def test_missing_local_workflow_fails(self):
        self.assertTrue(self.audit(active=policy.ACTIVE - {'.github/workflows/checks.yml'}))

    def test_disabled_local_workflow_fails(self):
        self.assertTrue(self.audit(
            [{'path': '.github/workflows/checks.yml', 'state': 'disabled_manually'}],
            active=policy.ACTIVE - {'.github/workflows/checks.yml'}))
