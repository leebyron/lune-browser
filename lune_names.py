#!/usr/bin/env python3
"""Apply Lune's display name through Helium's GRIT-aware substitution pipeline."""
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent / 'helium-chromium' / 'utils'))
import name_substitution as names
import name_substitution_utils as util

# Preserve the upstream exclusions (Web Store, Root Program, Remote Desktop).
# Preserve helium:// URLs and code/pref identifiers for compatibility.
HELIUM_PASS = '--helium' in sys.argv

util.REPLACEMENT_REGEXES = [
    (regex, replacement if HELIUM_PASS else replacement.replace('Helium', 'Lune'))
    for regex, replacement in util.REPLACEMENT_REGEXES
]
if not HELIUM_PASS:
    util.REPLACEMENT_REGEXES.append((re.compile(r'\bHelium\b'), 'Lune'))

# These attribution messages deliberately name the upstream project.
UPSTREAM_CREDITS = {
    'IDS_LUNE_UPSTREAM_CREDIT',
    'IDS_HELIUM_ONBOARDING_PARTNER_TITLE',
    'IDS_HELIUM_ONBOARDING_PARTNER_TOOLTIP',
    'IDS_HELIUM_ONBOARDING_WELCOME_UPSTREAM_CREDIT',
}
# Service providers keep their own identity, including translated labels.
# Explicit Lune disclosures can name both the product and its provider.
PROVIDER_DISCLOSURES = {
    'IDS_LUNE_SERVICES_PROVIDER', 'IDS_LUNE_SERVICES_CONSENT',
    'IDS_LUNE_SERVICES_UPDATES', 'IDS_HELIUM_ONBOARDING_SERVICES_PROVIDER',
    'IDS_SETTINGS_HELIUM_SERVICES_UBO',
    'IDS_SETTINGS_HELIUM_SERVICES_UBO_DESCRIPTION',
    'IDS_HELIUM_ONBOARDING_SERVICES_CONSENT',
    'IDS_HELIUM_ONBOARDING_SERVICES_INSTANCE_PROVIDER',
    'IDS_HELIUM_ONBOARDING_SERVICES_LUNE_UPDATES',
    'IDS_HELIUM_ONBOARDING_SERVICES_BANGS_TITLE',
    'IDS_HELIUM_ONBOARDING_SERVICES_BANGS_DESC',
    'IDS_HELIUM_ONBOARDING_SERVICES_EXTENSIONS_TITLE',
    'IDS_HELIUM_ONBOARDING_SERVICES_EXTENSIONS_DESC',
    'IDS_HELIUM_ONBOARDING_SERVICES_UBLOCK_TITLE',
    'IDS_HELIUM_ONBOARDING_SERVICES_UBLOCK_DESC',
    'IDS_HELIUM_ONBOARDING_SERVICES_SPELLCHECK_TITLE',
    'IDS_HELIUM_ONBOARDING_SERVICES_SPELLCHECK_DESC',
    'IDS_HELIUM_ONBOARDING_SERVICES_COMPONENT_UPDATES_TITLE',
    'IDS_HELIUM_ONBOARDING_SERVICES_COMPONENT_UPDATES_DESC',
    'IDS_HELIUM_ONBOARDING_PASSWORD_ONE_TIME_NOTICE',
}


def preserve_provider(message):
    text = ''.join(message.itertext())
    return (message.get('name') in PROVIDER_DISCLOSURES or
            'Helium services' in text or 'Helium servers' in text)


_replace_grit_message = util.replace_grit_message


def replace_grit_message(message):
    if message.get('name') in UPSTREAM_CREDITS or preserve_provider(message):
        return False
    return _replace_grit_message(message)


util.replace_grit_message = replace_grit_message

# Carry protected fingerprints through the existing worker map as identity
# entries. Ordinary substitutions never add an identity entry, and the map is
# already serialized to the XTB workers on spawn-based platforms such as macOS.
_replace_grit_tree = util.replace_grit_tree
_replace_xtb_translation = util.replace_xtb_translation


def replace_grit_tree(text):
    result, fingerprint_map = _replace_grit_tree(text)
    tree = util.xml.fromstring(text, util.get_parser())
    for message in tree.findall('.//message'):
        if message.get('name') in UPSTREAM_CREDITS or preserve_provider(message):
            fingerprint = util.compute_fp(message)
            if fingerprint_map.get(fingerprint, fingerprint) != fingerprint:
                raise ValueError('Upstream attribution conflicts with a renamed message')
            fingerprint_map[fingerprint] = fingerprint
    return result, fingerprint_map


def replace_xtb_translation(message, fingerprint_map):
    fingerprint = message.get('id')
    if fingerprint_map.get(fingerprint) == fingerprint:
        return False
    return _replace_xtb_translation(message, fingerprint_map)


util.replace_grit_tree = replace_grit_tree
util.replace_xtb_translation = replace_xtb_translation

if __name__ == '__main__':
    arguments = [arg for arg in sys.argv[1:] if arg != '--helium']
    if len(arguments) != 1:
        raise SystemExit('Usage: lune_names.py [--helium] CHROMIUM_SOURCE')
    names.do_substitution(Path(arguments[0]), None, min(os.cpu_count() or 1, 8), False)
