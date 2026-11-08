# Sidebar pin activation

Requested November 7, 2026; tracked in [issue #10](https://github.com/leebyron/lune-browser/issues/10).

## Behavior

The sidebar pin/toggle remains an enabled native SF Symbol button. It uses
`NSColor.controlTextColor` when its own window is key and the application is
active, and `NSColor.disabledControlTextColor` otherwise. These semantic colors
follow the button's effective appearance. The action, pinning preference,
left/right symbol, layout, and reveal animation are unchanged.

The previous borderless `NSButton` did not adopt the inactive treatment that
AppKit applies to the native traffic lights. A small `HeliumSidebarPinButton`
subclass observes its owning window's become/resign-key notifications and the
application's become/resign-active notifications. The app check also handles an
inactive application whose window still reports itself as key. It updates on
attachment and notifications, without waiting for pointer movement or a timer.

Block observer tokens are owned by the button, and callbacks capture it weakly.
Moving to another window unregisters the old owner first; detachment and teardown
remove the observers. This leaves AppKit's own button observers intact.

## Input and validation

- Base: accepted `inputs/menu-retention-2/macos`.
- Input: `inputs/sidebar-pin-activation-1/macos`, commit
  `ed6847b8cc1cb9c2a604c03070ef75d211280cbd`.
- Patch: `patches/helium/ui/sidebar-pin-activation.patch`.
- Development only, not in published builds 1 or 2 and not release-accepted.

Strict no-fuzz replay passes across 63 relevant patches and 24 files in the
combined menu/pin validation set, reproducing prepared source exactly.

`python3 scripts/check-native-sidebar-pin.py .work/chromium-158/macos/build/src`
compiles the exact production button class with native AppKit and fixture app/
window activation states. Add `--arch x86_64` to run it under Rosetta. Both
architectures pass attachment, window/app activation, unrelated-window isolation,
reparenting, light/dark semantic color selection, enabled state, detachment, and
observer teardown. The test does not claim visual acceptance of a real window.

Arm64 and Intel browser builds pass. The arm64 startup/page/JavaScript/profile
persistence smoke test passes. Component patch/translation lint, locked-object
validation, and all 44 repository tests pass. The Intel production button class
was executed in the native regression harness under Rosetta; a separate full
Intel browser smoke was not run for this color-only change.

In the real arm64 browser, read-only native inspection confirms active window/app
state selects `controlTextColor`, app deactivation selects
`disabledControlTextColor`, and reactivation restores `controlTextColor`, with the
button enabled throughout. Opening a second Lune window gives the first window
inactive tint and the second active tint simultaneously. The extra test window
was closed afterward. Inspection is recorded in `preview/activation.log`; no
debugger remains attached.

The preview is `.work/sidebar-pin-activation/Lune Sidebar Pin.app`, using an
isolated profile under `.work/sidebar-pin-activation/preview/`. Its sidebar is
pinned for comparing the pin button with the traffic lights. The requested
no-op Sparkle update fixture is restored. Owner visual acceptance is pending;
this is not a claim of a complete fullscreen/left/right appearance matrix or
native Intel hardware acceptance.

Evidence is under `.work/sidebar-pin-activation/`; the prepared-source replay
also includes the preceding menu-retention changes and is recorded under
`.work/menu-retention/`.
