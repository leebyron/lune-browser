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
util.REPLACEMENT_REGEXES = [
    (regex, replacement.replace('Helium', 'Lune'))
    for regex, replacement in util.REPLACEMENT_REGEXES
]
util.REPLACEMENT_REGEXES.append((re.compile(r'\bHelium\b'), 'Lune'))

# These attribution messages deliberately name the upstream project.
UPSTREAM_CREDITS = {
    'IDS_LUNE_UPSTREAM_CREDIT',
    'IDS_HELIUM_ONBOARDING_PARTNER_TITLE',
    'IDS_HELIUM_ONBOARDING_PARTNER_TOOLTIP',
    'IDS_HELIUM_ONBOARDING_WELCOME_UPSTREAM_CREDIT',
}
_replace_grit_message = util.replace_grit_message


def replace_grit_message(message):
    if message.get('name') in UPSTREAM_CREDITS:
        return False
    return _replace_grit_message(message)


util.replace_grit_message = replace_grit_message

# A translation has an ID, not a message name. Only rewrite it when the
# corresponding source message changed. Otherwise excluded upstream credits
# acquire Lune's name while retaining the original Helium fingerprint.
_replace_xtb_translation = util.replace_xtb_translation


def replace_xtb_translation(message, fingerprint_map):
    if message.get('id') not in fingerprint_map:
        return False
    return _replace_xtb_translation(message, fingerprint_map)


util.replace_xtb_translation = replace_xtb_translation

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: lune_names.py CHROMIUM_SOURCE')
    names.do_substitution(Path(sys.argv[1]), None, min(os.cpu_count() or 1, 8), False)
