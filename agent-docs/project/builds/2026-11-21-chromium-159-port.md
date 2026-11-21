# Chromium 159 adoption

The port starts from Lune main `118238fe9c431e59b250d5b6467a3b36507e3e51`, which integrates Helium 0.22.2 and includes the picture-in-picture permissions and native tab status changes. The target is macOS Chromium Early Stable `159.0.8154.13` at `4d790f9eb4c8abe65b8aaa3feba664e7c734ba56`. Recheck the macOS Stable selection before adopting the inputs. [Chromium Dash](https://chromiumdash.appspot.com/releases?platform=Mac) · [Source archives](https://github.com/imputnet/chromium-tarballs/releases/tag/chromium-159.0.8154.13)

The Lune branch is `port-chromium-159`. The baseline review records the Chromium 159 input before the separately reviewed Settings layout change.

## Source checks

The first 100 retained core patches replayed from the checksum-verified arm64 source with zero fuzz and 90 hunk offsets. All 784 affected files matched the quilt staging tree byte for byte in an independent replay. The prefix ends at `helium/core/search/fix-search-engine-icons.patch`. Core and macOS patch lint and translation lint passed. The exact patch hashes are in `.work/audit/strict-prefix-100.json` in the port worktree.

Chromium 159 already contains the two WebAssembly fixes, confirmed by reverse dry-runs. Its Windows packaging no longer includes the Privacy Sandbox attestations preload target removed by `disable-privacy-sandbox.patch`. The port retires those three entries and preserves the order of the retained patches.

Current source resolutions preserve the Safe Browsing build configuration, the disabled browser sign-in and AI surfaces, the JavaScript optimizer settings, and Manifest V2 support. Reader Mode uses local fonts. The Canvas `measureText()` noise flag still applies to main-thread browser canvases using the Chromium 159 measurement flow. The experimental `shapeText()` API merits its own check. The new-tab clipboard action uses the macOS copy/paste buffer and keeps Chromium's HTTP and HTTPS validation.

## Complete core replay

The signed local core tip is `8344b79943600bd43f643c8ce0cb92925559e84e`. All 372 retained core patches replayed with zero fuzz and 528 hunk offsets from each of the checksum-verified macOS host archives. All 1,756 affected files matched byte for byte across both replays and the quilt staging tree. The audit files are `.work/audit/strict-prefix-372.json` and `.work/audit/strict-prefix-372-x64.json`. The final core patch disables persistent pins at compile time. Standard pins use Chromium's `PinnedTabService`.

Chromium 159 also removes the Interest Group runtime declaration and disables Browsing Topics by default, so the separate Helium patch for those two defaults was retired. The regenerated pruning list accounts for 294 additions and 91 removals. The domain-substitution list has 421 additions and 349 removals. The inventory preserves the relocated Reader Mode models and the archive-provided macOS build dependencies.

## Complete macOS replay

Both independent archive replays match the ordered quilt result across 2,094 paths, including two absences. Each applied all 663 retained patches, 372 core and 291 macOS, with zero fuzz and 1,189 exact-context hunk offsets. The audit files are `.work/audit/strict-prefix-663.json` and `.work/audit/strict-prefix-663-x64.json`. Core and macOS patch and translation lint passed. The orchestrator ran 108 tests with one skip.

The sidebar port preserves the neutral group headers and disclosure, native tab-group menu, Older Tabs grouping, pin drop targets and hidden-sidebar popover. It adapts these features to Chromium's focus-animation and layout snapshot APIs. The privacy settings port moves the tracking protection row to the new Lit template and restores focus when leaving the subpage. The download delegate still strips matching campaign and tracking parameters before a renderer or Save Link As download starts. The native PiP permission offer and tab status symbols are included in the replay.

Full source preparation exposed a host-specific Open Screen formatter in the common pruning list. The core now prunes either formatter directory when present. The macOS GN graph also required the new download file-type proto label. Review builds use the pinned Xcode 27.2 and the macOS 13 minimum from the Chromium configuration. GN generation passed for both targets after the label update. The signed local checkpoints are core `53a5ae099eae7e76f5d9cd0a717c79d204f57c19` and macOS `fbc7c9fc02b904bafa8e587ce36020aa88568726`. The arm64 review build began with the three source adjustments that were then refreshed into those checkpoints.

The two prepared review trees matched across 572,663 shared source files and 130 symlinks. Starting compilation created three depot_tools cache files and generated the onboarding strings in the arm64 tree. Generating the strings in the Intel-target tree produced the same SHA-256, `daf3eab82c04bbe51e85621f9f6bf5d449f53b9ca62afffc55c3fb6033f2976a`. An additional syntax pass parsed 66 patched Settings TypeScript files using the archive's compiler. The syntax pass does not replace the WebUI build and runtime checks.

A fresh arm64 preparation from the signed checkpoints matched all 572,664 source files and 130 symlinks in the compiling review tree, including the generated onboarding strings. The three depot_tools cache files were the only extras in the build tree. The source inventory SHA-256 is `c81852608760c96a0c6af1c21273d2b21af2e3c65c7d0770a6ce954d9b182a20`.

Chromium 159 changes Clang, GN, Siso and both PGO profiles relative to the validated Chromium 158 output donor. The new build uses a fresh output directory. The shared `sccache` was retained. Its initial statistics showed zero hits and 8,417 calls bypassed because its parser could not handle a Clang argument.

## Compile repairs

Native compilation found four API or dependency changes after GN generation. The flags UI now uses `base::Feature::GetDefaultState()`. The existing Safe Browsing preference patch removes the remaining hash real-time preference callers. The New Tab Page drops an unused undo callback. Helium Services drops the obsolete Polymer help-bubble mixin and retains its preference and crash-reporting bindings. The individual C++ objects and the New Tab and Settings TypeScript targets passed on arm64 after resuming with the repaired input.

The signed components for this checkpoint are core `e026fa6e2734e43ec5ed78efe7be50f6b3fd3548` and macOS `ffb0b4bc81269ab43c1b3182ee1ca56a60b5fc77`. Both source archive replays match all 2,094 touched paths with zero fuzz and 1,186 exact-context hunk offsets.

Subsequent fixes adapt the shortcut label, palette header, Web Push overrides, side-panel sizing, optional sign-in artwork, group disclosure colors, and toolbar overflow and mute commands. The vertical sidebar call sites and their test fixtures use the same width accessor. The framework link fix gates the new enterprise attribution hook on the reporting backend that implements it.

The current signed core is `0a6fb01cf62cf69f8e6ed1044b167f5516bfda74`. The corresponding macOS component is `0fbdf54598f378b53bb37dd37d9caa2229004f04`. All 663 patches replayed from each archive with zero fuzz and 1,159 exact-context hunk offsets. The independent replays match the quilt result across 2,098 paths.

## Apple silicon build

The packaged browser and ChromeDriver report Chromium `159.0.8154.13`. The arm64 framework SHA-256 is `9f0b3bd74a5dcde443139afb209ad86fede6a2236699a6f843f4341debf49ed2`. Packaged smoke passed with Settings and artwork checks. Setup defaults, the 216px sidebar reservation, native sidebar activation, pinned-tab drag, the DevTools header, and the command palette fixtures passed.

The seven headed PiP permission cases passed. With extensions disabled, attachment navigation and HTML downloads removed tracking and campaign tags from the first request. Signed URLs, excluded domains, and the disabled cleanup setting retained the fixture query. The automation-only download override replaces the standard browser delegate, so the first-request validation uses the browser's ordinary download handling.

Both Media Session setters returned resolving promises, and CSS `AccentColor` inherited the page's selected accent in the default configuration. Lune's default profile omitted speculative preloading. An otherwise identical profile with preloading enabled prerendered an opted-in cross-origin frame before activation. The control withheld the cross-origin frame until activation. The reports are in `.work/audit/`.

The tracking privacy controls and the extension-free navigation request fixture also passed. The sidebar, pin drag, DevTools header and command palette source fixtures passed for the Intel target under Rosetta. The command palette fixture supports both the earlier index-based mute API and Chromium 159's tab handles.

The packaged arm64 preparation matched the fresh signed Intel preparation across 572,664 source files and 130 symlinks. The identical source inventory SHA-256 is `c85c49423cb8f893ae3ef34c29019ecc2a22b4996071f2dd2316fa9622ab3115`. The comparison excluded generated depot_tools bookkeeping and the Intel workspace's temporary CIPD executable, whose bytes matched the archive-pinned host tool.

A loopback canvas probe confirmed that partial readbacks match the corresponding pixels in a full readback, including repeated reads. With fingerprint protection enabled, both the document canvas and worker canvas changed the fixture pixels. With protection disabled, both returned the original bytes. The report is `.work/audit/arm64-canvas-readback.json`.

## Settings experiment

A separate arm64 run verified the standard Settings layout and search. It found six matches for “downloads” and seven for “tracking.” With the 2026 refresh and search explicitly enabled, General showed the Downloads and startup sections. The tracking toggle persisted in both layouts. In the redesign, browser Back returned focus to the tracking row. The new dropdown returned no results for “password,” “tracking,” or “helium.” Chromium's section factory returns an empty registry of sections in both verified source archives. Both features remain disabled by default. See `.work/audit/settings-2026-runtime.json` and `.work/audit/settings-2026-interaction.json`.

The extracted production services fixture passed the full update and consent matrix, dismissal, and one-time preference migration on arm64. French and German setup both displayed the expected Helium partner credit. The locale reports are `.work/audit/arm64-credits-fr.json` and `.work/audit/arm64-credits-de.json`.

## Adoption checks

The packaged x86_64 browser passed ChromeDriver, Settings, artwork
and profile readback smoke under Rosetta on Apple silicon. French and German
setup credits and the production services consent matrix passed. The Intel
framework SHA-256 is `5458fba5d1c6c68c79ab35b41807f6be42f787ab20d8e4a467ea67ca7dad6792`.
The reports are in `.work/audit/`. Both architecture builds use the
same verified source inventory. The Arm preview and the exact Intel target
represent the component commits in the development lock.

In a headed browser, reveal and dismiss the hidden-sidebar popover and verify that content keeps its width. Focus one group and then another, exit focus, drag across the pinned-group divider and check the pinned-tab appearance. With media playing, check the native badges and hover card, and exercise the PiP Allow and Not Now paths. Repeat attachment navigation, HTML download, and Save Link As with extensions disabled. Verify that the first request retains `keep=1` and drops `fbclid` and `utm_source`. Check Copy Download Link from the completed item.

The [earlier investigation](2026-11-20-helium-chromium-159-investigation.md#chromium-159-regression-targets) records web platform probes to repeat on the Lune build, including CSS accent colors, the Media Session camera and mic promises, and opted-in cross-origin prerendering.
