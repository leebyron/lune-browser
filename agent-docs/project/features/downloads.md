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

The native download control uses 16 pt medium SF Symbols. Idle uses
`arrow.down.circle`; recent successful completion temporarily uses
`arrow.down.circle.badge.checkmark`, pause uses the pause badge, and error uses
the xmark badge. Missing compound symbols use native SF component artwork.
Canceled, dangerous, and insecure downloads do not produce a success checkmark.
Completion attention retains the existing one-minute lifetime and acknowledgment
behavior. Native status badges replace the old underline and count overlays.

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

Requested November 11, 2026. Downloads is included in the registered default
`toolbar.pinned_actions` list. Profiles without a saved toolbar list show the
button immediately, including while idle. Saved toolbar lists retain their
precedence, so an explicit unpin remains effective. Customize Toolbar's existing
Reset to default action restores Downloads through the same registered default.
Download progress, completion attention, menus and temporary visibility retain
their existing behavior.

Signed platform commit `62f2f236c7fd191e6f998450a1e0ce8058bcc9ca`, retained by
`inputs/downloads-default-1/macos`, adds the focused
`helium/ui/downloads-toolbar-default.patch` above the accepted address-bar bangs
input. The core gitlink is unchanged. The development lock and patch provenance
select this default for future builds; published releases retain their frozen
inputs. No open issue specifically tracks this request.

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
