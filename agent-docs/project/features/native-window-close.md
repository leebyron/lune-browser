# Native window close controls

Status (2026-11-09): owner accepted **Lune Close Test 2** and requested a commit
and adoption for future builds. The development lock now pins
`inputs/native-window-close-1/macos`, signed platform commit
`72cd119be74fd692ccea125c7e436f8fca608fdf`. Existing frozen release records and the
installed production browser retain their original inputs.

## Failure and cause

The owner reported that the red macOS window button does nothing in production
and previews, while Command-W works. An isolated production-derived preview
reproduces the failed action. Runtime instrumentation confirms that the visible
replacement button is enabled and targets `BrowserNativeWidgetWindow` with
`performClose:`, but AppKit never calls `windowShouldClose:`. The original hidden
titlebar button is disabled.

An isolated AppKit probe distinguishes visibility from availability: hiding the
original button still permits `performClose:`, while disabling it prevents the
delegate request. AppKit checks the original button even when the action comes
from the enabled replacement. This explains why the earlier visibility-only
probe did not reproduce the defect.

## Implementation

The replacement button targets its native controls object, which invokes a
copied close callback. Both the floating and classic-fullscreen hosts configure
that callback with a weak reference to their owning browser widget and call
`CloseWithReason(kCloseButtonClicked)`. The browser's normal tab-drag, unload,
close-blocking, and asynchronous tab/window teardown logic remains authoritative.
There is no unconditional native-window close and no mutation of the original
button's disabled state. The other traffic-light targets/actions are unchanged.

The callback is copied before invocation so synchronous destruction of the
controls cannot invalidate the executing block. A dead widget makes it a no-op.

Classic fullscreen validation exposed an existing teardown fault, newly reachable
through the repaired close button: `BrowserFrameViewMac` restored the original
fullscreen titlebar buttons during destruction. AppKit synchronously queried
`NativeWidgetMacNSWindow::_isTitleHidden`, reaching
`NativeWidgetMacNSWindowHost::GetShouldShowWindowTitle` after the widget delegate
was destroyed. The destructor now detaches the fullscreen controls without
restoring a titlebar in a closing window, matching its existing floating-controls
teardown. Normal fullscreen-exit restoration remains in its live transition path.

## Inputs and patch workflow

The accepted candidate was developed under `.work/close-button/`:

- Platform clone/branch: `platform`, `topic/native-window-close`, based on
  `1cabd52145c9dc2ef1b3459c71b0133a81b6c4b4` (`inputs/release-delivery-1/macos`).
- Patch: `patches/helium/ui/native-window-close.patch`, appended to the platform
  series. It changes the native-controls header/implementation and macOS frame.
- Prepared sources and output caches were cloned from the existing development
  workspace into `build-src`; the original workspace was not edited.
- Quilt captured/refreshed the source edits. A second quilt refresh rebased only
  hunk positions onto the immutable release source; Helium's platform-patch
  merge/unmerge returned the final patch and series to the isolated platform clone.
- Release-source replay requires zero fuzz and zero offsets. Development-source
  replay requires zero fuzz and byte parity with all three built files. Existing
  compatibility/menu changes outside the patch explain development line offsets.

The development preview includes those existing compatibility/menu changes. It
is a test build, not a newly frozen or signed/notarized release candidate.

## Adoption into current main

The original signed fix is `ea781dea`. It is retained locally on
`topic/native-window-close`. The integrated commit
`72cd119be74fd692ccea125c7e436f8fca608fdf` applies that accepted change on top of
the current themed-sidebar input, `d503fa7151b4c8fbead63f0c252677de524be96b`.
The cherry-pick's append-only series conflict was reviewed by retaining all
existing entries and appending the close patch. Only patch hunk line positions
were refreshed; accepted code and context bytes are identical.

The existing older-macOS, Dock-prompt removal, downloads, footer prompts, startup
default, sidebar theme/width, and selection-contrast patches are preserved byte
for byte. Core, Chromium, ungoogled, and services inputs are unchanged. The new
macOS input is retained by an immutable signed tag, and its commit, tree, patch
hash, series position, and selection provenance are recorded in the development
lock. Both architectures and future release preparation consume that lock.

For this current-main composition, exact replay has zero fuzz and zero offsets;
the two changed implementation units compile on arm64 and x86_64, and native
close regressions pass on both architectures (x86_64 under Rosetta). No full
browser rebuild or runtime acceptance of the newly combined main stack was run;
the accepted candidate's full build/runtime evidence remains distinguished below.
All 65 repository tests and locked-input validation pass. Platform commit and
input-tag signatures are verified. See
[adoption evidence](native-window-close-evidence/adoption.json).

## Validation

Final build and browser-interaction results are recorded in
[the validation report](native-window-close-evidence/validation.json).
The portable native fixture compiles production native-controls code and the
actual shared widget callback, exercising the disabled-original reproduction,
owner isolation, close reason, expired-widget behavior, teardown during callback,
nonclosable windows, and unchanged minimize/zoom targets.

```sh
python3 scripts/check-native-window-close.py PREPARED_SOURCE --arch arm64
python3 scripts/check-native-window-close.py PREPARED_SOURCE --arch x86_64
```

Both full browser targets build. The native close and window-menu fixtures pass
on arm64 and x86_64 (the latter runs under Rosetta). Release replay passes without
fuzz or offsets; development replay matches the three built files byte for byte.

Live arm64 checks in **Lune Close Test 2** verify physical red-button activation,
whole-window closing with two tabs, a background tab's unload confirmation,
cancellation, confirmed closing, survival of an independent window, ordinary
Command-W tab closing, and classic-fullscreen closure without a process crash.
The earlier candidate also passed right-side unpinned header reveal/closing;
the final destructor-only refinement does not change that callback wiring.

The first classic-fullscreen close crashed, as described above. The corrected
preview passes the same scenario with another browser window still usable.

The stock smoke harness initially allowed Sparkle to replace the disposable
Intel app with the existing production release. That run is not final validation.
The evidence branch adds an empty loopback appcast and passes its URL through
`--custom-update-server-url` for every smoke session. Chromium's resolver rules
do not isolate Sparkle's native networking. The final smoke reports require
unchanged app-framework hashes throughout testing and after each complete run.

The final smoke runs cover packaged UI, defaults, settings bindings, JavaScript,
and profile persistence. They remain development checks, without release signing,
notarization, installed-update, or production-promotion acceptance.

Native Intel hardware remains unverified; x86_64 runtime coverage on this host
uses Rosetta. macOS before 26 remains unverified. Development adoption does not
change frozen release inputs or deploy a new browser release.
