# Trailing toolbar controls

Development work for [issue #9](https://github.com/leebyron/lune-browser/issues/9),
requested November 7, 2026. The current candidate is based on accepted
`inputs/sidebar-pin-activation-2/macos`. The current local platform head is
`83fba93ff1abb4b635f044be36a24d50365200bf` (tree
`e30c02540ce97e9a7dabbab80c6ddd95a557a065`). The owner accepted the preceding visuals
on November 7, 2026. A subsequently reported Profile animation crash is fixed;
this is not in published builds 1 or 2 and is not release-accepted.

## Candidate behavior

The floating trailing group retains Chromium Views controls, command handlers,
extension artwork and badges, popup anchors, and accessible names. Browser-owned
icons use native SF Symbols where mapped. Unrecognized or specialized status
artwork falls back to the existing representation.

The owner's explicit symbol choices are `puzzlepiece.extension` for Extensions,
`slider.horizontal.below.rectangle` for site info in the native address capsule,
`rectangle.split.2x1` for Open in Split View, `square.and.arrow.up` for Copy Link,
`slider.horizontal.2.square` for Customize, `book` for Bookmarks, `airplay.video`
for Cast, `person.crop.circle` for Profiles,
`rectangle.and.text.magnifyingglass` for Search Tabs, `eye.slash` for Incognito,
`memorychip` for Task Manager, `house` for Home, `plus` for New Tab,
`globe` for internal/New Tab page tabs and missing favicons, and `ellipsis` for More. Active split orientation indicators retain their existing distinct artwork.

Browser-owned SF Symbols use 16 pt medium configuration across the native
header, sidebar pin, trailing controls, command palette, and application menus,
except Site Information and Reload/Stop, which now use 14 pt medium at the owner's
request. Their 32 pt hit targets are unchanged. Reload sits 2 pt from the
trailing glass edge, reduced from 4 pt; its trailing anchor preserves this inset
as the capsule resizes.
The Customize close symbol also uses 16 pt medium because it is a header
control. Tab and sidebar-footer close symbols use 11 pt medium weight. The owner
requested a weight increase for close icons and then all header icons, explicitly
including navigation, site info, reload, the sidebar toggle, and the trailing group.
The Profile control has a separate image path; while floating it uses the shared
symbol/state-color renderer, retaining its menu behavior and status labels.
Extension artwork and external-site favicons retain their own appearance.

Apple's [SF Symbols guidance](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)
and [toolbar guidance](https://developer.apple.com/design/human-interface-guidelines/toolbars)
do not prescribe a fixed symbol weight for glass toolbar controls. Medium is
this candidate's chosen weight, one step above regular, not an asserted HIG mandate.

Floating toolbar icons use AppKit secondary-label color, rollover and pressed
system effects, and disabled-control text color, resolved for the profile's
Light/Dark/System appearance. The initial native toolbar-bezel experiment was
rejected because it produced an outline. The revised candidate draws no bezel
or Chromium hover/ripple fill. It is not a conversion of the trailing controls
to native NSButton instances. Native Back, Forward, Site Information, and Reload
buttons use the same semantic colors. Both groups fade between normal and hover
colors over 100 ms in either direction; reversing during the fade continues from
the current color. Pressed and disabled states take precedence immediately.
Native tracking timers stop on removal and teardown.

Transferred margins are saved and restored. The floating group has 4 pt outer
padding on both sides and 2 pt gaps. The extra 2 pt previously added at the
trailing edge now belongs to the ellipsis hit target: 1 pt on each side.
Ordinary icon targets are 32 pt (34 pt in comfortable density); the icon-only
ellipsis target is now 2 pt narrower, increasing from 28 to 30 pt at standard
density. Labeled menu states
retain their normal preferred width. Image padding derives from the intended
target size rather than the previous allocated width, avoiding stale insets
when the menu chip shrinks. This alone did not resolve the owner's missing
ellipsis. Opening Customize adds a transient toolbar action; source inspection
found that the nested animated layouts report their interpolated width. While
transferred, they now use host-bounds animation mode so the outer group reserves
the final preferred width immediately; their original modes are restored on
return. The floating group also lays out pending child changes even when its
total width is unchanged. Arm64 inspection confirms the ellipsis remains visible
and opens its menu after Customize is opened. The owner subsequently reported
that this worked, requesting further visual refinements. The existing content-view
fade is preserved.

The Extensions menu button has zero layout gap before the first extension.
The container's collapsed 2 pt margins are assigned only to each extension's
trailing side, with zero margins on the menu button. This preserves 2 pt between
extensions as pins are added or reordered. Returning the controls to the ordinary
toolbar restores its original margin defaults.

An empty trailing group reports zero width and immediately hides its glass and
child input window. A recursive button check uses intended layout visibility, including actions
temporarily hidden during animation or overflow, and ignores empty containers
whose padding can otherwise reserve a sliver. Disabled buttons still count as
items. Transferring controls preserves intended visibility rather than a prior
overflow result. A single item uses a 36 pt circular glass surface and centers
the actual button, including when a nested container has asymmetric margins. The controls stay attached, so enabling an item restores the
group; the address layout also drops the inter-group gap while it is empty.

A native vertical `NSBoxSeparator` separates Back and Forward inside their
existing glass group. Both 32 pt targets move 2 pt closer to the separator
relative to the preceding preview, narrowing the group from 76 pt to 72 pt.

The address capsule maximum is half the available header region outside the
sidebar, replacing the fixed 480 pt cap. It still shrinks to the free width
between navigation and trailing controls, and recalculates as the window and
sidebar geometry change.

The owner also requested that Customize Lune expose the sidebar and header while
editing Colors or Toolbar. A separate `customize-chrome-reveal.patch` checks the
owning window's visible Customize side-panel entry, cancels collapse, and forces
both reveal targets without changing pin preferences. Ordinary cursor behavior
resumes when that entry is no longer visible. The inactive-window early hide
path also respects this hold so Customize does not lose its header on focus loss.

Customize Toolbar now uses the same SF Symbol mapping as the actual controls.
Home leads the trailing pill when enabled. The existing Back/Forward toggles
control the native navigation pill: both buttons retain the separator, one uses
a centered 36 pt circle, and neither removes the pill. New Tab controls the
sidebar row and its spacing. Collapse Tabs controls the native sidebar toggle.
When it is off on the right sidebar, the empty header is replaced by a 10 pt
top inset; the left sidebar retains its traffic-light space. The old Views pin
stays hidden while the native sidebar toggle is in use, including preference
callbacks. The Reload toggle controls the native address-capsule button and
keeps the address text bounds unchanged when hidden, preserving both the
centered display position and the leading editing inset.

A second owner crash report, from dragging a pinned toolbar action, matches the
previous preview's framework UUID. Symbolication reaches
`ToolbarButton::UpdateIconsWithColors` from `SetIconVisibility(false)` during
`PinnedToolbarActionsContainer::OnDragUpdated`. Chromium uses
`VectorIcon::EmptyIcon()` for that placeholder; its name is null. Converting the
name directly to `std::string_view` violated its non-null contract. The shared
symbol entry points now accept nullable names and return an empty result for
that placeholder, preserving Chromium's drag/reorder behavior. Native regression
checks cover both entry points with null names.

## Validation and limits

`scripts/check-native-toolbar.py` extracts production symbol/color code and
compiles it against AppKit. Both arm64 and x86_64 via Rosetta pass symbol
availability, nonempty 1x/2x bitmap rendering, original-artwork fallback, floating
scope, light/dark semantic state colors, native 100 ms hover transitions and
mid-transition reversal, and pressed/disabled precedence. Its stand-ins do not exercise Skia
masking, Views layout, or real browser input.

The current arm64 and Intel browser builds pass, including the Profile animation
fix, customization parity, and null drag-placeholder handling.
The preceding headless smoke checks pass,
including page loading, JavaScript, persisted profile data, defaults, and settings.
Native Intel hardware validation is not implied.
Toolbar and Profile header-dependency checks pass.

Arm64 preview inspection verifies the native navigation separator. Earlier
inspection verified extension popup anchoring, action dispatch, and a badge
update using a local test extension. The target-padding correction alone did
not fix the missing ellipsis. With the subsequent animation-width correction,
Appearance and Toolbar settings retain the ellipsis and clicking it opens the
Lune menu. The inactive preview retains the header and sidebar. The owner
reported that this preview looked good except for visual refinements, now
included in the rebuilt preview. The owner accepted the resulting appearance.
The complete interaction matrix remains outstanding.

The current arm64 preview also confirms that the ellipsis opens its menu after
Customize opens, with the new padding, extension spacing, and responsive address
width present. The 100 ms timing and reversal are checked by the native harness;
the owner accepted the final hover feel and extension spacing.

The latest arm64 preview confirms the 14 pt address icons and revised ellipsis
spacing. Turning off Extensions and then Main Menu removes the trailing glass
entirely. Re-enabling Main Menu restores the group, and its menu remains clickable
after Extensions is restored too. Both preferences were returned to their original
enabled values, leaving all other customization settings unchanged.

A subsequent owner report exposed newly enabled Customize actions failing to
appear. The previous empty-group check used painted visibility, and transfer
could preserve an overflow-hidden container as explicitly hidden. Both now use
layout visibility intent. Live arm64 checks confirm immediate Bookmarks and
Downloads additions, repeated removal/re-addition of all ten enabled pinned
actions, a circular single Customize control, complete removal when Customize
closes with no remaining actions, and recovery on reopening Customize. A lone
ellipsis is clickable in its 36 pt circular group. Original preference values
and action order were restored after testing. The Reload trailing inset is 2 pt.

The owner then supplied a crash report from that preview. Its framework UUID
matches the arm64 debug symbols. Symbolication locates the fatal assertion in
`AvatarToolbarButton::AnimationProgressed`, reached from `gfx::ThrobAnimation`.
The profile button's pre-existing callbacks require its identity-pill slide
animation, while enabling the new shared hover fade also sends them hover
callbacks. Both progress and completion now recognize the inherited hover
animation and forward it to `ToolbarButton`; the identity-pill path and its
unexpected-animation assertion remain intact. The native harness compiles these
production callback bodies with stand-ins and checks hover forwarding separately
from identity-pill progress, expanded completion, and collapsed completion.
Both architectures pass this regression check. In the rebuilt arm64 browser,
pointer-driven Profile-menu opening and dismissal pass, and the browser remains
responsive afterward. The owner reports being idle at the time of the original
crash, consistent with its asynchronous animation-timer stack; no click is
required for that callback. Subsequent owner acceptance of toolbar drag reordering is recorded below;
issue #9 remains open while the broader toolbar refinements are reviewed.

The no-op Sparkle readiness fixture was restored against matching debug symbols
after rebuilding. It does not download or install an update.

Strict replay passes with zero fuzz for 106 affected patches across 59 files.
The platform patch linter passes.

Local evidence and isolated previews are under `.work/trailing-toolbar/`.
The preview includes the previously requested no-op Sparkle readiness fixture;
it does not download or install an update. No issue closure or release is implied
by these development checks.

The customization/drag candidate at `a097ac04` passes both browser builds,
both native symbol harness architectures (Intel under Rosetta), focused header
dependency checks, and headless browser smoke checks on both architectures.
Live arm64 inspection confirms matching Customize symbols, Home first in the
trailing group, immediate New Tab row removal/restoration, single-button
navigation, removal when both navigation toggles are off, and restoration of the
pair. The right sidebar without a toggle removes its header, and a New Tab tab
uses the SF globe. Initial pointer automation could not target the window;
subsequent automated drag attempts left the order unchanged. The owner then
confirmed successful reordering without a crash in the final preview. The null-placeholder regression checks
pass. The owner then requested Reload visibility, fallback globe coverage,
removal of the duplicate Views sidebar button, and an 8 pt empty-header inset;
the `c568a31b` refinement builds pass on both architectures. Live arm64 checks
confirm immediate Reload removal/restoration and exactly one native sidebar
toggle when enabled, with none when disabled. Subsequent fallback-state and
8 pt spacer corrections pass both browser builds. The later 10 pt inset and
native navigation menu changes pass both browser builds.

The owner also reported the footer moving above the tabs after switching to
horizontal tabs and back. `RemoveTabStripView` previously appended its New Tab
container after the footer. `AddTabStripView` uses that container's slot, so the
next vertical strip landed below the footer. Detachment now restores the
container at the outgoing tab strip's original index, preserving header, tabs,
footer order across orientation changes. This is included in `c568a31b`.
Live arm64 inspection confirms the footer stays at the bottom after a
Vertical → Classic → Vertical round trip. The owner independently confirmed the
footer remains at the bottom on November 7, 2026.

Live inspection also exposed two details corrected in the preceding candidate.
The default favicon model is an image generator with a cached callback identity;
comparing it to a newly constructed default model never matched. `TabUIHelper`
now identifies its own cached default model and carries that state through
`TabData` to the SF renderer, preserving supplied and retained site favicons.
The zero-height right header's margin was collapsed by layout, so that revision
used an explicit 8 pt preferred height with no additional margin. Live arm64
inspection confirms the no-favicon data page uses the SF globe and
the right sidebar gains the visible 8 pt top inset. The sidebar was returned to
its original left side after testing.

The owner requested 10 pt instead of 8 pt for the empty right header, fixed
address-text spacing when Reload is hidden, and native navigation context menus.
The current candidate applies those refinements. Native right-click and
Control-click route to the original Back/Forward and Reload ToolbarButtons via
stable providers, including when those Views are reparented into a detached
sidebar. A one-use screen anchor places each existing Chromium menu beneath its
native glass button. Original history entries, commands, availability rules,
and window-local menu reveal holds are retained. Chromium's advanced Reload
menu remains available when DevTools is connected and the button is in Reload
mode. Native event-routing checks pass on arm64 and Intel under Rosetta.
Both browser builds and arm64 live menu inspection pass. Back and Forward menus list the
expected history entries and selecting them navigates correctly. With DevTools
open, Reload offers Normal Reload, Hard Reload, and Empty Cache and Hard Reload;
Normal Reload dispatches successfully. Before/after screenshots of the short
`helium://version` address confirm unchanged text position when Reload is hidden.
The 10 pt right-header top inset is visible. Reload was restored, DevTools was
closed, and the preview test page was restored. The no-op Sparkle fixture was
restored against matching debug symbols.

On November 7, 2026, the owner accepted the latest arm64 preview's 10 pt top
inset above the right sidebar's tabs and unchanged address-text position when
toggling Reload. This records visual acceptance of those refinements; the
candidate remains outside the development lock and published builds.

The next refinement adds 500 ms press-and-hold menus to native Back, Forward,
and Reload, matching Chromium's existing delay. AppKit press recognition keeps
short clicks on the normal NSButton path and consumes a recognized hold so
releasing it cannot also navigate. Right-click and Control-click remain immediate.
The recognizer checks Chromium's original menu availability before recognition
and again before beginning; without an available menu, holding and releasing
still performs the normal button action. Reload therefore retains the existing
DevTools and Reload-mode gates. Disabling or detaching the button cancels a hold;
moving outside the gesture tolerance cancels recognition.

The production AppKit button passes real event-queue regression checks on arm64
and Intel under Rosetta: short clicks, a held menu without duplicate click,
drag-out, disabling, detaching, reuse after reattachment, and normal-click fallback
when no menu is available. Strict replay passes for 107 affected patches across
59 files, and platform patch lint passes. Both browser builds pass at platform
commit `6d3880a8`. Live arm64 held clicks show the Back and Forward history menus
without navigating on release; an ordinary Back click navigates normally.
Reload's held-menu live check remains pending.

The owner then reported three follow-up interaction issues. The right sidebar's
first row overlapped the floating header's 52 pt native drag shield after the
header was replaced by the 10 pt inset. The shield now stops at the right
sidebar edge when Collapse Tabs is off, leaving actual row controls to the
sidebar's existing hit routing.

Hidden Reload now returns its 32 pt target width to the address container.
The leading field inset stays at 40 pt. Short display addresses retain their
previous centering; longer display addresses can use the reclaimed width, and
editing always uses the entire available field. The production geometry passes
native checks on arm64 and Intel under Rosetta for short text, long text,
editing, and restoring Reload.

Site Information now tracks its own bubble widget weakly and closes it on a
second activation. A window-local mouse-down monitor consumes a second click on
the icon before focus-loss dismissal can be followed by mouse-up reopening.
The monitor uses a weak owner, is removed during shutdown, and leaves other
windows and ordinary outside clicks alone. These three fixes are in platform
commit `76cd8d6e`; strict replay passes for 110 affected patches across 59 files
and patch lint passes. Both browser rebuilds pass, and the final arm64 preview is
open. Native gesture and address-layout checks pass on both architectures. Live
sidebar, Site Information toggle, and Reload hold checks remain pending: owner
interaction changed the controls during automation, followed by a click timeout.
The owner has been asked to verify the three latest refinements. The no-op Sparkle
update-ready fixture is restored against matching debug symbols.

The owner accepted the raised sidebar row interaction and reclaimed address
space on November 7, 2026, but rejected the first Site Information toggle:
it still closed on mouse-down and reopened on mouse-up. The mouse-down monitor
was insufficient when Chromium processed focus-loss dismissal first.

Platform commit `d743d0e3` replaces that attempt with widget lifecycle observation.
When the bubble hides or is destroyed during a physical press over its own icon,
the owner records a release-suppression latch. The button's action consumes that
latch instead of reopening the bubble. A mouse-up monitor clears any unused
latch after NSButton dispatch, so releasing elsewhere cannot suppress a later
click. The observer covers both ordinary and internal-page bubbles, keeps a weak
Objective-C owner, and unregisters during destruction/shutdown. Strict replay
passes for 111 affected patches across 59 files; patch lint passes. Both builds
pass. The owner confirmed on November 7, 2026 that a second click now leaves
Site Information closed after releasing the mouse.


## Reviewed commit stack

At the owner's request, the issue #9 iteration was reviewed and consolidated on
local platform branch `trailing-toolbar-reviewed`, based on accepted
`inputs/sidebar-pin-activation-2/macos`. The original `trailing-toolbar-controls`
platform branch remains at `b4d517bd` with the complete draft history. The reviewed
stack is also imported into this repository as local branch
`topic/trailing-toolbar-reviewed`, without changing component pins. Earlier
commit IDs in this document refer to that preserved history.

Three implementation simplifications retain the accepted behavior:

- The sidebar header computes its margins in one method. Comparing the actual
  margins replaces the redundant cached empty-header flag and duplicate layout
  calculation, including transitions back to the ordinary header.
- Toolbar state images share one opaque SF Symbol mask, tinted with each native
  semantic color. This avoids four separate AppKit symbol renders without
  multiplying the normal state's alpha into the other states.
- One helper wires the original Chromium menu provider to all three native
  navigation buttons. Menu lookup is separated from invocation instead of using
  a `check_only` mode, while retaining weak window ownership and menu gates.

The Site Information lifecycle observer, its release suppression, and AppKit
press recognizer remain intact: their event-ordering behavior was necessary to
fix the observed regressions. Extension artwork, semantic state colors, accepted
spacing, toggle behavior, and popup models are preserved.

Each commit adds one final-form patch and its series entry. Follow-up fixes are
folded into the behavior they correct, so intermediate commits do not first
introduce the Profile hover crash, null drag-icon crash, or rejected Site
Information implementation. Apply the stack in the listed order; it is a series
of buildable changes, not nine mutually independent cherry-picks.

| Commit | Single thesis |
| --- | --- |
| `dacfaa17` | Use native symbols and semantic hover colors for browser controls |
| `417cf7a5` | Size floating toolbar groups from intended control visibility |
| `aec23824` | Honor toolbar preferences in native navigation and sidebars |
| `f6aa0511` | Use native globe symbols for internal and default tab icons |
| `da3907f5` | Preserve sidebar footer order across tab layout switches |
| `9b1b8af1` | Keep browser chrome revealed while Customize is open |
| `5c132f5b` | Route native navigation context and hold menus to Chromium |
| `fcae8e0b` | Scale the address capsule and reclaim hidden Reload space |
| `83fba93f` | Keep Site Information closed after a second button click |

Every commit's changed C++/Objective-C implementation units passed arm64
compilation with a fresh GN generation, and each platform patch passed lint.
The consolidated series replays 108 affected patches across 59 files with zero
fuzz and reproduces the simplified
prepared source byte for byte. These checks validate the commit boundaries;
whole-browser builds are checked at the final head rather than linked nine times.

The final head builds completely for arm64 and x86_64. Native symbol/state,
Profile animation, press-menu, and address-layout regressions pass on arm64 and
Intel under Rosetta. Headless page loading, JavaScript, profile persistence,
UI defaults, and settings checks pass on both architectures (Intel under Rosetta).
The arm64 preview is open with the existing no-op Sparkle update-ready fixture
restored. These are development checks, not release acceptance.
The regression-harness extraction boundary is a separate orchestration commit,
`8950f75`, so it stops at the native button's implementation instead of capturing
unrelated menu-wiring helpers. No release input, published build, or update feed
was changed.


On the final arm64 preview, a 750 ms press on Reload with DevTools open exposes
Chromium's Normal Reload, Hard Reload, and Empty Cache and Hard Reload menu.
The menu remains open after release. DevTools was then closed. This completes
the earlier pending live Reload hold check; the common recognizer's cancellation
and short-click behavior also pass the native tests on both architectures.

## Customize temporary icon removal

Requested and owner accepted November 10, 2026. Platform commit `1cd15a9c968749af7911e609445823c3092512e6` on `remove-customize-transient-icon`, retained by signed input tag `inputs/customize-icon-1/macos`, adds `helium/ui/customize-no-transient-toolbar-icon.patch` above the preceding search-suggestions input. Customize side-panel entries now disable Chromium's ephemeral toolbar button, so opening Colors or Toolbar no longer adds a Customize icon to the trailing strip. An explicitly pinned Customize button retains its existing visibility and active state. Menu commands, panel close controls, and the existing header/sidebar reveal hold are unchanged.

The patch was developed in the prepared source with quilt, refreshed, and unmerged into the platform repository. Zero-fuzz replay matches the prepared source exactly; platform patch lint and whitespace checks pass. Both architecture builds pass. Live arm64 inspection confirms Appearance and Toolbar open without adding a Customize button and the panel closes normally. Build and preview evidence is retained under `.work/customize-icon/`. The development lock and patch provenance adopt this input for future builds. Published releases retain their frozen inputs.

The isolated ad-hoc preview initially hit a Keychain identity warning. A subsequent shell-sandbox launch (PID `91627`) aborted during AppKit application registration, before browser UI initialization; its log records Mach bootstrap permission failures. The matching debug symbols resolve the crash through `BrowserCrApplication::sharedApplication`, `RegisterBrowserCrApp`, and `ChromeMainDelegate::PreBrowserMain`. Relaunching outside the shell sandbox with Chromium's mock keychain and a fresh test profile succeeds, and the Customize panel opens without the temporary icon. These test-launch limitations do not establish a browser feature crash.

## Header context menu opens Toolbar

Requested November 11, 2026. Platform commit `92a3c352323fbe0aed6a5dd4412ff2a50852fdcf`, retained by signed input `inputs/header-customize-toolbar-2/macos`, changes the header context menu from **Customize Lune** to **Customize Toolbar**. It uses Chromium's existing localized toolbar label and `IDC_SHOW_CUSTOMIZE_CHROME_TOOLBAR`, whose existing handler selects `CustomizeChromeSection::kToolbar`. The menu delegate, profile eligibility and the main-menu appearance entry retain their existing behavior.

The two-line source change was developed with quilt, refreshed and unmerged into the platform. Focused replay against the exact prepared preimage passes with zero fuzz, zero offsets and byte parity. Platform patch lint and lock/ancestry/tree/gitlink checks pass. Both complete browser builds pass: arm64 in 161 seconds and x86_64 in 192 seconds. Native interaction on the physical Apple silicon Mac verifies the header right-click label and selecting it opens the Toolbar heading with Back, Forward, Reload and other toolbar switches. No Intel runtime or physical Intel acceptance is claimed for this change.

The incremental build workspace also contained the separately reviewed neutral tab-group candidate and the accepted New Tab button change; its patch hashes and source hash are retained under `.work/customize-toolbar-context/`. The final platform input preserves the latest accepted New Tab input and adds only the toolbar-context patch. The earlier local `3542fd6e` input was superseded before publication. No specific open GitHub issue is fully resolved by this request. The task's isolated preview was quit and its disposable app/profile and replay fixture removed after retaining concise validation records. The development lock selects this fix for future main builds; published 26.1111.2 remains unchanged.

### Header and sidebar menu scope correction

The owner found during November 11 review that the shared system-menu change also renamed the sidebar entry. Signed platform commit `7744d8734689a9bb9adb7051128b6ed825757a67`, retained by `inputs/header-customize-toolbar-scope-1/macos`, restores **Customize Lune** and its general appearance destination throughout the sidebar, while retaining **Customize Toolbar** and the toolbar destination across the header toolbar. Native header context clicks within the visible sidebar's horizontal bounds identify the sidebar, including above the first tab row. Pinned and popover sidebar sources also identify the sidebar. Each initialization passes the current source to the cached builder, so alternating menus cannot retain the preceding command.

The owner accepted the right-click behavior on the physical Apple silicon Mac. Focused zero-fuzz/zero-offset replay passes; four complete builder/widget files and both native context-routing implementations match the compiled review source. Both browser builds and focused native routing fixtures pass; Intel fixture execution uses Rosetta. The incremental builds also contain separately pending sidebar layout candidates, which this component input excludes. The preceding conditional Downloads visibility input is preserved. [Validation record](../builds/2026-11-11-header-menu-scope-validation.json) records these boundaries. No specific issue is fully resolved by this correction.

The development lock adopts the correction for future main builds. Published 26.1111.2 retains its frozen inputs. The owner's active sidebar-spacing preview and testing profile remain open; menu acceptance does not accept the ongoing spacing changes.
