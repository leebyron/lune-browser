# Sidebar new-tab placement

Requested November 6–7, 2026. Development implementation; not release-accepted.

## Behavior

In vertical-tab mode, the New Tab row sits below the pinned tabs and above the
regular tabs. It remains outside both scrolling viewports, so scrolling regular
tabs does not move the button. With no pinned tabs, it is the first row. With only
pinned tabs, it remains available below them.

Ordinary new tabs use the first unpinned index. This includes the New Tab button,
new tabs created through the Command-T palette, and default-position API tabs.
The sidebar policy takes precedence over the inherited next-to-active preference.
Existing tabs are not reordered when switching modes.

Links opened in a new tab use the position immediately after the active tab.
Successive background links therefore appear newest-first immediately below their
opener. Pinned tabs remain a contiguous leading section, so links from pinned tabs
open at the start of the regular tabs. Groups and split tabs retain their existing
contiguity constraints. Explicit insertion positions, including drag/drop and
New Tab to Right, remain authoritative. Horizontal tabs retain their prior
insertion behavior and preference handling.

Typed new tabs preserve opener tracking when prepended, so closing a quick-lookup
tab can return to its opener. The command palette still reuses an existing blank
new-tab page according to its existing behavior.

New Tab has no resting background and uses the regular tab foreground and hover
fill, including native semantic colors in detached sidebars. The gap below it is
the same 2 pt used between regular tabs. Pinned tiles use a subtle fill instead of
an outline, retain their content insets, and have 6 pt horizontal spacing. The gap
between the pinned section and New Tab uses that same 6 pt constant.

## Implementation

`helium/ui/sidebar-new-tab-placement.patch` is a separate, unbranded patch using
shared Chromium Views and tab-model APIs. It is ordered after the current platform
UI stack because it modifies that stack's sidebar composition. It contains no
AppKit, Lune identity, service, or release-policy code.

The region transfers its existing button container into `TabStripView`, between
the pinned and unpinned scroll views, and takes ownership back when the view is
replaced. This retains context menus, collapse behavior, and action callbacks.
The layout reserves button height before allocating the scrolling viewports;
caption hit testing and the tab-drag bounds account for its new position.

`TabStripModel::AddTab` changes only default-position, unpinned insertion in
vertical mode. Explicit indices still go through the existing group, split, and
pinned-boundary constraints. `DetermineInsertionIndex` uses the active tab's next
index for both foreground and background sidebar links.

## Development input

The platform input is retained locally under `inputs/sidebar-new-tab-2/macos`.
Its parent input was `inputs/floating-address-20/macos`; the core input remains
`inputs/floating-address-2/helium`. The ordered platform commits are:

- `feb6cfd`: button placement, default insertion, and link placement.
- `80418123`: direct tab-model dependencies found by GN checking.
- `6b6f903d`: matching tab colors and gaps, filled pinned tiles.
- `cfaeba22`: cap the pinned scrolling minimum at its preferred height so a
  single row does not reserve an extra gap below its tiles.

The source was authored in the prepared tree with quilt, refreshed, unmerged into
the platform repository, and committed. The patch manifest records the ordered
patches and SHA-256 hashes; the lock retains the full commit and tree IDs.

## Validation

Local evidence is collected under `.work/sidebar-new-tab/`:

- Strict canonical replay reproduces all 15 touched source files across 29
  patches with zero fuzz (`replay.json`).
- GN dependency checks pass for the tab model, common/vertical tab Views, and
  vertical tab-strip region (`gn-check.log`).
- Arm64 and x86_64 compilation and linking pass. The standard browser smoke,
  defaults, and settings checks pass on arm64 and Intel under Rosetta.
- Five local ChromeDriver/extension checks pass: default prepend despite the
  next-to-active preference, explicit-index preservation, consecutive
  background links immediately after active, preservation of the active tab,
  and insertion outside a leading group (`final/runtime.json`).
- Native arm64 inspection confirms button placement, transparent resting
  background, filled pinned tiles without outlines, and button-click insertion
  above regular tabs. Closing the new tab returns to its opener. Screenshot
  evidence is under `styled/` and `final/`; final inspection confirms 6 pt below the
  pinned tiles and 2 pt below New Tab.
- All 44 repository tests, component patch/i18n checks, and locked Git-object
  validation pass.

These are incremental development builds, not fresh release preparation. Native
Intel hardware and the full light/dark, collapsed, detached, scrolling, split-tab,
and horizontal-mode interaction matrix have not been accepted for this change.
No release or deployment was performed.
