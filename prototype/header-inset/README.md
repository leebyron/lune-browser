# Obscured header experiment

Issue #11. This is a launch-gated renderer experiment, not a release input.

Run this candidate with `--lune-obscured-header-prototype` in a disposable
profile using Lune's native vertical-tab layout. Omit the flag and relaunch to
restore ordinary behavior. The experiment does not change saved pin preferences.

The prototype keeps the renderer surface full height, reduces the layout area
by 52 AppKit points, translates that layout down, and extends the root painting
clip and canvas background upward. Existing compositor scrolling is retained;
there is no page script injection or per-scroll browser layout callback.
The native header is held open, and main-frame input coordinates account for
the translation. The renderer flag is process-wide for this first experiment.
The floating header reserves no legacy Views toolbar height. Cursor polling
stops when the header is pinned and no unpinned sidebar needs retention tracking.

Website `viewport-fit=cover` and CSS safe-area integration are not implemented.
Root background images do not yet extend into the initial band: a transparent
gradient-only background leaves the band white. Root and propagated body colors
work, including live color changes. This intentionally tests the minimum color
fallback before adding website opt-in behavior.

Window-local geometry, nonstandard window types, accessibility, pinch/page zoom,
fullscreen transitions, split panes, and arbitrary PDF/plugin content require
further validation. This is not a production-ready browser mode.

## Source provenance

Platform base: `f0e2df52` (shared native result rows), with the accepted header
scroll routing beneath it. The local command-bar-glass-outset patch is retained,
as requested, with its original patch bytes. The canonical prepared source is
untouched. Branch: `prototype/pinned-header-inset`.

This copy retains the existing prepared-tree history: content-shadow patches
have an older order, and frame-label/day-night patches are not recorded in its
quilt applied list. The exact baseline is recorded in the local
`.work/header-inset/source-baseline.json`. It is not a fresh release preparation.

Patch: `patches/helium/ui/obscured-header-prototype.patch`.
Test fixture: `prototype/header-inset/page.html`.

## Validation on November 8, 2026

The arm64 browser and ChromeDriver build passes. Automated checks pass in
headless mode at device scale 1 and the native macOS renderer at Retina scale 2:

- The rendering surface remains 900 points tall; the layout viewport changes
  from 900 to 848. The document edge starts at 52 points and scrolls into the band.
- Root/background color changes and propagated body background colors match
  screenshot pixels. The separate background-image capability probe fails as
  documented above; it is not included in the supported color-only behavior.
- Fixed controls remain below the header and receive clicks at their painted
  position. Direct input in the scrolled band hits the correct document element.
- Wheel events scroll the page and a nested scroller positioned inside the band.
- The measured 80-point wheel scroll produces zero layout or style
  recalculations in either mode. This is not a battery benchmark.
- Removing the flag restores baseline geometry. The saved header pin preference
  remains false after both test sessions.
- The prototype patch strictly applies and reverses with `gpatch --fuzz=0`;
  all ten changed source files match their recorded baseline/final bytes.
  This verifies the delta, not a fresh replay of the entire distribution.

Native header visual inspection was not performed: the Mac was locked and the
owner requested continuing without it. Intel has not been built/tested for this
experiment. The existing development lock and published builds are unchanged.

The first run exposed a no-active-tab Forward-button lookup; the native refresh
now guards it. Later checks found and corrected the old 34-point toolbar
reservation and the root hit-test clip, which initially excluded the band.

`validation.json` records the final results and source hashes. The runnable check
requires Pillow and uses only a local fixture and disposable profiles:

```sh
python3 prototype/header-inset/check.py build/src/out/Default /tmp/lune-inset-check
python3 prototype/header-inset/check.py build/src/out/Default /tmp/lune-inset-retina --headed
```

Use a fresh evidence directory for each run. `--classic` isolates the renderer
from the native floating header; `--observe` records probes without assertions.
The Lune integration checkout retains the full logs and screenshots under
`.work/header-inset/`, and the isolated preview is `Lune Inset Test.app` there.
