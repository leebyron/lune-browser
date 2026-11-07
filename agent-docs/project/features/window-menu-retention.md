# Native window-menu retention

Requested November 7, 2026; tracked in [issue #6](https://github.com/leebyron/lune-browser/issues/6).

## Behavior

The native green/fullscreen traffic-light popover retains any already revealed
header and sidebar until it closes. Hidden surfaces are not forced open and
pinning preferences do not change. Layout continues to update. Normal pointer
retention resumes after dismissal, including when a collapse timer had already
been queued before the menu opened.

The implementation covers both `BrowserFrameViewMac::UpdateFloatingAddressBar`
and `BrowserView`'s cursor-driven and direct/timer-driven reveal paths. This is
separate from the unresolved resize cursor issue #5.

## Native lifecycle investigation

An isolated AppKit probe with a standard green button placed inside the content
area allowed the owner to exercise the menu without the computer-control overlay
covering the titlebar. On this Mac, the real popover emitted neither
`NSMenuDidBeginTrackingNotification` nor `NSMenuDidEndTrackingNotification` and
created no popup window in `NSApp.windows`.

AppKit uses an out-of-process menu. Read-only runtime inspection showed that its
show path attaches an `NSThemeWidgetZoomMenuRemoteView` to the originating zoom
button, calls the remote menu synchronously, and removes that child on return.
The owner's open/dismiss cycle confirmed that exact attachment at 23:03:54 UTC
and removal at 23:03:57 UTC on November 7. The host window stayed visible and had
no child windows throughout.

`HeliumFullscreenWindowControls::windowManagementMenuOpen` checks the existing
zoom-button children for that runtime class. It does not invoke the private
placeholder getter (which creates the child), modify AppKit's menu, swizzle
classes, install event taps, or change the menu-hosting preference. The class
name is an AppKit implementation detail: lookup is guarded, and future macOS
changes require revalidation. There is no new polling timer; the existing reveal
refresh queries the property.

For AppKit's in-process menu path, the controls also observe native menu tracking
notifications and match the menu delegate to their own zoom-button cell. The
menu reference is weak; only the matching end notification clears it, and
detaching the controls resets it. This fallback is covered by native tests, but
was not the path exercised by the host's real popover.

## Inputs and verification

- Base: `inputs/sidebar-footer-5/macos`, preserving the accepted sidebar/footer.
- Input: `inputs/window-menu-2/macos`, commit
  `2e7f31800164e6b0913c91ba91b7d351e87e1934`.
- Patch: `patches/helium/ui/window-menu-chrome-retention.patch`.
- Development only; not in published builds 1 or 2 and not release-accepted.
- The unpublished local input-1 checkpoint omitted the canonical series during
  refresh. Input 2 restores it; input 1 is not a usable build pin.

Strict no-fuzz replay passes across 55 relevant patches and all six affected
source files. A native test compiled from the production controls implementation
passes owning-control identity, independent menus, unrelated end notifications,
unrelated child views, real remote-view attachment/removal, control detachment,
and observer teardown. All 44 repository tests pass.

Arm64 and Intel compilation and headless smoke/default/settings/artwork checks
pass; Intel ran under Rosetta. Owner browser interaction acceptance is pending. Native Intel hardware acceptance remains separate from
Intel-under-Rosetta checks.

Local evidence: `.work/window-menu/` contains replay, native tests, component
checks, and build logs. `native-popover-lifecycle.log` records the real AppKit lifecycle and
`native-popover-inspection.log` contains the read-only show/close inspection.
These explain why ordinary menu notifications were insufficient. No debugger remains
attached to the probe.
