# Settings row layout

Nested settings keep a full-width row background and hit target. Their
labels begin 20 CSS pixels inward from the parent label. The trailing
controls align with the parent. Inline padding mirrors the order for
right-to-left locales.

The Settings 2026 refresh uses Chromium's 2 px section gap between
independent controls. Routed section wrappers and nested groups use the
same gap. Legacy separators give way to that gap in the refreshed
sections. Standard Settings uses its existing separator styling. Related
content can share one group, as the excluded-domain description and form
do in **Remove tracking parameters**.

## Appearance and behavior on macOS

Appearance includes the sidebar and toolbar controls. **Always show the
sidebar** sits directly below **Sidebar position** as a full-width row.
**Show toolbar** selects the toolbar reveal mode. The separate Layout section
and its legacy frame, address-bar, and collapse controls are omitted.

Normal vertical-tab windows keep the native floating toolbar and frame even
when an older profile saved the frameless mode, sidebar address bar, or native
frame materials preference as off. The **Use ⌘+S to toggle sidebar** setting
continues to switch between sidebar pinning and the Save Page shortcut.

[Appearance settings validation](../builds/2026-11-25-appearance-settings.json)

### Interface size and font

**Interface size** controls the Standard and Comfortable geometry, including
sidebar widths, row dimensions, and spacing. When a new size takes effect on
restart, the expanded sidebar width resets to 216 pt for Standard or 240 pt
for Comfortable. This applies to new windows and restored windows. A custom
width persists across restarts with the same interface size, including font
changes. [Sidebar width validation](../builds/2026-11-25-sidebar-width-reset.json)

**Interface font** controls the
sidebar typography that previously changed with density. Both preferences
apply on restart. The first launch with the new preference keeps Larger for
existing Comfortable installations. Other installations start at Normal.

Normal uses the macOS preferred reading size, with the standard reading size
as the fallback. Larger scales Normal by 15 percent before rounding. With the
system reading size at Default, Normal uses 12 pt labels and 9 pt date headings.
Larger uses 14 pt labels and 10 pt date headings. Both presets fit both
densities at the default reading size. Large macOS reading sizes can increase
the minimum height of text rows.

The Command bar description lists ⌘T for the floating palette and ⌘/ for
commands. The native address field receives ⌘L in Lune’s floating layout.

[Interface font preview validation](../builds/2026-11-25-interface-font.json)

The settled Appearance input passed strict replay and full source parity for both
architectures. Packaged checks covered the merged Settings rows, new tab
placement, both font choices, and sidebar width after changing size. Native
keyboard shortcuts passed on Apple silicon. Intel ran under Rosetta. [Adoption validation](../builds/2026-11-25-appearance-settings-adoption.json)

## Source and validation

The platform selects `lune/settings-row-layout.patch`. The refresh and
its experimental search remain disabled by default. The compiled arm64
preview exercised 77 standard and 71 refreshed routes, including dialog
routes without submitting their actions. The audit compared Lune and
Helium template changes with the pinned Chromium 159 source. Chromium's
site permissions, font, search-engine management, and security subpages
use their own subpage layout and contiguous rows.

Appearance and behavior, Accessibility, Search, and the custom privacy
controls use the refreshed gap. The packaged Settings resources passed
wide, narrow, and right-to-left geometry checks. The service panel and
tracking exceptions were checked with their controls visible. Patch lint,
the Settings resource build and both independent 664-patch zero-fuzz
replays passed. All 2,102 touched paths matched quilt.
Chromium's normal arm64 resource repack reproduced the accepted preview
byte for byte. Packaged app, ChromeDriver, appearance, Settings, and
artwork smoke passed.
The packaged x86_64 follow-up passed browser, Settings and artwork smoke
under Rosetta using Chromium's normal resource repack. The Settings change
altered two WebUI resources. The Intel resource pack SHA-256 is
`729d55529743996716946e6775198d354172098de067be47ccf07b1ddd6ba0c6`.

The owner accepted the on-screen arm64 preview on November 21, 2026.
The browser task's `.work/settings-row-layout/` directory holds the
route inventory, geometry reports, and arm64 preview pack hashes.
