# Floating Media Controls

Candidate for [issue #15](https://github.com/leebyron/lune-browser/issues/15),
based on the reviewed issue #9 stack at
`83fba93ff1abb4b635f044be36a24d50365200bf`.
The signed platform commit is
`2992b61939566c5325445d343322893c8dbb3d5e` (tree
`fd39835d9e86f8ac2d891b0427ed85fd5054bd6e`), imported locally as
`topic/media-toolbar-controls`. Root validation and documentation live on
`media-toolbar-controls`. No development lock, input tag, release, or update
feed has changed. Owner acceptance is pending.

## Change

The sidebar attachment path prohibited Media Controls even after its original
button moved into the floating action window. The controller now permits the
button when that host is attached and its preference is enabled. Attachment and
restoration reevaluate the policy, so an existing session becomes available
immediately and classic layout retains its original behavior.

The original media control moves before Home in the floating group; the saved
restore order remains unchanged. The toolbar records the concrete owning View
during construction: either the standalone Views button or the WebUI toolbar
host. It never casts the abstract MediaToolbarButton interface to a View.
The default, enabled Views backend is the one tested in the browser. The
experimental WebUI renderer remains disabled; its whole host can be ordered
safely, but its internal renderer layout and artwork are not converted or
runtime-accepted by this patch.

All three media vector-icon aliases map to `waveform` through the existing
native renderer. This also changes Customize Toolbar's Media Controls icon.
It retains the existing 16 pt medium configuration and semantic interaction
colors. No new media button, service, timer, playback handler, or dialog is
introduced. Chromium's media controller continues to determine active, frozen,
paused/resumable, and open-dialog availability. Existing Show/Hide preferred-size
notifications resize the glass and input window.

## Verification

- Strict replay: 109 relevant patches across 59 source files, zero fuzz, final
  source byte parity. Platform patch lint passes.
- Full arm64 and x86_64 browser/chromedriver builds pass.
- UI/settings/profile-persistence smoke checks pass on both architectures;
  Intel runs under Rosetta, not native Intel hardware.
- `scripts/check-media-toolbar.py` compiles the production controller methods,
  visibility policy, and floating ordering block against isolated manager/view
  fixtures. Both architectures pass preference changes, host attach/restore,
  active/frozen/open-dialog transitions, repeat calls, owner ordering, and
  observer teardown. It does not substitute for browser integration tests.
- `scripts/check-native-toolbar.py --symbols-only` passes both architectures,
  including all three media aliases, 1x/2x image bounds, and light/dark semantic
  colors. The full harness was also attempted twice on arm64; its unchanged
  short-click fixture reported zero delivered clicks and aborted before the
  symbol checks. No full gesture-harness pass is claimed for this candidate.

Live arm64 inspection with a local WAV/Media Session fixture verifies:

- Eligible playback reveals waveform before Home; a background session keeps
  the button available. Two playing tabs produce two independently controllable
  entries in the existing media dialog.
- Pause and Play change the actual audio element state. Paused sessions remain
  resumable. Closing one tab and ending the last session removes the button.
- The actual Customize toggle hides/restores the button immediately, including
  while media is playing. Its waveform artwork matches the toolbar.
- A media-only group is a centered 36 pt circle. Ending the last session removes
  that group; starting another session restores it.
- Left pinned and right unpinned sidebars, classic-to-vertical restoration,
  fullscreen dialog opening, and Light/Dark/Device appearance switching work.
  The media popup stays anchored to the original control and the revealed
  header remains visible while interacting with its playback actions.

Existing toolbar drag/reorder implementation is unchanged. No new drag test or
experimental WebUI-toolbar runtime test is claimed. The preview is
`.work/media-toolbar/Lune Media.app`, with isolated profile and local test audio;
the paused dialog was left open for owner review.

Local logs and reports are under `.work/media-toolbar/`: `replay.json`,
`build-{Default,Intel}.json`, `symbols-{arm64,intel}.log`,
`native-arm64{,-retry}.log`, and `smoke-{arm64,intel}.json`.

```sh
python3 scripts/check-media-toolbar.py .work/chromium-158/macos/build/src --arch arm64
python3 scripts/check-media-toolbar.py .work/chromium-158/macos/build/src --arch x86_64
python3 scripts/check-native-toolbar.py .work/chromium-158/macos/build/src --arch arm64 --symbols-only
python3 scripts/check-native-toolbar.py .work/chromium-158/macos/build/src --arch x86_64 --symbols-only
```
