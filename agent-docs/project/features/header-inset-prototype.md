# Pinned header and page inset prototype

Issue #11, resumed November 8, 2026. This experiment uses current main tooling
at `26375df286265b337db81bafcce802c1043d33da` and the accepted, pushed platform
stack at `7b9dda9113b0e13a8317da9c5452cb5770824130`
(`topic/command-bar-corners-reviewed`). Main still pins an older browser input;
no development lock or published build is changed.

Current preview: **Lune Inset Test 4**, with the three-choice “Show top controls”
submenu. Hover is the fresh-profile default; normal Always show protects every
page with the 52 pt inset; experimental overlay retains viewport-fit/env support.
The signed local mode commit is `cdec625c16d7fb851ee5740dbfb9064434b88d63`, atop
the earlier prototype stack, imported on `prototype/pinned-header-inset-current`.
See the three-choice section below for current validation and acceptance limits.

## Initial implementation and earlier candidates

A launch-gated, browser-owned 52 pt inset keeps the renderer surface full height,
reduces and translates ordinary page layout, and extends root painting and
hit-test clips upward. The document starts below the permanently visible native
header, then scrolls behind it. The initial band uses root or propagated body
background color. Ordinary background images do not extend into the band.

Pages can opt in with `viewport-fit=cover`. They then use the full viewport and
can paint images or other content behind the header. `env(safe-area-inset-top)`
exposes the header inset, 52 CSS pixels at normal zoom. The prototype honors
this metadata on desktop without enabling mobile viewport width/zoom behavior.
Dynamic cover/contain changes update through the existing viewport path.

This reuses compositor scrolling, with no injected page script or per-scroll
layout callback. The native header's cursor polling stops when pinned unless an
unpinned sidebar still needs retention tracking. This is the low-overhead
approach under test; measured scroll layout counts are not battery measurements.

The owner accepted the rendered behavior on November 8, 2026. The next
candidate adds “Tabs on Right Side” and “Always show controls” directly to the
macOS window context menu, removing the Browser Layout submenu. The checkbox
reuses the saved top-chrome pin preference and sends a per-WebContents inset
through WebPreferences. Existing/background tabs update immediately; the owning
normal browser layout determines whether the inset applies. The experimental
launch flag and fixed 52 pt header height remain. Menu acceptance,
Intel, zoom, fullscreen transitions, split panes, accessibility, nonstandard
windows and PDF/plugin content remain outside the verified prototype scope.

The signed local platform commits are `31d0a4a988d5a45c389bc23c9dcb20878d889686` (ordinary-page inset)
`c707d7ffe105d35bca6311cdb7fc4b8d96a1acab` (cover/safe-area opt-in and fixtures),
and `942299eddae59bfa41702b8852549da3893ba3f2` (live window-menu preference and validation).
They are saved on `prototype/pinned-header-inset-current` in both the isolated
platform repository and the integration repository; they have not been pushed.

## Local workspace and rollback

The reversible work is separate from the owner's integration checkout:

- `.work/header-inset/orchestrator`: this main-based documentation/tooling
  worktree, branch `prototype/header-inset-integration`.
- `.work/header-inset/platform`: platform branch
  `prototype/pinned-header-inset-current`, with the quilt patches
  `obscured-header-prototype.patch`, `obscured-header-cover-prototype.patch`, and
  `obscured-header-menu-prototype.patch`.
- `.work/header-inset/platform/prototype/header-inset`: tracked fixtures,
  ChromeDriver checks, strict forward/reverse replay tool, implementation notes
  and `validation.json`.
- `.work/header-inset/resume-2026-11-08`: base provenance, old candidate evidence,
  current renderer reports and screenshots.
- `.work/header-inset/Lune Inset Test 3.app`: distinct disposable-profile preview
  with ordinary and opted-in page examples.

The original candidate remains at `e8b314ceb0129f67a65ec5cad88e6867d79af613` on
`prototype/pinned-header-inset`. The canonical prepared source is preserved.
Keep the workspace at its original path because quilt metadata and build caches
contain absolute paths.

Enable the experimental renderer path with `--lune-obscured-header-prototype`.
Unchecking “Always show controls” restores auto-hiding controls and removes the
inset immediately. The saved header pin preference is controlled by the new menu checkbox. The renderer
patch is experimental, is not a setting in the regular app, and is not a release
input. See the platform README and validation record for the exact checks.

## Initial renderer validation on November 8, 2026

The arm64 browser and ChromeDriver build passes. Headless device scale 1 and
headed Retina scale 2 checks both pass: a 900 pt surface retains its size while
ordinary layout becomes 848 pt; content scrolls into the upper band; root/body
color changes, fixed and band clicks, and page/nested wheel input work.
The measured ordinary-page wheel scroll has zero layout/style recalculations.

Opted-in pages retain the 900 pt viewport, expose a 52 CSS px safe-area value,
paint their gradient into the upper band, and accept correctly positioned
clicks. Live cover/contain toggles and navigation back to an ordinary page pass.
Saved pin preferences remain false in all four disposable test profiles.
Both quilt patches strictly apply and reverse with zero fuzz, reproducing all
13 changed source files. This is delta validation, not full distribution replay.
The owner subsequently accepted this rendering. Menu toggle validation is
recorded separately; Intel remains unverified.

## Cover compatibility finding

The owner reported Apple and Substack headers underneath the controls. Inspection
of both live pages in candidate `c707d7ff` confirmed `viewport-fit=cover`, a
computed `env(safe-area-inset-top)` of 52px, and no document fullscreen element.
Apple's 44px global navigation is fixed at top 0 without top padding; Substack's
64px top bar begins at y=0 with zero top padding. Their loaded styles use other
safe-area edges, but their desktop headers do not consume the top inset.

The environment value is delivered correctly. Treating `viewport-fit=cover`
alone as adequate opt-in to desktop browser controls overlaying content exposes
a compatibility gap. Recommend retaining the protective browser-owned offset
for existing sites and requiring a deliberate controls-overlay opt-in. No
compatibility policy change is included in the menu candidate. Evidence is
tracked in the platform's `prototype/header-inset/site-compatibility.json`.

WebKit documents that cover removes automatic insetting and authors must
separately apply safe-area padding: [Designing Websites for iPhone X](https://webkit.org/blog/7929/designing-websites-for-iphone-x/).

## Menu candidate validation on November 8, 2026

The final arm64 browser/ChromeDriver build passes. Headless scale 1 and headed
Retina scale 2 checks pass live preference toggles with both sidebar orientations,
ordinary-page scroll retention, cover-page visual anchoring, click alignment and
saved unchecked preference after relaunch. Three patches strictly apply/reverse
with zero fuzz and reproduce all 20 affected source files.

Native inspection of Lune Inset Test 3 confirms the requested menu order with
no Browser Layout submenu. Toggling over Wikipedia at the top removes/restores
the inset. At scrollY 900, on/off/on keeps scrollY exactly 900 while layout height
changes 848/900/848; the restored glass header overlays the scrolled content.
The preview is left with controls enabled. Automated click alignment is verified
on local fixtures; the native website test covers menu interaction and geometry.
Evidence is in `.work/header-inset/menu-validation/` and the tracked platform
validation record. Intel and owner acceptance of the menu candidate remain pending.

## Three-choice controls mode

The owner requested a “Show top controls” submenu after “Tabs on Right Side”,
with mutually exclusive “Show on hover”, “Always show”, and “Always show with
overlay (experimental)” options. A fresh profile defaults to hover. The middle
choice always uses the browser-owned 52 pt translation regardless of viewport-fit
and adds no header inset to CSS environment values. It retains scrolling behind
the header. The experimental choice preserves the preceding cover/env behavior.

The existing pin boolean remains the native chrome source of truth; an additional
saved overlay-policy boolean defaults false. The menu derives exactly one radio
selection from them. Each preference change propagates through WebPreferences,
including transitions between the two pinned modes. There are no site-specific
rules, injected styles, or new scroll callbacks. The fourth isolated quilt patch,
`obscured-header-modes-prototype.patch`, adds this policy and submenu. All four
patches strictly replay forward/reverse across 25 source files.

The distinct preview for this revision is `.work/header-inset/Lune Inset Test 4.app`.
The older previews remain available. Three-mode build/runtime results are recorded
in the platform validation record after testing; prior sections describe prior
candidates, not acceptance of this revision.


Three-mode validation passes on arm64: the 23m02s browser/ChromeDriver build,
headless scale 1 and headed Retina scale 2 pixel/input checks, live transitions
on both sidebar orientations, all three saved modes after relaunch, and a fresh
profile selecting hover. Protective cover pages paint the root background into
the empty band and scroll content beneath it, with zero measured layout/style
recalculations during the test wheel scroll. Dynamic cover/contain changes leave
the protective inset and zero header safe-area value unchanged.

Native inspection confirms the exact submenu labels and one checkmark per mode.
On the loaded cover fixture, always gives height 848 / safe area 0, experimental
gives 900 / 52, and hover gives 900 / 0. Apple and Substack both display their
headers below the native controls in normal Always show despite declaring cover;
both report height 848 and safe area 0. The preview remains on Substack in Always
show for owner review. Source replay covers 25 files across all four patches;
the preview framework hash matches the tested build. Evidence is in
`.work/header-inset/modes-validation/` and the tracked platform validation record.
No Intel build or owner acceptance of this revision is claimed.
