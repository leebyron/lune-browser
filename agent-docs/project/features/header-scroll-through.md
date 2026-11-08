# Scroll through the floating glass header

Issue: [#16](https://github.com/leebyron/lune-browser/issues/16).

## Behavior

The local candidate forwards wheel events over the visible floating header to the
content beneath the pointer. Address, navigation, trailing actions, and header
gaps share this route. Click hit testing, native dragging, editing, and menus
retain their existing implementations. The receiver is selected from the visible
content containers, including split panes and docked DevTools, rather than from
the active tab alone.

The route is limited to the owning browser window and its trailing controls
window. Sidebar bounds, other popup windows, native sheets,
modal-blocked WebViews, and active native/menu reveal holds are excluded. Views
hit testing inside each content container protects content overlays before the
native receiver is selected. Fixed-height autocomplete rows consume their wheel
events locally instead of bubbling them to the page. Momentum retains the last
forwarded receiver and checks that it is still attached to a current visible WebView.

`HeliumHeaderScrollRouter` owns a local AppKit wheel monitor, removed on toolbar
reset and frame destruction. It delivers the original `NSEvent` directly to the
content receiver, then consumes the overlay event. This preserves precise deltas,
modifiers, phase, momentum, and timestamp without event synthesis or redispatch.
Chromium's event builder translates from the source event window to the target
view. Its Cocoa renderer also completes wheel-end cleanup on direct delivery if
the local end monitor has not already run.

## Provenance

Developed in the prepared Chromium 158 tree with quilt, as
`helium/ui/header-scroll-through.patch`, then unmerged into the macOS component.
The signed platform commit is `d0c49b0adb64fc3c445e1434b49e4b5804d05cc6`,
available locally as `topic/header-scroll-through`. It is based on the accepted
appearance stack at `622ccfac` (`topic/chrome-appearance-reviewed`), including reviewed toolbar and
media controls. It does not change the development lock or published binaries.

## Validation

The isolated native fixture compiles production routing, coordinate conversion,
and renderer wheel-end methods. Both arm64 and x86_64 (under Rosetta) pass:

- Source/target window conversion and same-window coordinate preservation.
- Original precise and discrete event delivery, including modifiers.
- Momentum receiver retention and completion, cancellation, other-window and
  missing-target exclusions, click pass-through, detach, and monitor teardown.
- Renderer cleanup both when a local monitor runs first and when forwarding
  consumes the event before that monitor can run.

Native appearance regressions also pass on both architectures. Strict zero-fuzz
replay of 53 relevant patches reproduces all five changed source files. Platform
patch lint passes. The Chromium wheel-builder regression test compiles for both
architectures; the full Chromium unit-test executable was not run.

Both browser builds and isolated page-loading, persistence, UI, and settings
smoke checks pass (Intel under Rosetta). Live arm64 checks with trusted native
wheel input confirm:

- Address editing, navigation, trailing controls, and header gaps scroll the page.
- A trailing control in its child window delivers the correct page coordinates.
- A nested scroller under the header receives the wheel instead of the page body.
- Each split pane receives scrolling under its own header area, including the
  inactive pane, with coordinates relative to that pane.
- Autocomplete rows consume scrolling; the top address row still passes it through.
- An extension popup opens normally and keeps its wheel events off the page.
- Fullscreen navigation controls pass wheel events to the page.

An isolated browser debug trace also confirmed that the local monitor invokes the
router and consumes the forwarded event. The final fixture recorded exactly three
page events from three header scrolls, with none from autocomplete or the popup.
Native hardware trackpad feel and native Intel acceptance remain unverified.
Docked DevTools, modal exclusions, and pinned-sidebar behavior are source-reviewed
but have not received live interaction checks for this candidate.

```sh
python3 scripts/check-native-header-scroll.py .work/chromium-158/macos/build/src --arch arm64
python3 scripts/check-native-header-scroll.py .work/chromium-158/macos/build/src --arch x86_64
```

Local logs, replay results, test page, and isolated preview are under
`.work/header-scroll/`.
