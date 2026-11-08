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

Website `viewport-fit=cover` and CSS safe-area integration are not implemented.
The first validation target is ordinary-page rendering, fixed/sticky layout,
background color, and input alignment. Window-local geometry, nonstandard window
types, nested scrolling into the band, accessibility, pinch zoom, fullscreen
transitions, and arbitrary PDF/plugin content require further validation.

## Source provenance

Platform base: `f0e2df52` (shared native result rows), with the accepted header
scroll routing beneath it. The unrelated command-bar-glass-outset patch was
popped only in this isolated copy. The canonical prepared source is untouched.

This copy retains the existing prepared-tree history: content-shadow patches
have an older order, and frame-label/day-night patches are not recorded in its
quilt applied list. The exact baseline is recorded in the local
`.work/header-inset/source-baseline.json`. It is not a fresh release preparation.

Patch: `patches/helium/ui/obscured-header-prototype.patch`.
Test fixture: `prototype/header-inset/page.html`.

Build and runtime results will be recorded after validation.
