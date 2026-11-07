# Sidebar footer

Requested November 7, 2026. Development implementation; not release-accepted.

## Behavior

The vertical sidebar reserves a footer below the scrolling tabs for two browser
level actions: the default-browser prompt and a downloaded Sparkle update ready
to relaunch. No other infobars are routed here. Horizontal mode retains the
existing default-browser infobar and toolbar update treatment.

Each action is one compact row with a 16 pt icon and its existing localized
label. Rows use the tab height, transparent resting background, native semantic
foreground and tab-style hover fill. The default-browser row reads “Make default
browser” and contains its close button inside the shared hover surface, visible
only while hovered. Its context menu retains “Don't ask me again” without a
second visible row. Sidebar tab close buttons also appear only on hover, including selected tabs
(with focus retention for an already focused close control). The footer and tabs
share the same close-button component. Targets are 2 pt larger than the first
refinement (6 pt larger than the original tab control); a native SF Symbols
`xmark` at 12 pt medium weight is centered in a 16 pt canvas to match the New
Tab plus more closely. The symbol size is independent of the target. Their top,
bottom and trailing clearances match. Sidebar row side margins are reduced from 6 to 5 pt; tab, New Tab and
footer icon left insets are increased from 7 to 9 pt. The footer bottom inset
is reduced from 6 to 5 pt. New Tab suppresses its hover tooltip while retaining
its accessible name.

The navigation pill has 8 pt clearance after the traffic-light container (up
from 4 pt) whenever they are adjacent: with a right sidebar or an unpinned,
collapsed left sidebar. A revealed left sidebar continues to determine the
navigation position. The right sidebar toggle is inset 9 pt rather than 4 pt,
including the final additional 1 pt rightward adjustment.

The default row keeps the same tab-height bounds when its close button appears;
only the action width changes. Overflowing default-browser text fades at the
trailing edge using the same `FADE_TAIL` behavior as a browser tab title.

The footer occupies only its preferred height; extra space goes to the tabs.
When both actions are present, the update row appears above the default prompt.
A collapsed sidebar keeps icon actions and accessible names; expansion restores
labels. The same footer travels with the pinned or detached sidebar.

The existing default-browser manager supplies eligibility, system-default action,
dismissal preferences and session-wide closure. The footer does not independently
check or change the system default. The experimental centralized-infobar feature
is unchanged; the shipping legacy manager path supplies the footer.

Sparkle exposes a readiness subscription. A row appears only after the downloaded
update has an installation callback, and invokes the existing relaunch path.
Vertical mode suppresses the duplicate toolbar update highlight, retaining the
app-menu update command. Update checks, download policy and installers are unchanged.

## Implementation

The unbranded platform patch `helium/ui/sidebar-footer.patch` adds a Views footer
to the existing sidebar content container. Its context menu retains the sidebar
hover state, and caption/tab-drag hit testing excludes the footer. Default prompt
callbacks use weak pointers and defer global closure until button/menu dispatch
finishes. Horizontal/vertical transitions transfer the default prompt between
its existing infobar and the footer.

`helium/ui/sidebar-close-controls.patch` applies the requested shared hover
controls, label and row spacing. The default-browser action reuses its existing
localized resource, so its horizontal-mode label also reads “Make default browser.”

`helium/ui/sidebar-native-close-icons.patch` adds the SF Symbol rendering,
independent target sizing, tooltip suppression, footer inset and chrome spacing
refinements. The macOS image conversion preserves supported display scales and
uses the existing semantic foreground color.

`helium/ui/sidebar-footer-hover-geometry.patch` explicitly centers the sidebar
close image horizontally; `SetImageCentered` alone only controlled vertical
alignment. It replaces the default row's flex sizing with fixed-height layout so
the larger close target cannot change its preferred height on hover. It also
uses tab-title fading and applies the final right-toggle inset.

## Development input

The platform input is retained under `inputs/sidebar-footer-4/macos`, commit
`7ffa2cc196acdae12dd8090ac89f7170c60bb829`. It follows `inputs/edge-frame-17/macos`.
The core input remains `inputs/floating-address-2/helium`. All four patches were
written in the prepared source tree, refreshed with quilt, strictly replayed and
unmerged into the platform repository before committing. The lock and patch
manifest retain the exact commit, tree and patch hashes.

## Validation

Evidence is under `.work/sidebar-footer/`:

- Strict canonical replay reproduces all 26 touched files across 96 relevant
  patches with zero fuzz, including the existing GRIT-aware name substitution.
- Five GN header dependency checks pass, along with all 44 repository tests,
  component patch/i18n checks and locked Git-object validation.
- Native arm64 interaction checks confirm default prompt routing, the rejection
  context menu and persisted rejection preference. An unrelated command-line
  warning stays in the header. A no-op Sparkle installer fixture calls the
  existing readiness callback: the update row appears alongside the default
  prompt, survives dismissal of that prompt, and disappears after its relaunch
  action dispatches. No real update is downloaded or installed.

Both final architecture builds pass. Arm64 smoke/defaults/settings/artwork checks
pass. Intel smoke/defaults/settings/artwork checks pass under Rosetta. Earlier
native interaction evidence in `final/` covers the compact two-row stack, shared
footer hover surface, hidden resting close controls and detached footer actions.

The initial SF Symbol refinement is captured under `symbols/`. Native arm64 checks
confirm the smaller `xmark` on a selected tab, the right sidebar toggle inset and
the matching traffic-light/navigation gap in both the right-mounted and unpinned,
collapsed-left layouts. New Tab retains its accessible name; tooltip suppression
is verified in source. The footer bottom inset and target dimensions are also
verified in source.
Owner design acceptance remains separate from these checks. The previous
simulated update was cleared before launching this preview.

The geometry correction is retained in `geometry/`. Native screenshots confirm
the resting footer and corrected horizontal close-icon position. Hover no longer
participates in preferred-height calculation, and the default label uses the same
fade enum as tab titles; these two fixes are verified in source. Native automation
did not reliably produce footer hover, so a before/after hover screenshot is not
claimed. The current preview is left pinned on the left for review. Both updated
architecture builds and smoke checks pass (Intel under Rosetta), and the two
affected GN target checks, component checks and lock validation pass.

These are incremental development builds, not fresh release preparation. Native Intel hardware,
real installed updates with this input, and the full horizontal/collapsed/split
interaction matrix remain unaccepted. No release or deployment was performed.
