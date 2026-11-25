# Download menus and native progress

Tracked in [issue #22](https://github.com/leebyron/lune-browser/issues/22).
The owner accepted the final native preview on November 9, 2026 and authorized
focused commits, publication, and adoption in future main builds.

## Behavior

A menu anchored to the header toolbar reveals and retains that header for its
lifetime, including the automatic download-completion menu. Anchor creation and
highlighting share the hold, so queued collapse and activation changes cannot
hide the header under an open menu. The final release resumes normal retention;
overlapping menus keep independent holds. Sidebar menus retain their existing
behavior, and pinning preferences do not change.

The native download control uses a 15 pt medium SF Symbol in a 36 pt target.
Idle uses `arrow.down.circle`. A new completion adds the checkmark badge,
pause uses the pause badge, and error uses the xmark badge. Shift the top-right
badged symbols 1 pt right and up to align the main arrow with the unbadged glyph.
Missing compound symbols use native SF component artwork.
Completion attention retains the existing one-minute lifetime and acknowledgment
behavior. Native status badges replace the old underline and count overlays.

When a download starts, show a 24 pt indicator for 380 ms. It travels up to
48 pt right with an ease-out and curves up into the toolbar button as it
fades. Keep the floating toolbar visible for at least one second after the
start cue, even when Reduce Motion suppresses the animation.

Downloading uses `arrow.down.circle` with no clock. Its original ring is a 25%
opacity track with an opaque completed portion, clockwise from twelve o'clock,
and rounded ends. The renderer draws the original configured SF artwork once
and applies an opacity mask to its unfinished ring. A filled angular sector
preserves the original ring's full inner and outer edges; a separately stroked
arc had clipped those edges and was rejected during visual review. At 100%, the
result matches the original SF symbol exactly.

The physical floating toolbar host identifies native header controls because
the inherited sidebar-address preference can remain enabled in that layout.
Other toolbar layouts retain their existing Chromium rendering.

## Native Downloads popover

On macOS, Downloads opens below the toolbar button in the shared AppKit
popover host. AppKit positions the arrow on the top edge and shifts it
toward the trailing end when screen space requires the popover to move
sideways. Keep the anchor and toolbar visible throughout the popover's
lifetime, including when it opens automatically after a download or the
pointer moves into the list. Release the hold on dismissal so the configured
toolbar visibility resumes.

The main page starts with the download rows and ends with **Show All
Downloads**, which opens the downloads page. Align its label with the
file icons above it. Use compact spacing for file icons and Finder artwork
for completed files, with a file-type fallback.
Use the same subtle hover color as Site Information for rows that open a
file or a security subpage, and for the footer. Apply the inset rounded
highlight immediately and retain the normal text colors. Keep the row
background clear on hover for in-progress, paused, canceled, and other rows
without an openable file or subpage. Use regular-weight text, with the
filename larger and darker than its status. Keep each label on a single
line and fade its trailing edge when it runs out of room. Reserve space
for quick actions while their buttons are visible.
Display the “Opening in” countdown without a trailing ellipsis.
Keep **Show in Finder** visible whenever it is available. Use the 13 pt `folder`
SF Symbol in the filename's foreground color at 70% opacity in a 36 pt circular
button. Hovering Finder brings the symbol to full opacity, highlights only that
button and replaces the status text with **Show in Finder**. This replaces
the hover tooltip. The button keeps its accessible action name.

The in-progress row uses 13 pt SF Symbols in 36 pt targets for Pause, Resume
and Cancel. Overlap their adjacent edges by 8 pt and split pointer input at
the midpoint. Hovering an action highlights only its circle and replaces the
status subtitle with **Pause Download**, **Resume Download**, or
**Cancel Download** in place of a tooltip. Move the
progress bar 1 pt up within the same row height. Canceled rows use the
`x.circle` SF Symbol.

The signed platform input `inputs/downloads-popover-2/macos` selects the reviewed native popover, download-start cue, and opening countdown for future main builds. [Downloads and browser chrome validation](../builds/2026-11-24-downloads-popover.json).

## Published source and build inclusion

The platform branch `downloads-menu-status-icons` contains three signed,
single-thesis commits, each changing its own patch and series entry:

- `8ee649b31ad027d895a084d4c735d5af5d2fd010`: header reveal and menu lifetime.
- `f21733751f219d5406a1b7f1ad8ee5e30be0f0cd`: SF status badges and state aggregation.
- `e631e3559ca1aba129c0446c06460da4e0493bbb`: native SF ring progress.

The signed permanent input `inputs/downloads-1/macos` selects the final commit.
The development lock and ordered patch manifest adopt it for both arm64 and
x86_64. Its parent is the current main input
`c4f0680e7b37bc5585624b357eba827da88d8647`, preserving the separate Dock-prompt
removal and older-macOS fixes. Existing frozen release inputs remain unchanged.

## Validation and limits

The patches were refreshed through quilt and unmerged into the platform stack.
Strict replay with zero fuzz and zero offsets reproduces all 15 accepted source
files byte-for-byte. Platform patch lint and GN dependency checks pass. The newer
Dock-prompt patch changes separate source files and remains in the series.

Full arm64 and x86_64 browser/chromedriver builds pass for the accepted downloads
source. Focused extracted-production fixtures cover status precedence, successful
completion and acknowledgment, timer expiry, pause, failure without an end time,
cancellation, unsafe downloads, mixed states, scanning, fullscreen deferral,
overlapping menu holds, final release, and browser destruction. Native rendering
fixtures pass on arm64 and x86_64 under Rosetta, including track opacity,
monotonic progress, exact SF geometry at 100%, and full ring width at 25%.

Live arm64 checks confirm automatic completion reveals the hidden header,
dismissal permits hiding, and a manually opened download menu retains the header
during transfer. Pause exposes Resume; cancellation clears active progress; a
truncated response produces the error state. The owner accepted the final ring
thickness and inner radius in the identified Lune Downloads Test 5 preview.

Builds used the prepared Chromium 158 development tree; the evidence does not
claim a clean frozen release build or a new signed/notarized browser release.
Native Intel hardware and pre-glass macOS runtime acceptance remain unverified.
The separate Dock removal was validated by its own changed-unit checks rather
than rebuilding the combined browser after that disjoint patch was added.

## Default toolbar visibility

Downloads is unpinned by default for future builds. The owner requested this
restoration on November 11, 2026 after confirming that disabling its toolbar
setting only removes persistent pinning. A new download still requests temporary
visibility independently of the pin state. Existing progress, completion/menu
attention and automatic hiding remain unchanged. Saved toolbar lists retain
precedence, including explicit pins; Reset to default leaves Downloads unpinned.

Signed platform commit `e262732c9ad7afb477ba7f7285eea3972591363a`, retained by
`inputs/downloads-conditional-default-1/macos`, retires only the standalone
`helium/ui/downloads-toolbar-default.patch` and its series entry from platform
input `92a3c352323fbe0aed6a5dd4412ff2a50852fdcf`. The development lock and patch
manifest select the restored default. The core gitlink and published release
inputs are unchanged. No specific open issue tracks this request.

Source inspection confirms that `DownloadDisplayController::OnNewItem()` updates
the display state; in-progress downloads call `ShowToolbarButton()`, and
`DownloadToolbarUIController::Show()` requests ephemeral visibility through
`ShowActionEphemerallyInToolbar()` without checking the pinned preference. Its
existing `ButtonShowsForDownloadingItems` browser test covers that behavior;
that browser-test binary was not built or run for this change.

A focused reverse replay with zero fuzz and zero offsets restores the preference
registration file byte-for-byte to the source built in published 26.1111.2.
Neither remaining selected component patch series touches that file. Platform
patch lint, lock ancestry/tree/gitlink/patch-hash validation and repository checks
pass. No new native rebuild or headed interaction check is claimed for this
patch retirement. Concise source and replay evidence is retained under
`.work/downloads-conditional-default/`.

### Earlier pinned-default change

Requested earlier on November 11, 2026. This superseded change included Downloads
in the registered default `toolbar.pinned_actions` list. Profiles without a saved
toolbar list showed the button immediately, including while idle. Saved lists
retained precedence, and Reset to default restored Downloads. Progress, completion
attention, menus and temporary visibility were unchanged.

Signed platform commit `62f2f236c7fd191e6f998450a1e0ce8058bcc9ca`, retained by
`inputs/downloads-default-1/macos`, adds the focused
`helium/ui/downloads-toolbar-default.patch` above the accepted address-bar bangs
input. The core gitlink is unchanged. The development lock and patch provenance
initially selected this default, which was later retired as described above.
Published releases retained their frozen inputs. No open issue specifically
tracked this request.

The preference change was developed with quilt from the prepared source,
refreshed and unmerged into the platform stack. Strict replay uses zero fuzz and
zero offsets and reproduces the compiled source byte for byte. Platform patch
lint and locked ancestry, tag, tree, gitlink and patch-hash validation pass.

Both full browser/ChromeDriver builds pass. Disposable-profile runtime checks
pass on native Apple silicon and x86_64 under Rosetta: a fresh profile includes
Downloads, an explicitly empty pinned list survives a restart, and Settings'
Reset to default restores Downloads. All 73 repository tests, workflow safety
checks, documentation links and whitespace checks pass. These checks do not
claim native Intel hardware validation, a headed visual review, a linked
Chromium browser-test suite, or a new browser release. Concise build/replay and
runtime reports are retained under `.work/default-downloads/`; task profiles and
isolated quilt/checkout artifacts are removed after publication. The shared
prepared Chromium source and incremental build outputs remain available.
