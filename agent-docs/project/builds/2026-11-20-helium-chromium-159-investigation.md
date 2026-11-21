# Helium and Chromium 159 upgrade investigation

The November 20, 2026 investigation starts from Lune main
`1b3c21722f107008cf9635d623dc9c88d1ee4a85` on
`investigate-helium-chromium-159`. The findings support a staged port.
Helium's new persistent pins require a product decision, and its current patch
series already needs changes to prepare on 159. The checkout still uses the
[development lock](../../../manifests/browser.lock.json).

## Inputs

| Input | Revision at inspection |
| --- | --- |
| Current Lune | Chromium `158.0.8127.37`, core `96ee1fb8d4d27f60891b747b8efc89f3fe68f2f8`, macOS `b5abc65dd1cd214b9b41fc83724d69013785ac9f` |
| Helium core | [0.22.2](https://github.com/imputnet/helium/releases/tag/0.22.2) and main at `f32f2c066787492b9ba112dc1be1ad230b53658a`, targeting Chromium `158.0.8127.36` |
| Helium macOS | [Current main](https://github.com/imputnet/helium-macos/commit/0e6652ec877e64a32bb732d8f8d00d56bcb6d46e) at `0e6652ec877e64a32bb732d8f8d00d56bcb6d46e` pins core 0.22.2. The latest published macOS release observed was [0.22.1.1](https://github.com/imputnet/helium-macos/releases/tag/0.22.1.1). |
| Ungoogled Chromium | [158.0.8127.36-1](https://github.com/ungoogled-software/ungoogled-chromium/releases/tag/158.0.8127.36-1) at `76f39e0fead37326b9ba0440831336b198a17246` is an ancestor of new Helium core. |
| Chromium 159 comparison target | `159.0.8154.13` at `4d790f9eb4c8abe65b8aaa3feba664e7c734ba56`. Google lists this Early Stable build for both macOS CPU families, and Imput provides both host overlays. The highest source tag observed was `.30`. Recheck the release target before an adoption. [Chromium Dash](https://chromiumdash.appspot.com/releases?platform=Mac) · [Archives](https://github.com/imputnet/chromium-tarballs/releases/tag/chromium-159.0.8154.13) |

The `.13` checksum manifest matches the GitHub release asset digest. Both
metadata ZIPs match that manifest, identify the same Chromium commit and base
inventory, and cover arm64 and x64 targets. The base and both host archive URLs
responded successfully to HEAD requests.

## Updating Helium

A Git merge simulation against the locked Lune components flagged **103 core
patch files** plus the engine version, patch series and domain-substitution
list. It flagged **six macOS patch files** plus the series and core gitlink.
These counts measure direct Git merge conflicts. Many core conflicts put
Lune's earlier M158 port against upstream's own implementation of the M158
port. Compare behavior when deciding which Lune adaptations to retain on top
of upstream's complete series.

**Persistent pins are the largest user-facing change.** Upstream enables them
for every profile. Normal windows share pins, closing a pin hibernates it,
unpinning removes it from the other windows, and user-initiated navigation to
another site opens a regular tab. Upstream defers pin state changes until a
drag ends. Lune changes pin state during the drag to render the destination
and handle transfers between the grid and groups. The nine upstream pin
patches touch 47 source paths, 19 of which Lune-added patches also touch.
Those include six paths in Lune's individual pinned-grid drag patch and
eight in its pinned-group patch. Review profile migration, Cmd-W, tab
hibernation, URL behavior, mid-drag cancellation, cross-window moves and
pinned groups together. [Helium persistent pins](https://github.com/imputnet/helium/pull/2931) ·
[Pin layout](https://github.com/imputnet/helium/pull/2939) ·
[Lune grid drag](../features/pinned-grid-tab-drag.md) ·
[Lune pinned groups](../features/pinned-tab-groups.md)

**Native chrome has moved.** Upstream moved macOS frame materials from core to
the platform series. All ten files in the new platform patch also appear in
Lune's existing core frame-material patch. Reconcile ownership and ordering
before replaying Lune's edge-to-edge composition, then check fullscreen,
native resize, sidebar reveal and floating toolbar geometry. The Git
simulation also flags the fullscreen and Sparkle patches, which need separate
behavior checks. [Upstream frame move](https://github.com/imputnet/helium-macos/pull/428) ·
[Lune edge-to-edge frame](../features/edge-to-edge-frame.md)

## Porting the engine

The first ordered patch in Helium 0.22.2,
`upstream-fixes/wasm-interpreter-trustedcast-raw.patch`, fails forward
application against `.13` with zero fuzz and upstream whitespace handling.
All three V8 preimages match the verified arm64 source inventory. GNU patch
reports all three sections as reversed or previously applied, and a zero-fuzz
reverse dry run succeeds in all three files. This establishes that the patch
effect is present in the tested V8 source. Replay stopped at that patch.

The archive inventory comparison gives the size of the remaining review:

| Series | Patches | Patches touching altered or removed source paths | Paths removed from the source inventories |
| --- | ---: | ---: | ---: |
| Current Lune core | 350 | 268 | 27 |
| Current Lune macOS | 287 | 178 | 1 |
| New Helium core | 370 | 287 | 27 |
| New Helium macOS | 24 | 15 | 0 |

These counts compare the macOS arm64 base and host inventories for
`158.0.8127.37` and `159.0.8154.13`. A changed path can still apply cleanly.
The removed targets include Settings HTML, Safe Browsing and Reader Mode
sources. Of the files present in the old inventory, 91 paths in Helium
0.22.2's pruning list and 349 in its domain-substitution list are absent
from the new one. Review their replacements and regenerate the lists against
the new source before full preparation.

GN, Siso, Clang, Rust and both bundled macOS PGO profiles have different
bytes. Budget for cold builds on both targets. The macOS SDK selection file
has the same bytes, and runtime verification still needs to cover Lune's
macOS 13 deployment target.

## Validation sequence

1. Compose the new Helium core and macOS upstream revisions with Lune's
   feature patches on M158, using the upstream macOS gitlink and preserving
   ancestry and patch order. Use an arm64 preview to isolate pin semantics,
   native frame behavior and Settings before changing engine milestones.
2. Port that composition to the selected M159 tag. Review the already-present
   V8 change and the pruning/domain lists first, then refresh conflicts through
   quilt and unmerge into the owning component. Complete clean zero-fuzz
   preparation and prepared-source parity.
3. Before adoption, build and smoke-test arm64 and x86_64, recording any
   Intel-under-Rosetta results. Run the focused native drag, resize, fullscreen,
   shortcut, Settings, profile restart and update checks on the resulting builds.

Investigation evidence is under the ignored `.work/input-audit/` directory
inside this worktree. It includes both Git simulations, the source inventory
analysis, the checksum-verified metadata and the forward and reverse patch
logs. Full archives were not downloaded. Complete preparation, compilation
and runtime behavior remain unverified.
