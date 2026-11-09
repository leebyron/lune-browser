# Older macOS window corners and fallback surface edges

Status: owner report and source investigation, 2026-11-09. No browser patch or
replacement binary has been produced from this investigation. Published
26.1109.1 artifacts remain immutable; fixes belong in a subsequent release.

## Owner report

On the Intel Mac previously identified as macOS 13.7.8, the owner reports that
downloading worked and the fallback glass UI looks good overall. Two visual
problems remain: transparent gaps at the window corners, and insufficient
separation between borderless fallback controls and the page underneath.
Safari offered the architecture chooser rather than detecting Intel.

This is native Intel owner feedback, not an independently reproduced test.
It does not establish the outstanding update, restart/persistence, wrong-CPU
update rejection, or second Intel Mac checks. Do not promote those acceptance
fields to passing based on this report.

The owner explicitly wants the native-feeling smaller window radius on older
macOS. Preserve the OS frame shape; match Lune's content to it. Do not force the
newer radius onto older window frames. Add a thin adaptive edge to fallback
control surfaces, similar to the existing sidebar/content separator.

## Source findings

Inspected the prepared release source and platform input
`1cabd52145c9dc2ef1b3459c71b0133a81b6c4b4`, with core input
`49bdc572bee38436250f9058351c8a328cd8c8ad`.

- `chrome/browser/ui/views/helium/frame_corner_radius_mac.mm` returns 16
  unconditionally. The browser's restored window/content clipping uses this
  helper, including the native root clip in `browser_frame_view_mac.mm`.
- `components/remote_cocoa/app_shim/browser_native_widget_window_mac.mm`
  overrides `_getCachedWindowCornerRadius` to 16 only on macOS 26+. Earlier
  systems still use the superclass's native frame radius. This mismatch explains
  the reported gap; an older-system pixel measurement is still pending.
- Core `patches/helium/ui/frame-radius-helper.patch` originally returned 17 on
  macOS 26+ and 12 otherwise. Lune's `glass-focus-and-frame-geometry.patch`
  replaced that conditional with 26; `edge-to-edge-frame.patch` later changed
  it to 16, retaining the lost older-system distinction.
- In `browser_frame_view_mac.mm`, `HeliumGlassSurface` uses
  `NSGlassEffectView` on macOS 26+ and a rounded `NSVisualEffectView` with
  `NSVisualEffectMaterialPopover` on older systems. The fallback has no border.
  The additional header shadow is also gated to macOS 26+.
- `HeliumSidebarDivider` already draws `NSColor.separatorColor` at
  `1 / backingScaleFactor` points. This supplies an existing semantic-color and
  physical-pixel convention for the requested fallback edge.
- Command-T in `chrome/browser/ui/helium/helium_command_bar_view_mac.mm` has a
  separate `NSVisualEffectView` fallback. Include it in the surface audit;
  changing only the shared header host would not cover all fallback surfaces.

## API availability and proposed correction

Apple's SDK declares `NSGlassEffectView`, including its `cornerRadius`, available
from macOS 26. This controls a **glass view**, not the outer `NSWindow` frame.
Lune's outer-frame adjustment uses an inherited Chromium private AppKit hook.
Chromium intentionally leaves that hook at the superclass value before macOS
26. Neither this code nor the public glass API establishes a first OS version
where arbitrary window-frame radii became a supported public API.

For the supported systems, use the following provisional content-radius policy:

| System | Native frame policy | Lune content-radius policy |
| --- | --- | --- |
| macOS 13–15 | Preserve AppKit's frame | Restore Helium's 12 pt fallback, subject to native visual verification |
| macOS 26+ | Preserve the currently accepted 16 pt Lune frame override | Match at 16 pt |
| Fullscreen | Preserve existing fullscreen frame behavior | No rounded content clip |

The 12 pt value is inherited Helium implementation evidence, **not an Apple
contract or a measurement of every older release**. Verify all four corners on
the owner's macOS 13 machine. If its frame differs, measure it and update the
fallback rather than inventing per-version constants. macOS 14/15 remain
unverified. Keep the single helper shared by content clipping and related
geometry, and check maximized/fullscreen transitions separately.

For fallback surfaces, use an inside hairline following the existing shape:
one physical pixel (0.5 pt at 2x, 1 pt at 1x), with the resolved semantic
separator color as the initial appearance. Outline each surface/group, rather
than every icon within a group. Cover navigation, address/results, trailing
controls, Customize close and Command-T; retain the square floating sidebar
shape. The edge must not add layout inset, intercept events, or duplicate the
pinned sidebar separator. Keep native macOS 26+ glass treatment unchanged.

Use public AppKit/Core Animation drawing; no new private API is needed for an
outline. Resolve the edge color again when effective appearance changes (a
stored CGColor is not dynamically adaptive), and update its physical-pixel width
when the window moves between display scales. Verify Light/Dark/System,
Increase Contrast, inactive windows, pale/dark page backgrounds, focus and
result expansion. Visual acceptance on the actual older OS is still necessary.

## Safari download selection

The website only selects an architecture automatically when
`navigator.userAgentData.getHighEntropyValues(['architecture'])` returns `arm`
or `x86` for macOS. Missing/withheld values retain both explicit downloads.
Legacy `MacIntel` or `Intel Mac OS X` strings are not trustworthy CPU evidence.
WebKit's current implementation explicitly returns an empty architecture string;
older Safari can lack the API entirely. The owner's chooser result is consistent
with this design; the exact Safari version/API response was not captured.
Keep explicit choice instead of misdirecting Apple silicon users based on the
legacy Intel string.

## Primary references

- [Apple NSGlassEffectView](https://developer.apple.com/documentation/appkit/nsglasseffectview)
  and [glass cornerRadius](https://developer.apple.com/documentation/appkit/nsglasseffectview/cornerradius).
  Availability verified against the installed Xcode 27.2 AppKit SDK header.
- [Chromium native window implementation](https://github.com/chromium/chromium/blob/main/components/remote_cocoa/app_shim/browser_native_widget_window_mac.mm):
  private frame hook and deliberate pre-26 superclass fallback. Online main is
  a moving reference; Lune's inspected release-input identity is recorded above.
- [Apple CALayer borderWidth](https://developer.apple.com/documentation/quartzcore/calayer/borderwidth)
  and [NSColor separatorColor](https://developer.apple.com/documentation/appkit/nscolor/separatorcolor).
- [WebKit NavigatorUAData](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/page/NavigatorUAData.cpp)
  and [WebKit client-hints implementation discussion](https://bugs.webkit.org/show_bug.cgi?id=241749).
