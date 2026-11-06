#!/usr/bin/env python3
"""Check that Lune name substitution preserves upstream credit translations."""
import argparse
import importlib.util
import re
from pathlib import Path
import sys
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('platform', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('--prepared', action='store_true',
                        help='Also reject Lune branding inside protected upstream translations in prepared sources.')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('lune_names', args.platform / 'lune_names.py')
    names = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(names)
    names.util.add_grit_to_path(args.source)
    fixtures = {
        'IDS_HELIUM_ONBOARDING_PARTNER_TITLE': 'Helium Partner',
        'IDS_HELIUM_ONBOARDING_PARTNER_TOOLTIP': 'Paying for this service will support the development of Helium.',
        'IDS_LUNE_UPSTREAM_CREDIT': 'Built on Helium, with thanks to its authors and contributors.',
        'IDS_HELIUM_ONBOARDING_WELCOME_UPSTREAM_CREDIT': 'Built on Helium, with thanks to its authors and contributors.',
        'IDS_SETTINGS_HELIUM_SERVICES': 'Helium services',
        'IDS_LUNE_SERVICES_PROVIDER': 'Lune uses services hosted by Helium.',
        'IDS_TEST_PRODUCT': 'Welcome to Helium',
    }
    expected_text = dict(fixtures)
    expected_text['IDS_TEST_PRODUCT'] = 'Welcome to Lune'
    source = ET.Element('grit')
    translations = ET.Element('translationbundle', lang='en-GB')
    before_ids = {}
    for name, text in fixtures.items():
        message = ET.SubElement(source, 'message', name=name)
        message.text = text
        fingerprint = names.util.compute_fp(message)
        before_ids[name] = fingerprint
        # The two credit messages share text and therefore the same translation.
        if not any(t.get('id') == fingerprint for t in translations):
            ET.SubElement(translations, 'translation', id=fingerprint).text = text
    ET.SubElement(translations, 'translation', id='123').text = 'Legacy Helium branding'
    changed_source, mapping = names.util.replace_grit_tree(ET.tostring(source, encoding='unicode'))
    changed_xtb = names.util.replace_xtb_tree(ET.tostring(translations, encoding='unicode'), mapping)
    actual = {t.get('id'): t.text for t in ET.fromstring(changed_xtb)}
    for name, text in fixtures.items():
        before = before_ids[name]
        if name != 'IDS_TEST_PRODUCT':
            if mapping.get(before) != before or actual.get(before) != text:
                raise SystemExit(f'Upstream attribution was renamed: {name}: {actual.get(before)!r}')
        elif actual.get(mapping[before]) != 'Welcome to Lune':
            raise SystemExit('Ordinary product translation did not follow its updated source ID')
    if actual.get('123') != 'Legacy Lune branding':
        raise SystemExit('Unrelated translation behavior changed')
    for message in ET.fromstring(changed_source).findall('message'):
        expected = expected_text[message.get('name')]
        if message.text != expected:
            raise SystemExit('Source message differs from expected branding policy')
    # Exercise the actual multiprocessing entry point as well as the helper
    # functions; macOS workers import the script in fresh Python processes.
    with tempfile.TemporaryDirectory(prefix='lune-name-check-') as directory:
        tree = Path(directory)
        (tree / 'tools').mkdir()
        (tree / 'tools/grit').symlink_to((args.source / 'tools/grit').resolve())
        source_file = tree / 'strings.grd'
        xtb_file = tree / 'strings_en-GB.xtb'
        source_file.write_text(ET.tostring(source, encoding='unicode'))
        xtb_file.write_text(ET.tostring(translations, encoding='unicode'))
        subprocess.run([sys.executable, str((args.platform / 'lune_names.py').resolve()), str(tree)],
                       check=True, capture_output=True, text=True)
        if source_file.read_text() != changed_source or xtb_file.read_text() != changed_xtb:
            raise SystemExit('Multiprocessing name-substitution output differs from the tested helpers')
    if args.prepared:
        protected = {}
        seen_names = set()
        for relative in ('chrome/app/settings_strings.grdp',
                         'components/helium_onboarding/helium_onboarding_strings.grdp'):
            for message in ET.parse(args.source / relative).getroot().iter('message'):
                if message.get('name') in names.UPSTREAM_CREDITS:
                    protected[names.util.compute_fp(message)] = message.get('name')
                    seen_names.add(message.get('name'))
                    if 'Helium' not in ''.join(message.itertext()):
                        raise SystemExit(f'Upstream name missing in {message.get("name")}')
        if seen_names != names.UPSTREAM_CREDITS:
            raise SystemExit('Missing protected source messages')
        count = 0
        for path in names.names.get_substitutable_files(args.source, ['xtb']):
            text = path.read_text()
            if not any(f'id="{fingerprint}"' in text for fingerprint in protected):
                continue
            for translation in ET.fromstring(text).iter('translation'):
                if translation.get('id') in protected:
                    count += 1
                    if re.search(r'\bLune\b', ''.join(translation.itertext())):
                        raise SystemExit(f'Localized upstream credit was renamed: {path}: {protected[translation.get("id")]}')
        if not count:
            raise SystemExit('No protected translations found to validate')
        print(f'Prepared attribution passed: {count} protected translations checked.')
    print('Name-substitution regression passed: credits, ordinary localized branding, and multiprocessing.')


if __name__ == '__main__':
    main()
