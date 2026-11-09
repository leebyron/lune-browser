# Obscured header experiment

Issue #11. This is a launch-gated renderer experiment, not a release input.
Use `--lune-obscured-header-prototype` with a disposable profile in Lune's
native vertical-tab layout. The macOS window context menu has “Tabs on Right
Side” followed by the “Show top controls” submenu, with one selected choice:

| Choice | Header | Page layout | Header safe-area value |
| --- | --- | --- | --- |
| Show on hover (default) | Existing hover behavior | Full height | None |
| Always show | Pinned | Always inset 52 pt, including viewport-fit=cover | None |
| Always show with overlay (experimental) | Pinned | Inset ordinary pages; full height for cover pages | 52px for cover pages at normal zoom |

The existing saved `helium.browser.zen_mode_top_chrome_pinned` preference remains
responsible for pinning. `helium.browser.top_controls_overlay` enables the
experimental policy and defaults false. The radio selection is derived from
these preferences: unpinned means hover; pinned selects either normal or overlay.
A fresh profile defaults to hover. Existing saved pin choices remain pinned and
use the protective mode unless overlay was explicitly enabled. Changes apply
live to the profile's tabs, including background tabs, and survive relaunch.

## Behavior and cost

Ordinary pages retain a full-height renderer surface, but their layout area is
52 AppKit points shorter and translated down by 52 points. Root painting and
hit-test clips extend upward so content scrolls into that band. Root and
propagated body background colors fill the initial empty band, including live
color changes. Background images on ordinary pages do not extend into it;
a transparent gradient-only background leaves that band white.

In experimental overlay mode, pages with
`<meta name="viewport" content="viewport-fit=cover">` use the full
surface without the translation. They can paint background images or other
content behind the header, and use `env(safe-area-inset-top)` to keep controls
and text clear. At normal page zoom the value is 52 CSS pixels, including on
Retina displays. Switching between cover and contain updates geometry and the
environment value without reloading. Desktop mobile-width/zoom interpretation
remains disabled; only viewport-fit parsing is enabled by the prototype flag.

Both always-show modes keep the native header open. Main-frame input coordinates account for
the ordinary-page translation. The floating header reserves no legacy Views
toolbar height. Cursor polling stops when the header is pinned and no unpinned
sidebar needs retention tracking. Existing compositor scrolling is retained;
there is no injected page script or per-scroll browser layout callback.
Viewport metadata and pin preference changes update layout and environment
values through the existing viewport path. The owning normal browser window
supplies the inset through WebPreferences; popup windows receive zero. This is a low-overhead design, not a battery benchmark.

## Source provenance

The platform base is the accepted, pushed UI stack at
`7b9dda9113b0e13a8317da9c5452cb5770824130`
(`topic/command-bar-corners-reviewed`). The integration tooling worktree starts
from current `origin/main`, `26375df286265b337db81bafcce802c1043d33da`.
Main still pins an older browser input, so this experiment explicitly uses
the accepted platform stack above without changing the development lock.

Platform branch: `prototype/pinned-header-inset-current`. The original parked
candidate remains at `e8b314ceb0129f67a65ec5cad88e6867d79af613` on
`prototype/pinned-header-inset`. This work rebases its renderer delta onto the
accepted UI stack and adds separate cover/safe-area, menu, and mode patches:

- `patches/helium/ui/obscured-header-prototype.patch`
- `patches/helium/ui/obscured-header-cover-prototype.patch`
- `patches/helium/ui/obscured-header-menu-prototype.patch`
- `patches/helium/ui/obscured-header-modes-prototype.patch`

The isolated prepared tree and outputs are in `.work/header-inset/platform`.
Its historical applied prefix is retained; this is not a fresh release source
preparation. Before adding the prototype, all 13 files affected by the 12 newly
accepted UI patches matched the canonical prepared tree byte for byte.
The canonical prepared source and original integration checkout are untouched.
Base and previous-prototype evidence is in
`.work/header-inset/resume-2026-11-08/`.

## Validation and limits

See `validation.json` for final build, renderer and strict replay evidence.
The runnable check requires Pillow and uses local fixtures and disposable
profiles. Use a fresh evidence directory for each run:

```sh
python3 prototype/header-inset/check.py build/src/out/Default /tmp/lune-inset-check
python3 prototype/header-inset/check.py build/src/out/Default /tmp/lune-inset-retina --headed --toggle
python3 prototype/header-inset/replay.py build/src /tmp/lune-inset-replay
```

The checks compare baseline/flagged geometry and screenshot pixels, fixed and
scrolled-band input, page/nested wheel routing, layout/style counts during a
scroll, cover-mode gradients and CSS insets, dynamic cover/contain changes,
and navigation back to an ordinary page. `--toggle` additionally exercises live
changes between all three modes with either sidebar orientation, retains page
state across the changes, verifies protective mode ignores dynamic viewport-fit
changes, tests each saved mode after relaunch, and checks fresh-profile defaults. `--observe` records
renderer probes without assertions.
The replay check applies and reverses all four patches with `gpatch --fuzz=0` and
compares every affected source file. It verifies this delta, not the full stack.

The experimental flag remains process-wide, but the inset is now supplied per
WebContents from its owning browser layout and saved preference. The header
height remains hard-coded at 52 pt.
Nonstandard window types, accessibility, pinch/page zoom, fullscreen transitions,
split panes, and PDF/plugin content require further validation. Intel is not
built or tested for this experiment. The owner accepted the preceding renderer
preview on November 8, 2026. The earlier binary's native inspection confirmed
on/off toggling over Wikipedia at the top and at scrollY 900. Validation of the
new three-choice candidate passes arm64 build, headless and Retina renderer
checks, fresh defaults, all-mode persistence, and native menu inspection. Apple
and Substack clear the pinned header in Always show. See `validation.json` for
exact evidence; owner acceptance of this revision remains pending.

The distinct preview is `.work/header-inset/Lune Inset Test 4.app`, with its own
profile. The older previews and original branch remain available for rollback.
No release input, published app or update feed is changed.

## Existing-site compatibility

Apple and Substack both declare `viewport-fit=cover` and correctly receive a
52px top safe-area value, but their desktop headers do not apply it. Cover alone
is therefore insufficient evidence that a page accommodates overlaid desktop
controls. See `site-compatibility.json`. The user selected a browser-level policy
choice: “Always show” now protects all pages, while the explicitly experimental
choice preserves the original cover behavior. No new website opt-in syntax or
site-specific heuristics are introduced.
