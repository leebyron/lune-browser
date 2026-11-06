"""Regression coverage for the advisory source catalog audit."""
import importlib.util
from pathlib import Path
import sys
import unittest

scripts = Path(__file__).parents[1] / 'scripts'
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location('component_inputs', scripts / 'check-component-inputs.py')
inputs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inputs)
sys.path.pop(0)


class CatalogAuditTests(unittest.TestCase):
    def test_superseded_wording_does_not_create_a_false_gap(self):
        old = {'source': 'settings.grdp', 'name': 'IDS_FRAME', 'message': 'Experimental'}
        final = {**old, 'message': 'Applies after restart'}
        self.assertEqual(inputs.catalog_gaps([old, final], [final]), [])
        self.assertEqual(inputs.catalog_gaps([old, final], [old]), [final])

    def test_same_id_in_different_resources_is_not_collapsed(self):
        settings = {'source': 'settings.grdp', 'name': 'IDS_CREDIT', 'message': 'Credit'}
        onboarding = {**settings, 'source': 'onboarding.grdp'}
        self.assertEqual(inputs.catalog_gaps([settings, onboarding], [settings]), [onboarding])
