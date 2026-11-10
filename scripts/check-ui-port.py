#!/usr/bin/env python3
"""Check prepared UI defaults, search recommendation, and surviving attribution."""
import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def check(tree):
    def read(name):
        return (tree / name).read_text()

    prefs = read('chrome/browser/ui/browser_ui_prefs.cc')
    tabs = read('chrome/browser/ui/tabs/tab_strip_prefs.cc')
    for name, value in {
        'kHeliumRoundedFrameThickness': '4', 'kHeliumCenteredLocationBar': 'true',
        'kShowAvatarButton': 'false', 'kHeliumCommandBarEnabled': 'true',
        'kHeliumLinkPeekEnabled': 'false', 'kVisualTabSwitcher': 'true',
        'kTabCyclingMRU': 'true', 'kHeliumVerticalPinnedTabsPerRow': '4',
    }.items():
        assert re.search(r'prefs::' + name + r',\s*' + value + r'\)', prefs), name
    for name, value in {
        'kHeliumVerticalRightAligned': 'true', 'kHeliumZenMode': 'true',
        'kHeliumZenModeSidebarPinned': 'true', 'kHeliumZenModeTopChromePinned': 'false',
        'kHeliumVerticalAddressBarInSidebar': 'true', 'kVerticalTabsUncollapsedWidth': 'kVerticalTabStripDefaultUncollapsedWidth',
        'kVerticalTabsCollapsedState': 'false', 'kVerticalTabsExpandOnHoverEnabled': 'true',
    }.items():
        assert re.search(r'prefs::' + name + r',\s*' + value + r'\)', tabs), name
    state = read('chrome/browser/ui/tabs/vertical_tab_strip_state.h')
    assert re.search(r'kVerticalTabStripDefaultUncollapsedWidth\s*=\s*216\s*;', state)
    assert 'HeliumLayoutType::kVertical' in tabs
    assert 'static_cast<int>(HeliumUiDensity::kStandard)' in prefs
    for file, name in [
        ('chrome/app/settings_strings.grdp', 'IDS_LUNE_UPSTREAM_CREDIT'),
        ('components/helium_onboarding/helium_onboarding_strings.grdp',
         'IDS_HELIUM_ONBOARDING_WELCOME_UPSTREAM_CREDIT'),
    ]:
        message = ET.fromstring(read(file)).find(f".//message[@name='{name}']")
        assert message is not None and 'Built on Helium' in ''.join(message.itertext()), name
    for file in ['chrome/browser/resources/settings/about_page/about_page.html.ts',
                 'components/helium_onboarding/src/pages/Welcome.svelte']:
        assert 'id="upstream-credit"' in read(file)
        assert 'https://helium.computer/' in read(file)
    search = read('components/helium_onboarding/src/lib/search-engine-config.ts')
    assert search.index('kagi:') < search.index('duckduckgo:')
    strings = read('components/helium_onboarding/helium_onboarding_strings.grdp')
    assert 'Suggested for Lune.' in strings and 'paid subscription after the trial' in strings
    print('UI source checks passed: defaults, Kagi recommendation, and Helium credits.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_tree', type=Path)
    check(parser.parse_args().source_tree)
