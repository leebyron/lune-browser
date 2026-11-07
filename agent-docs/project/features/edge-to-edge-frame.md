# Edge-to-edge macOS frame

Requested November 7, 2026. This is the owner's proposed macOS 27 styling,
not a claim that Apple mandates these dimensions. It replaces the earlier
26 pt perimeter, 4 pt gutters, content shadow and inset floating sidebar.

## Implemented behavior

- The native AppKit frame hook and content-layer clip both use a 16 pt outer
  radius. Fullscreen retains square screen edges. Individual web panes have
  square clips; the native window clips their outer perimeter once.
- Content has no outer padding, outline, or drop shadow, including fullscreen,
  split view and profiles with the old rounded-frame preference disabled.
  Pinned sidebars still reserve their width, and split dividers still work.
  A single physical-pixel semantic separator overlays the pinned sidebar edge.
- An 8 pt interaction band at the window perimeter reveals the header from the
  top and the sidebar from its mounted side. It occupies no layout space.
  AppKit retains actual window resizing. The reveal check also observes the
  immediately adjacent exterior edge. Fullscreen uses the top four physical
  screen pixels for header reveal and the last side pixel for sidebar reveal, rather than reserving a resize band.
- The detached sidebar is a square glass sheet flush to the top, bottom and
  outer window edge. Its existing fullscreen menu-bar offset is retained.
  The window's outer clip still rounds the physical window corners.
- The sidebar material keeps square corners when glass is recreated for an
  appearance change. It registers no arrow-cursor region over native resize
  targets. Its tab-control child window excludes the 6 pt outer/bottom resize
  region and the existing 5 pt inner sidebar resize handle.
- The header region is 56 pt tall. Native controls remain 36 pt tall, inset
  8 pt from the top and outer side edges. The sidebar header uses the same
  clearance, without changing vertical position when pinned/unpinned.
  The 12 pt minimum adjacent gap is shared by both sidebar modes.
- The existing fade, drag retention, 48 pt dismissal distance, editing retention,
  theme behavior, standard traffic-light spacing and sidebar pin/menu behavior
  remain in place. The macOS frame-radius/gutter controls are hidden because
  their legacy preferences no longer control this layout.

There is no public AppKit API used here to query an exact system resize-band
width. Six points remains Lune's conservative cursor/child-window reservation;
it is independent of the eight-point reveal observer and is not a replacement
resize implementation. The exposed header accepts delivered mouse presses
through its top edge, eliminating a dead strip where AppKit did not resize.
The native frame-radius hook is inherited private AppKit integration. The glass
surface itself continues to use public `NSGlassEffectView` APIs.

## Interaction refinement

The owner accepted edge reveal on input 2 and requested the following changes:

- Add one physical pixel to the fullscreen top trigger. The existing AppKit
  menu-bar fraction drives the top controls and both sidebar modes, including
  the pinned sidebar's tabs, New Tab, toggle and traffic lights.
- Use identical 4 pt tab-area and toggle insets in pinned and popover modes.
  Use a 12 pt adjacent gap for the header controls in both modes. Pinning should
  change page layout without shifting the exposed controls.
- Extend the visible header's input shield to y=0, including the gap above
  controls when the fullscreen menu bar lowers them. Hit testing blocks page
  input throughout that region; native controls are excluded using converted
  native bounds. Cursor registration leaves the native resize perimeter to
  AppKit. A press delivered to the visible header can drag anywhere outside its controls,
  including the top strip: AppKit receives native resize input first. Scrolling
  over the header is consumed.
- Add an appearance-aware `NSColor.separatorColor` hairline only on the pinned
  sidebar's content edge. It is one physical pixel, consumes no layout width,
  accepts no input and is hidden when the sidebar is unpinned.
- Consult `TabStripView::IsPositionInWindowCaption` for the tab list, rather than
  treating its entire available-height rectangle as interactive. An additional
  native input host routes blank pinned space to the existing native window-drag
  and sidebar-menu handlers: AppKit caption dispatch alone bypasses Views. Tabs,
  New Tab, scrollbars, wheel input and resize handles retain their existing routing.
  Caption testing also ignores input-disabled decorative views: the invisible
  full-size shadow view was incorrectly rejecting blank space as interactive.

## Inputs

- Core: `3c3726b5935203480de96fdb08c9839a814fc2b9`.
- macOS: `60529e0d37812d2ec9e211530c1b4e7bf27421b5`.
- Tag: `inputs/edge-frame-5/macos`.
- Patches: `helium/ui/edge-to-edge-frame.patch`,
  `helium/ui/edge-to-edge-separators.patch`,
  `helium/ui/consistent-sidebar-geometry.patch`,
  `helium/ui/pinned-sidebar-native-input.patch`, and
  `helium/ui/header-edge-input.patch`.
- Based on the locked sidebar-new-tab-2 input, retaining all prior browser and
  sidebar work. Ordered patch hashes remain in `manifests/patches.json`.

## Validation

Initial edge-frame validation replayed 61 relevant patches without fuzz and
matched all ten modified prepared source files. Component lint and lock/ancestry checks pass.
All 44 repository tests pass. Native AppKit probes pass square glass recreation
through three light/dark changes, left/right child-window resize clearances,
standard 14 pt traffic lights with 23 pt center spacing, and seven bottom-edge
resize samples retaining the header's top inset and child-window alignment.

Apple silicon and Intel compilation pass. Both architectures pass page loading,
JavaScript, profile persistence, packaged defaults and settings smoke checks;
Intel runs under Rosetta. Native arm64 inspection confirms content fills the
window without the old gutter and the top controls use the 8 pt inset. With the
sidebar collapsed, the actual web viewport is 1100 × 760 CSS pixels in a
1100 × 760 pt window (device scale 2). Command-L selects the address and opens
suggestions in the retained glass editor.

The current native automation cannot reliably position the physical pointer.
The owner confirmed input-2 edge expansion looks right. Acceptance of the
latest menu animation, pin/unpin alignment and header/resize coexistence remains
pending. The owner confirmed input-4 pinned blank-area dragging and right-click
menus work on November 7, 2026. The isolated Apple silicon preview
`.work/floating-address/edge-frame-delivery/` is left open with normal website access.

Local evidence is under `.work/edge-frame/`; source preparation and builds use
`.work/chromium-158/macos/build/src`. This is a development input, not a signed
release or a stable-feed change. Native Intel acceptance remains separate from
Intel-under-Rosetta checks.

Input-3 source validation: strict no-fuzz replay passes across 45 relevant
patches and five touched files. Native AppKit probes verify 25 header points
block document input, controls pass through, perimeter clicks do not start window
dragging, hidden chrome passes through, and the fullscreen menu gap stays shielded.
The divider paints exactly one physical pixel in both alignments and appearances,
accepting no input. Seven resize-anchor samples and all 44 repository tests pass.
Input-3 arm64 and Intel builds and smoke/default/settings checks pass (Intel
under Rosetta). Input-4 strict replay passes across 35 relevant patches and
three touched files. The owner confirmed the pinned-sidebar input correction
in the rebuilt arm64 app. Input-4 arm64 smoke/default/settings checks and both
architecture builds pass.

Input 5 changes windowed reveal to 8 logical pixels on top and side, fullscreen
top reveal to 4 physical pixels, and retains a 1 physical-pixel side trigger.
Extracted production AppKit probes pass all exact boundary cases, header
blocking/control exclusions, and drag delivery in the previously inert top
strip. Strict replay passes across 29 relevant patches and two files. Final
Both architecture builds and smoke/default/settings checks pass; Intel runs
under Rosetta. Final combined replay covers 47 relevant patches and all five
touched source files. All 44 repository tests pass. Physical resize/drag
coexistence with the widened reveal bands still requires owner acceptance.
The accepted pinned-sidebar drag/menu behavior is retained.
