# Floating native address capsule

Prototype requested on 2026-11-06: reveal a floating glass address bar when the
pointer enters the top rail. The owner replaced the initial 700 ms cooldown with
a 48 pt distance boundary, requested an editable primary address bar, and an
8 pt inset for the floating sidebar. Use Apple's
public UI SDK and the latest mockups from the “Lune: Figma design” chat.

## Reference and scope

[Figma file](https://www.figma.com/design/I39uQunZpu6LsS7mDjcGSh/Untitled).
The latest mounted/floating left/right mockups in that chat show a centered
address capsule, separate navigation and extension capsules, and content behind
the controls. Figma's connector hit its Starter-plan limit. The owner explicitly
authorized using the desktop mockups and screenshots instead of connector output.
The reference inspected was `02-mounted-right-design.png` from that chat's
`sidebar-screenshots` directory.

This increment implements the address capsule, paired navigation capsule, and
trailing browser-actions glass group. The remaining sidebar redesign in
[issue #3](https://github.com/leebyron/lune-browser/issues/3) is separate work.

## Implementation

The native macOS view uses public AppKit `NSGlassEffectView` (macOS 26+) with
native controls inside its `contentView`, system font, and SF Symbols. macOS 27 adds
`effectIsInteractive`; earlier supported macOS versions use AppKit's
`NSVisualEffectView`. AppKit owns the material rendering and accessibility
transparency adaptation. No CSS glass imitation or private glass API is used.

The 480 × 36 pt capsule is centered over the content region, 8 pt from the top,
and narrows with the window. Mounted sidebars and the current animated bounds of an unmounted sidebar
reduce the available space. The capsule moves and narrows with the sidebar
without resizing the page.
The native host overlays the content without participating in page layout.
The visible strip's empty background uses AppKit's `performWindowDragWithEvent:`
for window dragging. Native controls and text selection keep their normal input.
Back and forward share a leading 76 × 36 pt glass capsule using SF Symbols
`chevron.backward` and `chevron.forward`, with enabled states from Chromium's
navigation controller. The old sidebar navigation row is hidden in this mode.
The trailing group hosts the actual existing Views toolbar controls in a
nonactivating transparent child widget over an AppKit glass surface. This retains
extension models, pinned actions, menus, and their real anchor views. Controls
return to the original toolbar when switching layouts. The old expanded header
is suppressed, so revealing controls does not move the content panel.
The prototype applies to the existing vertical, frameless, address-in-sidebar
layout with the top bar unpinned; other layouts keep their existing toolbar.

The native `NSTextField` is the primary address editor in this layout; the
sidebar URL row is hidden, with navigation moved to the leading glass pair. Clicking the
field or pressing Cmd+L selects the complete URL in place, opens autocomplete
immediately, and animates the text from its centered display toward the left
editing alignment. The first mouse click enters editing and returns before AppKit starts caret
tracking; subsequent clicks allow ordinary caret positioning. Address focus
retains the top controls until editing ends. Chromium's profile-aware
`AutocompleteController` supplies URL, history, bookmark, and search matches;
up to six native suggestion rows appear below the field. Up/Down selects a row,
Enter navigates the current tab and Escape restores the page address.
Cmd+Enter opens a new foreground tab. An AppKit event monitor scoped to the
focused editor handles that command before Chromium's window key dispatcher. Cmd+T retains the existing command palette. This first native
editor does not reproduce every omnibox action chip or popup accessory.

The display uses Chromium's URL formatter and security text. The leading button
opens the existing page-information bubble anchored to the glass control; the
trailing button reloads or stops the page. Profile light/dark appearance is
applied to the AppKit material and native controls. The text field supplies a
rounded focus-ring mask spanning the entire glass surface, letting AppKit render
the system focus indicator instead of outlining the inner text rectangle.

Presentation uses a Core Animation translation and AppKit opacity, sliding down
12 pt while fading in over 180 ms; dismissal reverses
that motion. AppKit's Reduce Motion preference skips the transition. A reentry
invalidates the previous completion, so an old fade-out cannot hide a reopened
surface. Public AppKit standard traffic-light buttons occupy a transparent
host with a fixed top-left resting position and no glass pill. Their reveal
tracks the top bar or left sidebar, remaining visible until both are hidden.
They appear when the top glass is presented, or when a left-aligned sidebar is
visible. A right-aligned sidebar does not independently reveal them. Existing
titlebar buttons are restored outside this layout.

An 8 pt top rail reveals the capsule. Once visible, it stays open while the
pointer remains within the window and no more than 48 pt below its bottom edge,
across the window's full width. There is no departure timer. Address editing and
open browser bubbles retain the controls during interaction. Inactive windows
hide the capsule. Browser and content fullscreen retain edge reveal; content
fullscreen temporarily treats pinned chrome as unpinned. A fullscreen-only cursor
sampler covers screen-edge mouse events consumed by AppKit. The glass follows
the menu-bar offset on screens without a notch. A visible-only cursor refresh
handles native interaction transitions without a new mouse movement.

The unmounted sidebar uses the same 48 pt retention distance into the page from
its inner edge, for both left and right placement. Leaving the window dismisses
it without the previous window-exit grace timer; active menus and keyboard focus
retain the existing interaction protections. Its top, bottom, and outer-edge
insets are 8 pt. New profiles default to 4 pt rails; existing explicit preferences
remain intact. The macOS outer window radius stays 26 pt regardless of the rail
setting, applied to both the native content and its common frame/material
container with public AppKit/Core Animation. Content radii subtract only the
configured rail thickness from that outer radius: 22 pt with a 4 pt rail. The detached sidebar radius is 18 pt (26 minus 8),
keeping its corners concentric with the window. Mounted sidebars
retain their layout. The unmounted surface has a centered,
8-dp ambient shadow at 48/255 black opacity and a 0.5-dp white highlight stroke at
96/255 opacity (one physical pixel on a 2x display). The border consumes no
layout space and the shadow does not intercept input.

## Validation

Local work and evidence are under `.work/floating-address/`.

The first distance/editor revision passed arm64 and x86_64 compilation and arm64
headless smoke checks. Native arm64 checks verified in-place Cmd+L editing,
current-tab URL navigation, search suggestions, keyboard suggestion selection,
clicked suggestion navigation, Escape, page information, internal settings URLs,
and light/dark appearance. The owner manually accepted the 48 pt distance
behavior for both the top capsule and unmounted sidebar on 2026-11-06.

The subsequent refinements use a system focus ring around the complete glass
surface and initially added a window-control pill. Native arm64 inspection verified both
and confirms Cmd+Enter opens a second tab. The owner accepted the slide/fade
animation on 2026-11-06. Fullscreen keyboard entry/exit and address focus were
exercised; screen-edge pointer reveal and synchronized floating-sidebar geometry
remain pending explicit manual acceptance. Both final architectures compile;
native arm64 and Intel under Rosetta pass the final headless smoke checks. These are incremental development
builds from the quilt-prepared workspace, not fresh CI builds of the new lock.

Strict canonical replay currently applies 62 patches affecting 21 files with
`--fuzz=0`, followed by the pinned ungoogled domain substitution, producing
byte-identical prepared source. The content-shadow refinement belongs to shared
core; the editor and floating-sidebar treatment depend on the platform UI stack.

Native Intel UI, pre-macOS-26 fallback appearance, and Reduce Transparency are not
independently verified by these development checks.

Evidence files include `build-{arm64,intel}.log`, `revision-smoke-*.json`,
`revision-replay.json`, `revision-repository-tests.log`, `revision-dark.png`,
and `refined-focus-light.png`.

The owner’s earlier acceptance applies to the preceding revision. The final
toolbar/geometry revision restores the existing 4 pt default, so it needs no
distribution preference patch. The focused field animates its containing
layer rather than resizing AppKit's separately owned field editor. Native arm64 checks confirm visible selected URL text, back/forward navigation,
extensions-menu and pinned-uBlock popovers, the app menu, and returning the
controls to the original toolbar when it is pinned. Pointer dragging and
first-click focus still need the owner's manual check.

The final dark native inspection confirms readable selected URL text and rounded
trailing glass without a rectangular backdrop. A shutdown crash was traced to
restoring native titlebar buttons after the widget delegate was destroyed. The
closing path now restores detached toolbar children before widget teardown and
avoids changing titlebar visibility in the frame destructor. An observed native
browser process exit reports status 0 after closing the final preview
(`toolbar-verified-dark/shutdown.json`). Both final architectures compile.
Final smoke evidence is `toolbar-smoke-{arm64,intel}.json`; native dark evidence
is `toolbar-final-dark.png`. The 44 repository tests and locked Git ancestry,
tree, tag, gitlink, and patch-hash validation pass.

## Native chrome feedback refinement

The native chrome refinement addresses the owner's corner, focus, sidebar, and
fullscreen feedback. It reuses Helium's existing native traffic-light group
(including its AppKit hover compatibility handling and fullscreen-overlay
suppression), animates the controls with top/sidebar visibility, and centers the
first button at the outer corner's 26 pt center. The frame and material container
share the same outer clip. Single-pane macOS layout reserves only the configured
rail, removing the additional 3 pt split-layout inset and ordinary 1 pt content
outline. Browser fullscreen, as well as content fullscreen, removes the rails.

First pointer focus selects the complete URL before AppKit starts caret tracking.
AppKit cell metrics center the address field vertically. The site-controls gear
and reload use 15 pt, medium-weight SF Symbols, matching the navigation pair.
The actual trailing Views controls keep their existing popup anchors but use
transparent button decoration and vertical centering inside the glass group.
The sidebar pin/unpin control sits on the inner edge of a fixed-height header;
attached and detached sidebar header rows share their vertical origin.

Both final architecture builds and smoke tests pass, including page loading,
JavaScript, profile persistence, defaults, and settings (Intel under Rosetta).
Reports are `polish-smoke-{arm64,intel}.json`. The first Intel test attempt failed
to create a ChromeDriver session without a new macOS crash report; the diagnostic
rerun with verbose driver logging passed. Its cause is not established, and the
first attempt is retained as `polish-smoke-intel-first*.log`.
Native arm64 light/dark inspection confirms
matching outer corner clips, 4 pt rails, readable selected URL text, matching
gear/reload symbol weights, and transparent, centered trailing controls. The
actual Lune menu opens from its glass group. Browser fullscreen inspection shows
edge-to-edge page content with no rail or ordinary outline. Closing the final
light preview reports process exit status 0. Evidence:
`polish-final-{light,dark,fullscreen}.png`,
`polish-final-{light,dark}/shutdown.json`, and
`polish-repository-tests.log` (44 passing).
Strict replay applies 62 patches with no fuzz and reproduces all 21 touched source
files after domain substitution. Locked ancestry, trees, tags, patch hashes,
component lint, and the translation registry pass.

The native tool's synthetic pointer does not reliably drive hover tracking.
First physical click, traffic-light hover/animation, sidebar pin/unpin stability,
and fullscreen top-edge overlay suppression still require manual acceptance.
Keyboard focus and fullscreen entry are verified separately; they do not prove
those pointer interactions. These remain development builds, not release acceptance.

## Pinned inputs

- Platform commit: `bd8cd36f4f25171d7669da8cc4b13843f172f158`.
- Platform tag: `inputs/floating-address-4/macos`.
- Core commit: `3c3726b5935203480de96fdb08c9839a814fc2b9`
  (`inputs/floating-address-2/helium`).
- Patch and ordered selection hashes are pinned in `manifests/patches.json` and
  `manifests/browser.lock.json`.

This is a development feature. Published builds 1 and 2 and their feeds remain
immutable and do not contain it. A new signed release must use a new build number
and repeat release gates, including native pointer interaction acceptance for the released binary.

## API evidence

- [Apple text-field HIG](https://developer.apple.com/design/human-interface-guidelines/text-fields)
- [Apple focus-ring mask API](https://developer.apple.com/documentation/appkit/nsview/drawfocusringmask())
- [Apple NSGlassEffectView](https://developer.apple.com/documentation/appkit/nsglasseffectview)
- [Apple contentView contract](https://developer.apple.com/documentation/appkit/nsglasseffectview/contentview)
- Installed Xcode 27.2 SDK: `AppKit.framework/Headers/NSGlassEffectView.h`.
