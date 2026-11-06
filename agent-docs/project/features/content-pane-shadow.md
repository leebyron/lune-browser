# Content pane shadow

Implements [issue #1](https://github.com/leebyron/lune-browser/issues/1): subtle
visual separation between rounded content panes and the surrounding browser chrome.

## Design

The shared `ContentsContainerView` owns a transparent, non-interactive anchor
behind its content surfaces. Chromium's `views::ViewDecoration` draws a 2-dp
Material Design shadow around that anchor using cached compositor decoration
layers. Each split pane gets its own shadow. The anchor encloses docked DevTools
and the new-tab footer, rather than shadowing those surfaces separately.

The shadow follows the existing content bounds and per-corner radii; it does not
change content insets, sidebar width, focus order, hit testing, or the active
split-pane outline. Its visibility follows `should_round_contents_`, including
the existing distinction between macOS browser fullscreen and content fullscreen.
An unrounded edge-to-edge content surface has no shadow. Existing frame and
highlight borders remain above it.

The feature contains no Lune branding, services, preferences, or platform-specific
code. It lives in the shared Helium core as
`patches/helium/ui/content-pane-shadow.patch`. It uses Chromium 158's
`ViewDecoration` API; an upstream submission against older Chromium would need
the equivalent shadow API adapter. No upstream submission is made automatically.

## Validation

Development work and evidence are under `.work/content-shadow/`. The two changed
Chromium files were reconstructed from their pre-patch backups and replayed with
all nine relevant patches using GNU patch with `--fuzz=0`. Inserting the new
patch at the end of the shared core, before platform patches, produces files
identical to the compiled prepared source. The merge/unmerge workflow places the
feature in the core repository and changes only its platform gitlink.

Verified on 2026-11-06:

- Incremental `chrome` and `chromedriver` builds pass for arm64 (5m36s) and
  x86_64 (4m58s).
- Existing page loading, JavaScript, profile persistence, UI/defaults, onboarding
  attribution, and settings smoke checks pass for native arm64 and Intel under
  Rosetta. This is not a native Intel hardware check.
- Native arm64 visual inspection passes in light and dark mode, left/right
  vertical sidebars, classic horizontal tabs, and split view. Each split pane
  retains its rounded corners and the active-pane outline. Closing a split
  restores the single-pane shadow; page controls remain clickable.
- Disabling the rounded frame removes the shadow; reenabling it restores it.
  Browser fullscreen preserves the upstream rounded-frame behavior. Content
  fullscreen is edge-to-edge without a shadow, and exiting restores the pane.
- Strict patch replay, Git object/lock validation, and all 37 repository tests
  pass. Split-divider dragging and native Intel visual inspection were not
  independently verified.

Local evidence: `build-{arm64,intel}.log`, `smoke-{arm64,intel}.json`,
`strict-replay.json`, and `shadow-*.png` in `.work/content-shadow/`.

## Pinned inputs

- Core commit: `e2a09ea1efab4c9459be14513c446cab2723175e`.
- Platform gitlink integration: `6ecd11db298eafc5276b58443532c9a81a950145`.
- Permanent tags: `inputs/content-shadow-1/{helium,macos}`.
- Patch SHA-256:
  `66d11bec2acb4e4acc765146de06fd469ba14badd59e5c9b94742425615a3810`.

The development lock pins the complete core tree (including this patch and its
series position) and the platform gitlink. Existing platform PR selections are
unchanged. The feature is authored as a separate core commit so it can be
reviewed or ported to Helium independently.

## Release boundary

This is a development input change. Published builds 1 and 2, their source kit,
and their staging feeds remain immutable and do not contain this feature. A
future signed release must use a new build number and repeat release gates.
