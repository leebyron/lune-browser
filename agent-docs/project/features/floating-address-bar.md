# Floating native address capsule

Prototype requested on 2026-11-06: reveal a floating glass address bar when the
pointer enters the top rail; hide it after 700 ms continuously away. Use Apple's
public UI SDK and the latest mockups from the “Lune: Figma design” chat.

## Reference and scope

[Figma file](https://www.figma.com/design/I39uQunZpu6LsS7mDjcGSh/Untitled).
The latest mounted/floating left/right mockups in that chat show a centered
address capsule, separate navigation and extension capsules, and content behind
the controls. Figma's connector hit its Starter-plan limit. The owner explicitly
authorized using the desktop mockups and screenshots instead of connector output.
The reference inspected was `02-mounted-right-design.png` from that chat's
`sidebar-screenshots` directory.

This increment implements the address capsule and its reveal behavior. It does
not implement all of [issue #3](https://github.com/leebyron/lune-browser/issues/3):
sidebar redesign, window-control relocation, and separate navigation/extension
glass groups remain separate work. Preserve existing working browser controls.

## Implementation

The native macOS view uses public AppKit `NSGlassEffectView` (macOS 26+) with
buttons inside its `contentView`, system font, and SF Symbols. macOS 27 adds
`effectIsInteractive`; earlier supported macOS versions use AppKit's
`NSVisualEffectView`. AppKit owns the material rendering and accessibility
transparency adaptation. No CSS glass imitation or private glass API is used.

The 480 × 36 pt capsule is centered over the content region, 4 pt from the top,
and narrows with the window. Either mounted sidebar changes its available space.
The native host overlays the content without participating in page layout.
The middle rail does not reveal the old layout-based toolbar. The outer edges
retain its window/extension/app controls, including their existing reveal layout;
keyboard focus and open menus also preserve that toolbar.
The prototype applies to the existing vertical, frameless, address-in-sidebar
layout with the top bar unpinned; other layouts keep their existing toolbar.

The title comes from Chromium's address formatter and security display text.
The leading button opens the existing page-information bubble; the trailing
button reloads or stops the page. Clicking the address opens the existing URL/
command palette with the complete navigation URL, including its scheme. When that
palette is disabled, focus goes to the existing omnibox. This retains existing suggestions and
navigation handling rather than introducing a second search implementation.

An 8 pt top rail reveals the capsule. The capsule and the gap between it and the
rail keep it visible. A separate one-shot 700 ms timer begins on departure and is
cancelled on reentry. Keyboard address editing also reveals the capsule. Active
editing or browser bubbles hold it open. Content fullscreen and inactive windows hide it. A visible-only cursor refresh
handles native interaction transitions without a new mouse movement.

## Validation

Local work and evidence are under `.work/floating-address/`.

Final input checks on 2026-11-06:

- Incremental `chrome` and `chromedriver` builds pass for arm64 (2m23s) and
  x86_64 (2m22s).
- Page loading, JavaScript, profile persistence, fresh-profile defaults,
  onboarding attribution, and settings smoke checks pass on arm64 and Intel
  under Rosetta. These are headless checks, not native Intel acceptance.
- All 37 repository tests, Git ancestry/tag/tree/gitlink validation, documentation
  links, and whitespace checks pass.

Patch and native UI checks:

- Strict replay applies all 33 patches affecting the five edited files with
  `--fuzz=0`, producing byte-identical prepared sources. Unmerge changes only
  the macOS patch and its series entry; the shared core remains unchanged.
- Native arm64 inspection during implementation verifies that AppKit renders
  the capsule above page content, exposes its three localized buttons to accessibility, opens the
  existing address palette and site-information bubble, and reloads the page.
  Page clicks continue working. Leaving address editing dismisses the capsule
  after a delay; content fullscreen hides it and exiting restores normal UI.
- A pointer-specific hover/reentry timing pass is still pending. The automation
  injects clicks without moving the macOS pointer used by the hover monitor.
  A manual pointer check was requested; do not report that check as passed from
  the keyboard-driven inspection alone.
- The final native rerun for the URL-scheme and profile-theme corrections is
  pending because macOS locked during testing. Native Intel UI,
  pre-macOS-26 fallback appearance, and Reduce Transparency are not independently
  verified by this development check.

Evidence files: `build-{arm64,intel}.log`, `smoke-{arm64,intel}.json`,
`strict-replay.json`, `repository-tests.log`, and `doc-links.json`.

## Pinned inputs

- Platform commit: `b3a4ba00f2e7de5427fa0e2034890de2edc526ec`.
- Platform tag: `inputs/floating-address-1/macos`.
- Core remains `e2a09ea1efab4c9459be14513c446cab2723175e`
  (`inputs/content-shadow-1/helium`).
- Patch and ordered selection hashes are pinned in `manifests/patches.json` and
  `manifests/browser.lock.json`.

This is a development feature. Published builds 1 and 2 and their feeds remain
immutable and do not contain it. A new signed release must use a new build number
and repeat release gates, including native pointer interaction acceptance.

## API evidence

- [Apple NSGlassEffectView](https://developer.apple.com/documentation/appkit/nsglasseffectview)
- [Apple contentView contract](https://developer.apple.com/documentation/appkit/nsglasseffectview/contentview)
- Installed Xcode 27.2 SDK: `AppKit.framework/Headers/NSGlassEffectView.h`.
