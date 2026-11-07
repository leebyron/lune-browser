# Edge-to-edge macOS frame

Requested November 7, 2026. This is the owner's proposed macOS 27 styling,
not a claim that Apple mandates these dimensions. It replaces the earlier
26 pt perimeter, 4 pt gutters, content shadow and inset floating sidebar.

Current status: header/popover geometry and input-13 resize retention are accepted.
Resize cursor stability is unresolved. The owner rejected the input-14/15
interaction fixes and later withdrew initial acceptance of a synchronous-resize
A/B after further cursor flicker and invisible toolbar icons. Input 16 simplifies
the resize integration; input 17 addresses the confirmed toolbar opacity conflict.
Both architecture builds and smoke checks pass (Intel under Rosetta). The owner
confirmed input-17 icons stay visible but resize cursors still flicker while Lune
is active. Further cursor implementation is deferred at the owner's request;
[issue #5](https://github.com/leebyron/lune-browser/issues/5) records the findings,
failed approaches, retained baseline and criteria for resuming.

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
- The header region is 52 pt tall (36 pt controls plus 8 pt above and below). Native controls remain 36 pt tall, inset
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
- macOS: `d2dd4a3016b1aa58a567e1f335ceec5824d98310`.
- Tag: `inputs/edge-frame-17/macos`.
- Patches: `helium/ui/edge-to-edge-frame.patch`,
  `helium/ui/edge-to-edge-separators.patch`,
  `helium/ui/consistent-sidebar-geometry.patch`,
  `helium/ui/pinned-sidebar-native-input.patch`,
  `helium/ui/header-edge-input.patch`,
  `helium/ui/floating-address-lifecycle.patch`,
  `helium/ui/native-resize-cursor.patch`,
  `helium/ui/native-resize-cursor-and-sidebar-drag.patch`,
  `helium/ui/resize-cursor-ownership.patch`,
  `helium/ui/native-tracking-cursor-and-popover-clip.patch`,
  `helium/ui/native-frame-cursor-tracking.patch`,
  `helium/ui/native-resize-hit-routing.patch`,
  `helium/ui/live-resize-chrome-retention.patch`,
  `helium/ui/sidebar-local-content-layout.patch`,
  `helium/ui/renderer-tracking-cursor-ownership.patch`,
  `helium/ui/synchronous-native-window-resize.patch`, and
  `helium/ui/floating-toolbar-content-opacity.patch`.
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
latest menu animation and pin/unpin alignment remains pending. The owner
confirmed input-5 header-strip dragging and native edge resizing both work,
but reported resize-cursor flicker. The owner confirmed input-4 pinned blank-area dragging and right-click
menus work on November 7, 2026. The isolated Apple silicon preview
`.work/floating-address/edge-frame-simplified17/` is open with normal website
access and the preserved synchronous-experiment profile. It has no resize feature
launch override and no injected diagnostics.

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
strip. Strict replay passes across 29 relevant patches and two files.
Both architecture builds and smoke/default/settings checks pass; Intel runs
under Rosetta. Final combined replay covers 47 relevant patches and all five
touched source files. All 44 repository tests pass. The owner accepted physical resize/drag
coexistence with the widened reveal bands; cursor flicker remained.
The accepted pinned-sidebar drag/menu behavior is retained.

The following input-by-input sections describe historical experiments. Input 16
removes most cursor overrides described in inputs 6–10 and 15. Use the current
status and inputs 16–17 sections for the retained implementation.

## Native cursor and profile lifetime correction (input 6)

The window's content now reaches the native resize perimeter. Chromium's
`NativeWidgetMacNSWindow::cursorUpdate:` previously applied the content cursor
throughout that full rectangle, including functioning resize hit targets. It now
uses AppKit's existing `_resizeDirectionForMouseLocation:` predicate, already
used by Chromium's frame mouse-down routing, and delegates cursor handling to
AppKit at those targets. This changes neither resize geometry nor reveal widths.
Physical hover-cursor stability remains an owner check.

The owner also supplied an arm64 crash report after a suspected fullscreen
operation. Symbolication against the matching build's dSYM resolved its main
thread to `HeliumFloatingAddressBar::dealloc` → `AutocompleteController`
destruction → `DocumentProvider::Stop` →
`KeyedServiceBaseFactory::AssertContextWasntDestroyed`, during `windowWillClose:`.
The exact connection between the initiating fullscreen action and window close
was not reproduced. The lifetime bug itself is identified: AppKit can retain
the native editor past destruction of the profile's keyed services.

The editor now observes `OnProfileWillBeDestroyed`, whose contract guarantees
keyed services are still alive, and explicitly tears down autocomplete there.
Frame destruction also calls the idempotent shutdown method. Shutdown detaches
text and key callbacks, clears the browser weak pointer and results, and guards
a deferred finish-editing callback against an already-destroyed controller.

Strict no-fuzz replay passes across 49 relevant patches and all six affected
source files. Both architectures compile, and arm64 smoke/default/settings checks
pass. Component patch lint, translations, lock/ancestry checks and all 44
repository tests pass. Intel-under-Rosetta smoke/default/settings checks also pass for input 6.

Native arm64 checks passed: fullscreen entry (2880 × 1620 pt window), editing
with suggestions in fullscreen, private-window close with suggestions active,
fullscreen-window close with suggestions active, creation of another normal
window, and quitting with suggestions active (recorded process exit 0). The
preview was reopened afterward with normal network access. These checks do not
claim to reproduce the owner's exact initiating gesture. Evidence is under
`.work/edge-frame/cursor-*` and `.work/floating-address/edge-frame-cursor/`.

## Shared cursor ownership and initial popover dragging (inputs 7–8)

The owner reported input 6 still flickered, and that the popover background did
not drag. The window-only cursor fix was insufficient: the renderer deliberately
reapplies its web cursor on mouse moves when it differs from the system cursor,
and resets the cursor on exit. Those paths included functioning native resize
targets when content reaches the frame edge.

The shared `ui::GetWindowResizeCursor` helper uses the existing AppKit resize hit
predicate and, on macOS 15+, returns the public SDK frame cursor for that precise
edge/corner. Window cursor updates, glass mouse movement and child-window cursor
updates share it. The renderer yields native resize targets on mouse movement
and asynchronous cursor updates; its exit path also preserves the frame cursor.
The default cursor-update implementation can consult content cursor rectangles,
which is why calling `super` alone did not establish ownership. See Apple's
[cursor-update contract](https://developer.apple.com/documentation/appkit/nsresponder/cursorupdate(with:)).
No reveal or resize geometry changes in this correction.

The popover could be created before the first header reveal, storing a nil weak
pointer to the header's not-yet-created drag handler. The handler is now created
before either surface needs it and reused when the header attaches. Its common
mouse-button latch retains the popover throughout native window dragging.

Extracted production methods pass an AppKit regression probe covering all eight
native edge/corner hit directions, their matching standard frame cursor, and
normal content cursor ownership in the interior. The renderer's actual
`shouldChangeCurrentCursor` method yields all eight native targets and retains
the center. The probe uses an unshown window and replaces cursor application
with recording, so it does not move or alter the real pointer. Strict no-fuzz
replay covers 51 relevant patches and all ten affected files.
Both architectures compile; arm64 smoke/default/settings checks pass. The owner
confirmed popover blank-area dragging works, but resize cursors still flicker.


## View cursor dispatch and popover clipping (input 9)

A bounded LLDB trace of the running preview identified the remaining arrow
updates inside AppKit's tracking-area cursor-rectangle dispatch. The receivers
included `RenderWidgetHostViewCocoa`, `WebContentsViewCocoa` and
`BridgedContentView`; all inherit `BaseView`. This happens before the native
window's cursor handler. `BaseView::cursorUpdate:` and the custom native chrome
views now preserve the shared native resize cursor before delegating interior
points to normal AppKit handling. This does not change resize hit targets.

The owner also reported a clipped New Tab row in the popover. Its separate tab
window previously started below the full header region, cutting off controls
whose Views layout begins above that boundary. The child window now excludes
only the actual native buttons (8 pt top inset plus 36 pt height). Tab layout
retains its own margin. The owner clarified the complete header should be
52 pt: 36 pt buttons with 8 pt above and below. Both sidebar modes reserve that
same height, and header reveal/input regions use it consistently. The old 56 pt
specification is superseded.

Strict no-fuzz replay matches 53 patches across all 12 affected files. The
extracted production BaseView method passes all eight native resize targets
and delegates the interior to normal cursor handling, alongside the window
and renderer cursor-ownership probes. These probes use an unshown window and
record cursor changes without changing the real pointer. The arm64 build and
smoke/default/settings checks pass. Native Command-L selects the full address
and opens suggestions; page clicks work after dismissing the editor. Intel
compilation and smoke/default/settings checks pass under Rosetta. The owner confirmed the
52 pt header and popover look correct, including New Tab visibility. Resize
cursor flicker remains, so input 9 is not accepted as a cursor fix. A further
live trace is collecting cursor identity, pointer position and resize-hit
direction. The isolated preview retains the owner's sidebar preferences and
normal website access.


## Persistent frame cursor tracking (input 10)

The input-9 live trace captured AppKit's `_clearOverrideCursorAndSetArrow` and
tracking-area structural updates applying an arrow while the native resize-hit
predicate still returned a valid top-edge direction. It also captured the native
window cursor handler applying its delegate cursor at a current resize location:
the handler had been querying the older tracking-event coordinates.

The browser's existing native frame subclass now owns a persistent
`NSTrackingCursorUpdate` area, active in the key window and following the frame's
visible bounds. Its cursor handler uses the same native resize predicate and
otherwise delegates to AppKit. The window handler now uses the current pointer
position too. This supplies a cursor owner during AppKit's structural updates;
it adds no hit target, polling, or global cursor interception. It follows Apple's
[tracking-area cursor dispatch](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/TrackingAreaObjects/TrackingAreaObjects.html).

Strict replay passes across 54 patches and 13 affected files. Extracted native
methods verify one persistent cursor-update area across repeated updates,
visible-rect tracking and key-window activation, plus all eight native resize
cursors and interior ownership. A stale interior event still selects the correct
cursor at each current edge/corner location. Arm64 compilation and
smoke/default/settings checks pass on both architectures (Intel via Rosetta).
The owner reports input 10 still has inconsistent resize cursors, so this is
not accepted as a cursor fix; input 11 attempts the direct hit-routing correction
below. Its initial cursor acceptance was subsequently withdrawn.
The previous preview quit cleanly (exit 0) before this one opened. Live debugger captures are under `.work/edge-frame/cursor9-live-trace*`;
each debugger detached and left the preview running.


## Native resize hit routing (input 11)

Read-only inspection of the running input-10 window found the frame tracking
area installed and cursor rectangles enabled. At window point (550, 744) in
its 1100 by 745 pt frame, the native resize predicate returned top-edge (2),
and the frame's hit test returned `BrowserWindowFrame`. However, direct
`contentView hitTest:` returned `RenderWidgetHostViewCocoa`. NSWindow can query
the content view directly, bypassing the native frame's first refusal.

`BridgedContentView::hitTest:` now yields actual native resize points before
routing into Views, web content or floating native controls. It uses converted
view-to-window coordinates and the shared native predicate. Interior points,
nonresizable child windows and fullscreen retain the previous routing. This
adds no gutter or layout inset and preserves the accepted 52 pt header.

Strict replay passes across 55 patches and 14 files. Native AppKit probes verify
direct content hit testing yields all eight edge/corner targets and retains
interior interaction. Existing cursor, stale-event and tracking-area probes
also pass. Both architecture builds and smoke/default/settings checks pass
(Intel under Rosetta). All 44 repository tests, component lint, lock/ancestry
validation, changed documentation links and whitespace checks pass.
Live inspection of input 11 confirms the direct content hit test returns nil at
the native top resize target while the frame hit test returns BrowserWindowFrame.
The owner confirmed “cursors look great now” on November 7, 2026.

Historical input-11 cleanup retained cursor guards because native tracking dispatch,
asynchronous renderer updates, child-window cursor updates and direct content
hit testing are separate paths. No diagnostic logging is present in these
production patches, and no debugger remains attached. Temporary debugger commands,
failed captures and regenerable probe binaries were archived with byte verification
under `.work/edge-frame/diagnostics-archive/`. Successful diagnostic evidence and
the current probe sources remain available. Immutable input tags and patch history
are preserved. Those guards were subsequently superseded by input 16; profiles remain preserved.


## Retain chrome during native resizing (input 13)

The owner requested retaining any revealed header or sidebar while resizing the
window. The AppKit `NSWindow.inLiveResize` state now freezes the current native
header presentation and the Views top/sidebar reveal targets. The latter guard
is at the shared state-update boundary, so both cursor updates and a previously
queued collapse timer respect it. Layout and native control positions continue
following the resized window. Hidden surfaces stay hidden during the resize;
ordinary pointer retention resumes once AppKit ends it. Pinned layout is unchanged.
No extra timer, global input interception, or independently latched resize flag
is added. This does not modify the accepted native resize hit/cursor routing.

Strict no-fuzz replay passes across 68 patches and 16 files. Apple silicon
compilation and smoke/default/settings checks pass. Component lint, lock/ancestry
validation, all 44 repository tests, documentation links and whitespace checks
pass. Intel compilation and smoke checks also pass under Rosetta. The owner
confirmed resize retention works, then reported cursor inconsistency and drifting
sidebar tab contents during resize. This change is separate from the accepted input-11 cursor
fix and has not been published as a browser release.


## Sidebar coordinates and renderer cursor dispatch (inputs 14–15)

The glass sidebar is an AppKit surface; its Chromium Views tab controls are in
an overlaid child widget. Native frame synchronization keeps their windows aligned,
but tab layout previously subtracted independently updated screen origins. During
live resize those origins can represent different native/compositor frames.
Input 14 passes the clipped child-widget origin in sidebar coordinates and lays
out the tab contents relative to it, avoiding that cross-window conversion.
It preserves slide clipping, fullscreen offsets, and existing tab interactions.

A subsequent native trace confirmed direct content hit testing still yields the
native resize edge, and live-resize state resets on release. Resize cursor updates
still competed with renderer/page cursor updates and AppKit structural cursor
resets. Multiple native frame tracking regions also appeared in a plain unshown
AppKit window after resizing, so their presence alone is not a Lune-specific bug.

Input 15 replaces the renderer's static full-visible-rect cursor registration
with a single cursor-update tracking area. It resolves page-versus-resize ownership
at dispatch time and explicitly applies the native resize cursor on mouse moves.
Asynchronous renderer updates continue yielding native resize points. It adds no
polling timer, global cursor interception, or new private AppKit geometry API.

Strict replay passes across 70 patches and 17 files. Extracted production methods
in an unshown AppKit probe choose all eight native resize cursors plus the interior
page cursor after four window-size changes, with one renderer cursor tracking area.
Existing native hit-routing and stale-event checks also pass. The probe records
cursor choices without setting the real pointer. Apple silicon compilation and
smoke/default/settings checks pass. The previous preview quit cleanly (exit 0)
and the updated preview retained its profile. Intel compilation and smoke checks
also passed under Rosetta. The owner rejected both interaction fixes: cursor
flicker and sidebar content drift persisted. Input 16 reverses these experiments.


## Simplify resize integration (input 16)

Chromium already provides a synchronous native resize path through
`features::kAsyncLiveResize`. Disabling that feature makes the existing native
window bridge synchronize the compositor transaction during resize. An input-15
preview launched with `--disable-features=AsyncLiveResize` initially received
owner acceptance for sidebar alignment and edge cursors. Further use showed
cursor flicker remained and the trailing toolbar icons could disappear after
fullscreen while still responding to clicks. This is not cursor acceptance.

Input 16 selects that existing synchronous path by default and removes 183 lines
of speculative cursor guards, custom tracking and the failed sidebar-local
coordinate layout (25 lines added). It restores upstream cursor handling and
retains only direct content hit-test refusal at AppKit resize points, plus the
separate accepted live-resize retention. It does not port the Chromium tab strip
to AppKit. Synchronous rendering can block the UI thread while awaiting a frame;
no performance improvement is claimed.

Strict no-fuzz replay passed across 72 patches and 18 files. An unshown native
probe verifies all eight native resize hit targets at five sizes, interior
interaction and nonresizable/nil exclusion. It does not test real pointer cursor
stability. Arm64 compilation, component checks, lock validation and 44 repository
tests passed. Input 16 was not separately launched before the toolbar fix.

## Separate toolbar fade from compositor visibility (input 17)

Native inspection of the failing synchronous preview found the trailing
102 by 36 pt child window ordered visible, with content alpha 1 but window
alpha 0. The controls remained accessible and clickable. Chromium's window
bridge temporarily sets NSWindow alpha while waiting for a correctly sized
compositor frame, saving and later restoring its previous value. Lune also
animated that same alpha and set it to zero immediately before ShowInactive.
A delayed compositor frame can therefore restore Lune's stale zero.

The toolbar now animates its content view alpha; Chromium retains exclusive
control of the child window's visibility alpha. Fade timing, click suppression
while hidden, positioning, and native glass remain unchanged. No debugger stays
attached and no diagnostic library is loaded in the preview.

Strict no-fuzz replay passes across 73 patches and 18 files. Arm64 compilation,
smoke/default/settings checks, component lint, lock validation, all 44 repository
tests and documentation-link/whitespace checks pass. The native resize-hit probe
passes with WindowServer access; its sandboxed execution could not validate the
native targets. This probe does not establish pointer-cursor stability.

Native arm64 checks show all three trailing icons after fullscreen entry and
exit, both when the toolbar hides during transition and when the editor retains
it. The trailing menu opens correctly. Post-transition inspection confirms the
child window alpha stays 1 while content alpha handles visibility. Both debugger
inspections detached. The previous preview exited cleanly (status 0), and the
updated preview is open with the preserved profile. Intel compilation and
smoke/default/settings checks pass under Rosetta. The owner confirmed the icons
stay visible; resize cursors still flicker while Lune is active. Cursor work is
paused at the owner's request and tracked in issue #5.

Eight obsolete or unused diagnostic helpers were archived and byte-verified,
including the never-loaded tracing dylib. Successful evidence, current probes,
profiles and build caches are preserved. Cursor flicker remains a separate
unresolved issue; no speculative cursor override is added for this toolbar fix.
