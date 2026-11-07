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
- A 6 pt interaction band at the window perimeter reveals the header from the
  top and the sidebar from its mounted side. It occupies no layout space.
  AppKit retains actual window resizing. The reveal check also observes the
  immediately adjacent exterior edge. Fullscreen keeps the last physical screen
  pixel trigger rather than reserving a resize band.
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
  The existing 12 pt minimum gap beside a revealed sidebar is preserved.
- The existing fade, drag retention, 48 pt dismissal distance, editing retention,
  theme behavior, standard traffic-light spacing and sidebar pin/menu behavior
  remain in place. The macOS frame-radius/gutter controls are hidden because
  their legacy preferences no longer control this layout.

There is no public AppKit API used here to query an exact system resize-band
width. Six points is Lune's conservative input reservation, already used by its
native toolbar drag exclusion; it is not a replacement resize implementation.
The native frame-radius hook is inherited private AppKit integration. The glass
surface itself continues to use public `NSGlassEffectView` APIs.

## Inputs

- Core: `3c3726b5935203480de96fdb08c9839a814fc2b9`.
- macOS: `b61c7d7e8d2d5b72145cfd43a50a4f8815cdd5fc`.
- Tag: `inputs/edge-frame-2/macos`.
- Patches: `helium/ui/edge-to-edge-frame.patch` and
  `helium/ui/edge-to-edge-separators.patch`.
- Based on the locked sidebar-new-tab-2 input, retaining all prior browser and
  sidebar work. Ordered patch hashes remain in `manifests/patches.json`.

## Validation

Strict no-fuzz replay passes across 61 relevant patches and matches all ten
modified prepared source files. Component lint and lock/ancestry checks pass.
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
Owner confirmation of resize-edge reveal/resize coexistence, flush popover
appearance, and both sidebar orientations remains pending. These are not claimed
as completed pointer-interaction acceptance. The isolated Apple silicon preview
`.work/floating-address/edge-frame-check/` is left open with normal website access.

Local evidence is under `.work/edge-frame/`; source preparation and builds use
`.work/chromium-158/macos/build/src`. This is a development input, not a signed
release or a stable-feed change. Native Intel acceptance remains separate from
Intel-under-Rosetta checks.
