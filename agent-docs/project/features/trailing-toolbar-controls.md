# Trailing toolbar controls

Development work for [issue #9](https://github.com/leebyron/lune-browser/issues/9),
requested November 7, 2026. The current candidate is based on accepted
`inputs/sidebar-pin-activation-2/macos`. The current local platform head is
`9b91701dcd4c3253b9555e4e7df6e2a6035f9021` (tree
`beba2a85530ca7d0e6d85ddf25a79f390f97e7f2`). The owner accepted the preceding visuals
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
and `ellipsis` for More. Active split orientation indicators retain their existing distinct artwork.

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
Extension artwork and favicons retain their own appearance.

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

## Validation and limits

`scripts/check-native-toolbar.py` extracts production symbol/color code and
compiles it against AppKit. Both arm64 and x86_64 via Rosetta pass symbol
availability, nonempty 1x/2x bitmap rendering, original-artwork fallback, floating
scope, light/dark semantic state colors, native 100 ms hover transitions and
mid-transition reversal, and pressed/disabled precedence. Its stand-ins do not exercise Skia
masking, Views layout, or real browser input.

The current arm64 and Intel browser builds pass, including the Profile animation
fix and the latest sizing, hit-target, and empty-group refinements.
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
required for that callback. Owner retry after the crash fix remains pending,
so issue #9 remains open.

The no-op Sparkle readiness fixture was restored against matching debug symbols
after rebuilding. It does not download or install an update.

Strict replay passes with zero fuzz for 92 affected patches across 42 files.
The platform patch linter passes.

Local evidence and isolated previews are under `.work/trailing-toolbar/`.
The preview includes the previously requested no-op Sparkle readiness fixture;
it does not download or install an update. No issue closure or release is implied
by these development checks.
