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
