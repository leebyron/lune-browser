#!/usr/bin/env python3
"""Check prepared Lune defaults, onboarding search choices, and attribution."""
import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def check_attribution(tree):
    def read(name):
        return (tree / name).read_text()

    about_strings = ET.fromstring(read('chrome/app/settings_strings.grdp'))
    credit = about_strings.find(".//message[@name='IDS_LUNE_UPSTREAM_CREDIT']")
    assert credit is not None
    wording = (credit.text or '') + ''.join(part.tail or '' for part in credit)
    assert wording.strip() == ('Lune is made possible by the Chromium, ungoogled-chromium, '
                               'and Helium open source projects and other open source software.')
    for project, argument in [('CHROMIUM', 1), ('UNGOOGLED', 2), ('HELIUM', 3), ('OSS', 4)]:
        link = credit.find(f"ph[@name='BEGIN_LINK_{project}']")
        assert link is not None and f'href="${argument}"' in link.text
        assert credit.find(f"ph[@name='END_LINK_{project}']").text == '</a>'
    about = read('chrome/browser/resources/settings/about_page/about_page.html.ts')
    assert about.count('id="upstream-credit"') == 1
    assert (about.index('$i18n{aboutProductCopyright}') < about.index('id="upstream-credit"')
            < about.index('$i18nRaw{aboutProductLicense}'))
    assert 'luneUpstreamCredit' not in about
    provider = read('chrome/browser/ui/webui/settings/settings_localized_strings_provider.cc')
    assert re.search(r'IDS_LUNE_UPSTREAM_CREDIT,\s*chrome::kChromiumProjectURL,\s*'
                     r'u"https://github\.com/ungoogled-software/ungoogled-chromium",\s*'
                     r'u"https://helium\.computer/",\s*chrome::kChromeUICreditsURL16,',
                     provider)
    onboarding = ET.fromstring(read('components/helium_onboarding/helium_onboarding_strings.grdp'))
    credit = onboarding.find(".//message[@name='IDS_HELIUM_ONBOARDING_WELCOME_UPSTREAM_CREDIT']")
    assert credit is not None
    assert credit.find("ph[@name='BEGIN_LINK_HELIUM']").tail == 'Helium browser'
    footer = read('components/helium_onboarding/src/components/WelcomeFooter.svelte')
    assert 'class="upstream-credit"' in footer and 'https://helium.computer/' in footer


def check(tree):
    def read(name):
        return (tree / name).read_text()

    prefs = read('chrome/browser/ui/browser_ui_prefs.cc')
    tabs = read('chrome/browser/ui/tabs/tab_strip_prefs.cc')
    for name, value in {
        'kHeliumUiDensity': 'std::to_underlying(HeliumUiDensity::kDefault)',
        'kHeliumRoundedFrameThickness': '4', 'kHeliumCenteredLocationBar': 'true',
        'kShowAvatarButton': 'false', 'kHeliumCommandBarEnabled': 'true',
        'kHeliumLinkPeekEnabled': 'false', 'kVisualTabSwitcher': 'true',
        'kTabCyclingMRU': 'true', 'kHeliumVerticalPinnedTabsPerRow': '4',
    }.items():
        assert re.search(r'prefs::' + name + r',\s*' + re.escape(value) + r'\)', prefs), name
    for name, value in {
        'kHeliumVerticalRightAligned': 'false', 'kHeliumZenMode': 'true',
        'kHeliumZenModeSidebarPinned': 'true', 'kHeliumZenModeTopChromePinned': 'false',
        'kHeliumVerticalAddressBarInSidebar': 'true',
        'kVerticalTabsUncollapsedWidth': 'GetVerticalTabStripDefaultUncollapsedWidth()',
        'kVerticalTabsCollapsedState': 'false', 'kVerticalTabsExpandOnHoverEnabled': 'true',
    }.items():
        assert re.search(r'prefs::' + name + r',\s*' + re.escape(value) + r'\)', tabs), name
    layout = read('chrome/browser/ui/layout_constants.cc')
    assert re.search(r'GetVerticalTabStripDefaultUncollapsedWidth\(\)\s*\{\s*'
                     r'return IsSpaciousUiDensity\(\) \? 240 : 216;', layout)
    assert 'HeliumLayoutType::kVertical' in tabs
    check_attribution(tree)
    search = read('components/helium_onboarding/src/lib/search-engine-config.ts')
    assert search.index('startpage:') < search.index('kagi:') < search.index('duckduckgo:')
    strings = read('components/helium_onboarding/helium_onboarding_strings.grdp')
    assert 'paid subscription after the trial' in strings
    print('UI source checks passed: defaults, onboarding search choices, and attribution.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_tree', type=Path)
    check(parser.parse_args().source_tree)
