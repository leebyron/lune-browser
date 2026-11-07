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

The configured top rail (4 pt by default) reveals the capsule. Once visible, it stays open while the
pointer remains within the window and no more than 48 pt below its bottom edge,
across the window's full width. There is no departure timer. Address editing and
open browser bubbles retain the controls during interaction. Inactive windows
hide the capsule. Browser and content fullscreen retain edge reveal; content
fullscreen temporarily treats pinned chrome as unpinned. A fullscreen-only cursor
sampler covers screen-edge mouse events consumed by AppKit. The top address/navigation glass follows
the menu-bar offset on screens without a notch. Sidebar icons and traffic lights
remain at a fixed 8 pt top position when that system menu bar is exposed; their
hit-test exclusions account for the independently offset drag strip. A visible-only cursor refresh
handles native interaction transitions without a new mouse movement.

The unmounted sidebar uses the same 48 pt retention distance into the page from
its inner edge, for both left and right placement. Leaving the window dismisses
it without the previous window-exit grace timer; active menus and keyboard focus
retain the existing interaction protections. Its top, bottom, and outer-edge
insets are 8 pt. New profiles default to 4 pt rails; existing explicit preferences
remain intact. The macOS outer window radius stays 26 pt regardless of the rail
setting. The current correction updates Chromium’s existing native frame-radius
hook and keeps the content clip consistent with it; see the investigation below. Content radii subtract only the
configured rail thickness from that outer radius: 22 pt with a 4 pt rail. The detached sidebar radius is 18 pt (26 minus 8),
keeping its corners concentric with the window. Mounted sidebars
retain their layout. The original unmounted surface used a centered ambient
shadow and a half-point highlight; the current native glass correction delegates
that surface treatment to AppKit to match the other glass controls.

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

The preceding toolbar revision’s canonical replay applied 62 patches affecting 21 files with
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
first button at the outer corner's 26 pt center. That revision made the frame and material container
share the same outer clip; the later investigation below corrects the remaining
native window-shape mismatch. Single-pane macOS layout reserves only the configured
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

## Native frame and glass surface correction

Follow-up feedback showed that the preceding corner inspection was insufficient:
its 26 pt layer mask did not change the actual AppKit window shape. Source
investigation found `BrowserWindowFrame::_getCachedWindowCornerRadius` still
returning 17 pt on macOS 26+. Chromium already overrides that AppKit frame hook
and uses it for the top and bottom corners. The new patch changes that existing
override to 26 pt, retaining AppKit's fullscreen handling, rather than adding
another frame-layer mask. This is inherited Chromium compatibility code, not a
new public NSWindow corner-radius API. The redundant outer frame-layer clipping
workaround is removed; the content retains its coradial 22 pt radius at 4 pt rails.

The trailing controls previously combined their own glass window, an extra native
window shadow, and an asynchronous `orderOut` on dismissal. That completion could
hide a newly revealed group. The new implementation uses the same in-window
`HeliumGlassSurface` host as the navigation/address controls; the actual extension
and menu Views remain in a transparent, shadowless child widget. Hidden controls
ignore input, and presentation no longer queues a stale native-window hide.

The detached sidebar uses Apple's `NSGlassEffectView` with an 18 pt radius, or
`NSVisualEffectView` on older systems. Its theme-painted background and duplicate
custom shadow/outline are suppressed. Browser-owned toolbar/sidebar glyphs and
tab text use resolved AppKit semantic foreground colors; site favicons and
extension-provided artwork retain their own identity colors. The sidebar header
adds 2 pt below its controls. A single SF Symbol sidebar button stays in the
sidebar's inner corner and moves with that surface. The independently floating
toolbar pill is removed entirely. Clicking the sidebar button toggles pinning;
edge entry temporarily reveals a closed, unpinned sidebar. Detached tab rows use
AppKit selection, hover, label, and focus colors instead of the browser theme.

Chromium composites the page and sidebar together, so placing a background
NSGlassEffectView below that compositor also places it behind the page. The
correction retains a layout placeholder in the sidebar region and hosts its
existing content area in a transparent native child widget above the in-window
glass. Region ownership checks include those detached controls. The child
widget shares the browser focus hierarchy, clips to the browser during slides,
and leaves its header row available to the native controls in the parent window.
Controls return to the region before switching layouts or destroying the browser.

Windowed pointer entry follows the configured rail thickness. Fullscreen entry
requires the outermost physical pixel, using AppKit coordinates and backing
scale. Hidden/offscreen sidebar bounds no longer expand the entry area into page
content. The 48 pt retention boundary applies only after a surface is revealed.
Traffic lights move with the actual sidebar bounds rather than translating 12 pt
inside a stationary clipped host. A drag-start latch retains the top controls
until physical mouse-up; it does not assume AppKit blocks until dragging ends.
The installed AppKit `NSWindow.h` documents that `performWindowDragWithEvent:`
returns immediately and may not deliver `mouseUp`, so release is detected through
`NSEvent.pressedMouseButtons`.

The native sidebar button toggles pinning from its sidebar position. New profiles default to pinned, left-mounted sidebars;
existing explicit preferences are preserved. The detached control host forwards
blank-area context menus to the original browser menu, and the native sidebar
button also exposes that menu on right click. The visible drag region explicitly
excludes the moving sidebar button’s bounds, so pointer clicks reach its NSButton
instead of being swallowed as window drags. Accessibility activation alone did
not expose that overlap; coordinate-click testing now verifies pinning and unpinning separately from
accessibility activation. The non-client hit test also recognizes the native
sidebar host when the top toolbar is hidden; previously it returned a titlebar
hit and swallowed some clicks. The host stays above the other native surfaces,
and the detached tab widget leaves the entire button row unobstructed.

Glass materials and semantic icon colors honor Customize Lune’s explicit Light
or Dark choice. System mode follows the OS appearance. The pinned sidebar button
uses the same effective appearance as the window pane; the prior OS-only override
was a regression and is removed. Child-widget glyph colors resolve from their owning browser’s effective
Light/Dark/Device choice. Native-window appearance alone proved insufficient in
live tests. Theme refresh also compares the prior glass material appearance,
preventing AppKit’s earlier window update from skipping cached Views icon updates.
Assigning appearance directly to the existing effect was still insufficient:
live Light-to-Dark changes left its material light. The final correction recreates
only the NSGlassEffectView under the new appearance, preserving its content,
editor, alpha, and transform. Native inspection verifies Light-to-Dark-to-Light
changes of the material and glyphs; Device mode returns to the current OS scheme. The visible native toolbar and traffic-light gaps own their input
and arrow cursor instead of passing it through to the underlying page. The top
strip only enables window dragging while presented; native drag state retains
it until the initiating mouse button is released. The permanent hidden titlebar hit
test no longer makes the same page area draggable after dismissal. The drag
strip excludes a 6 pt window-edge perimeter from hit testing and arrow cursor
rectangles so it does not compete with AppKit resize cursors.

The sidebar button has a 4 pt inner margin (reduced from 6 in input 13); the tab region gains 2 pt horizontal
margin. macOS side-panel headers, including Customize Lune, have 10 pt outer
padding and a 52 pt minimum height, aligning their title and close button with
the other headers. Toolbar placement measures
actual page bounds instead of the outer rail container. In windowed mode the
inset is the difference between the content radius and the 18 pt glass radius
(4 pt at the default 22 pt content radius), making exposed corner centers align.
Fullscreen keeps an 8 pt inset. Sidebar-contained controls and traffic lights
keep a fixed vertical origin when the system menu bar overlays fullscreen.
Traffic lights belonging to the exposed top toolbar follow its menu-bar offset.
Their hit-test exclusions use the actual converted native bounds.
The detached sidebar still reserves space during
its reveal. Transparent toolbar/sidebar child widgets explicitly participate in
existing fullscreen Spaces so the controls appear with their glass backgrounds.

Validation through input 12:

- Strict patch replay passes without fuzz: 80 relevant patches, 37 final source
  files byte-identical to the prepared tree.
- Both arm64 and x86_64 compile. GN dependency checks, component patch/i18n lint,
  input/tag/tree/gitlink validation, and all 44 repository tests pass.
- Arm64 and Intel-under-Rosetta headless page execution, profile persistence,
  registered defaults, and settings checks pass. Native Intel remains untested.
- Native arm64 inspection confirms a fresh pinned-left sidebar, unpinning, the
  original sidebar options menu on right click, working trailing app menu,
  fullscreen trailing controls, and Command-L full-URL selection in the preceding
  revisions. Final arm64 coordinate-click inspection verifies unpinning while
  the top toolbar is hidden and absence of the former floating toolbar toggle.
  The material-recreation build verifies Light-to-Dark-to-Light surface and glyph
  changes, Device selection, and increased Customize Lune header spacing.
  Test previews exit cleanly with detached controls.
- The owner confirmed retention throughout a native window drag. Cursor shape, OS
  appearance switching, fullscreen edge entry, and right-side animation remain
  manual acceptance checks. Synthetic native clicks do not reliably move the
  global pointer used by the distance-retention logic; no runtime pass is claimed
  for those interactions. Earlier owner acceptance covers earlier revisions only.

Local evidence is under `.work/floating-address/`: `surfaces-validation.json`,
`revision-replay.json`, `surfaces-smoke-{arm64,intel}.json`, the build/test logs, and
`surfaces-input-check/shutdown.json`.

## Sidebar interaction follow-up

The owner accepted window-edge resize cursors and fullscreen behavior for input
12. Input 13 restores blank-area dragging and the original sidebar
options menu in the detached native content widget, on both sides. Tab controls
keep their own input handlers. A native drag retains both surfaces until the
initiating mouse button is released, including events serialized by remote_cocoa.

The detached child window starts below y=46 in browser coordinates; it no longer
adds that whole distance to the sidebar's existing 8 pt top inset. This removes
the overlap that clipped the first tab row. The sidebar toggle's inner inset is
4 pt, and the nearest top-bar glass group stays 12 pt from the popover, matching
inter-group spacing. Entering the visible sidebar's first 44 pt reveals the full
top bar in either pinned or unpinned mode. Existing distance retention applies.

Input 13 changed the main top-bar surfaces and traffic lights to fade-only
presentation. Subsequent owner testing found a separate frame animation on the
trailing icon child window; input 14 removes that remaining motion. Sidebar
slides and the system fullscreen menu-bar offset remain separate behaviors.

Validation: both architecture builds, strict no-fuzz replay (81 patches and 37
matching files), GN dependencies, component lint, lock validation, and all 44
repository tests pass. Arm64 and Intel-under-Rosetta smoke/default/settings
checks pass. Native Intel hardware remains untested. Native arm64 right-click on the pinned sidebar toggle opens
the original options menu. Detached background drag/right-click, first-row
visibility, spacing, header-hover reveal, and fade timing still require manual
acceptance because native automation cannot reliably hold the reveal cursor.
Prior acceptance does not imply acceptance of these new pointer interactions.
Local evidence: `.work/floating-address/sidebar-validation.json`,
`sidebar-smoke-{arm64,intel}.json`, and `revision-replay.json`.

## Toolbar and customization follow-up

Input 14 removes the trailing icon child window's independent vertical animation
and positions it before showing it. Icons and glass use the same destination
bounds, with opacity-only presentation. Right-side sidebar animation no longer
supplies the traffic lights' x coordinate; they remain on the left.

Fullscreen content keeps its edge shadow while a vertical sidebar is pinned.
Hovering visible left traffic lights also reveals the collapsed left sidebar.
The sidebar stays open throughout its native options menu, then resumes ordinary
pointer retention after the menu closes. The sidebar SF Symbol is 17 pt; its
inner inset is 2 pt in popover mode and remains 4 pt when pinned.

The toolbar drag strip excludes the open side-panel bounds. Customize keeps its
existing WebUI Appearance row as the first item and removes the extra native
header. A native AppKit glass close button sits alongside that row. Its scroll
content has square clipping rather than a rounded container; the outer browser
window still clips to its own rounded frame.

Validation: arm64 and x86_64 builds and headless page/profile/default/settings
smoke checks pass (Intel under Rosetta). Strict replay passes without fuzz:
83 relevant patches, 41 final files matching the prepared tree. GN dependency
checks for both architectures, component lint, locked inputs, and all 44
repository tests pass.

Native arm64 inspection confirms the existing Appearance row first without an
extra header, the native glass close working by coordinate click while the top
bar is visible, dark-mode material/glyph changes, trailing icons contained in
their glass in both sidebar layouts, right-sidebar unpinning, Command-L selection,
the pinned-sidebar context menu, and a visible fullscreen content-edge shadow.
The preview exits cleanly. Hover-triggered reveals, transient right-sidebar
traffic-light placement, fade timing, and detached context-menu retention still
require real-pointer acceptance. Scroll clipping is source-verified; the inspected
panel did not overflow, so its scrolling appearance remains a manual check.
No acceptance is inferred from earlier builds.

Local evidence: `.work/floating-address/toolbar-panel-validation.json`,
`toolbar-panel-smoke-{arm64,intel}.json`, `toolbar-panel-check/shutdown.json`, and
`revision-replay.json`.

## Sidebar sizing and fullscreen offset follow-up

Inputs 15–16 add 2 pt to each horizontal margin around pinned tabs (4 pt
region padding per side), keeping the popover's existing 2 pt padding. The
popover is 2 pt narrower at its inner edge; its outer 8 pt inset is unchanged.
Its 5 pt inner resize band uses Chromium's standard horizontal resize cursor
and drag handling on either side. Local hit coordinates replace parent-relative
coordinates, and detached style no longer disables the handle. Resize starts
from the logical stored width so repeated drags do not accumulate the visual
2 pt reduction. Cursor-based dismissal pauses during a resize drag.

In fullscreen, the detached sidebar uses the same menu-bar reveal offset as
the floating toolbar. Material, tabs, toggle, and left traffic lights move
together. Its bottom inset stays fixed as the top moves. Pinned sidebar
controls remain stationary. The child controls window preserves the header
clearance and exposed resize band after the offset changes.

A separate build-only patch adds missing direct GN dependencies uncovered by
the broader frame-target header check. These declarations do not change UI
behavior.

Validation: both architecture builds, strict no-fuzz replay (85 relevant
patches, 41 final files matching prepared source), all frame-target GN header
checks on both architectures, component lint, locked inputs, and all 44
repository tests pass. Arm64 and Intel-under-Rosetta smoke/default/settings
checks pass.

Native arm64 inspection confirms the increased pinned-tab margins and the
resize handle exposed in the detached sidebar's accessibility tree. The
accessibility resize action timed out in native automation. On November 6,
2026, the owner manually accepted inner-edge resizing on both left and right
popovers and the fullscreen popover moving down with the menu bar and top
controls in the input-16 Apple silicon preview. Width persistence across an app
restart was not part of that acceptance. The inspected preview exited cleanly
before the final preview was relaunched and left open.

Local evidence: `.work/floating-address/sidebar-sizing-validation.json`,
`sidebar-sizing-smoke-{arm64,intel}.json`,
`sidebar-sizing-gn-{Default,Intel}.log`,
`sidebar-sizing-check/shutdown.json`, and `revision-replay.json`.

## Pinned inputs

- Platform commit: `71cb42086d33308c04ec4a36bd37eecefb2f1e63`.
- Platform tag: `inputs/floating-address-16/macos`.
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
