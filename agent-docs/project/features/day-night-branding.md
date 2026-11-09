# Wider Lune artwork and day/night appearance

The owner approved the paired-lune preview on 2026-11-06 and requested rollout
across the website, app icon and browser resources. The light palette is
Chlorophyll Daylight; dark retains the Color Atlas's Pelagic Signal.
The canonical geometry and palettes are in
[`branding/palettes.json`](../../../branding/palettes.json).

## Implementation

- The center thickness of each lune increases from 28 to 36.4 source units,
  exactly 30%. Outside radius 111, center offsets 14, and tips at
  `y = 150 ± sqrt(111² - 14²)` remain fixed. The inner circular arc radius is
  approximately 112.725508. Vector and raster generators use the same geometry.
- Website marks, app tiles and SVG favicon follow system appearance. CSS covers
  the desktop, browser illustration, story, glass controls and focus states.
  PNG/ICO/Apple touch fallbacks retain the dark tile; Apple touch is opaque.
- Both `.icns` variants ship in the macOS bundle. An AppKit appearance observer
  updates the running Dock icon on launch and macOS appearance changes. Finder
  and helper fallback icons use the dark tile. No upstream asset catalog is bundled.
- All existing browser-logo resource destinations use the thicker artwork.
  Onboarding SVG and CSS follow appearance; light/dark wordmarks and monochrome
  WebUI/vector icons retain their existing selection paths.
- Default browser colors follow the existing System/Light/Dark preference.
  Explicit accents, custom themes, app windows and high contrast keep precedence.
  The palette is applied before dependent color recipes and retained after the
  macOS Graphite postprocessing pass; native controls keep their native behavior.
- `components/helium_onboarding/BUILD.gn` now tracks `src/app.css` as an action
  input so palette edits invalidate the packaged onboarding output.

The change is a distribution-only macOS patch, `lune/day-night-branding.patch`.
The exact input is `20231c574761dd463b4567fb10a4beda68a92dd9`, retained under
`inputs/day-night-2/macos`. It does not change the shared Helium core input. This also rebuilds the previously
pending frame-thickness label input. Reusable floating-address and content-shadow
work remains separate, with its existing acceptance limits.

## Validation

The patch was authored with quilt in a prepared source subset and unmerged into
the platform repository. Strict forward replay applies 54 relevant patches over
all eight affected/predecessor files with zero fuzz. The seven branding files
match the compiled source after the known domain substitutions. Resource coverage
also verifies the two inline WebUI marks and all mapped logo destinations.

Local evidence lives under `.work/branding/`: `strict-replay.log`,
`resource-verification.json`, architecture build logs and smoke reports.
`scripts/smoke-browser.py --ui --internal-icons --appearance` checks packaged
icons, loaded WebUI artwork, default preferences, page execution, profile
persistence and both actual browser appearance settings and onboarding palettes.

Both architecture builds pass. Arm64 headless/headed and Intel-under-Rosetta
automated checks confirm the
exact ground/text colors in Settings and onboarding for both modes, as well as
page execution, profile persistence and bundled artwork. All 44 repository tests,
component patch/i18n lint, Git-object ancestry/tag/tree checks, generated-vector
checks and website deployment dry run
pass. Website desktop and browser-story layouts were visually inspected in both
palettes using local previews. The website uses the existing main-branch
self-hosted deployment workflow; no browser binaries or update feeds are published
by this change.

The Mac was locked during the native visual check. Dock switching and final
native window appearance still need an unlocked-screen inspection. Automated
headed execution is not a substitute for that visual acceptance.
These are development builds, not signed release candidates. Published builds 1
and 2 and their feeds remain unchanged; native Intel release acceptance remains
outstanding.

## Local monochrome symbol sizing refinement

The shared monochrome Chromium vector now fits the dual-lune mark to the full
width of its square canvas, preserving its aspect ratio and vertical centering.
A 16px icon slot paints a 16 by 14.09px mark, instead of 13.33 by 11.75px.
All ten mapped consumers, including the default-browser sidebar action, receive
the same resource. Colored app tiles and layout spacing are unchanged. Generator
consistency, exact geometry bounds, and all ten source/resource copies pass;
the arm64 browser build passes. The owner accepted the updated mark in
Lune Icon Test on November 9, 2026.
