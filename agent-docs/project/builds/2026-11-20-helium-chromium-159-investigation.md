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
another site opens a regular tab. Upstream's drag tracker allows provisional
tab-model changes and defers writes to the shared pin list until drag end.
Lune's provisional pin state renders the live destination and handles
transfers between the grid and groups. The nine upstream pin
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

## Update-by-update replay

The locked core and platform histories contain 24 and 12 new upstream
first-parent updates respectively. Merge commits count as one update.
For each update, the Git simulation uses its first parent as the base.
Paths Lune never changed start at that parent so missing earlier upstream
updates on those paths do not count as Lune conflicts. Paths Lune changed
use Lune's exact locked entries.

| Component | Updates | Clean Git merge | Git conflict | Conflict limited to engine version or gitlink |
| --- | ---: | ---: | ---: | ---: |
| Helium core | 24 | 10 | 14 | 1 |
| Helium macOS | 12 | 6 | 6 | 3 |
| Total | 36 | 16 | 20 | 4 |

A direct simulation against the untouched Lune inputs gives 13 clean and
23 conflicting updates. The ordered replay stopped at the first conflict
in each component, the intermediate Chromium `157.0.8103.50` version
change in core and the intermediate core gitlink in macOS. The per-update
results are independent diagnostics. They give neither a composed tree nor
a count of runtime regressions.

### Browser benefits and measured source results

Four zero-fuzz probes replayed the affected files through the existing Lune
series from checksum-verified Chromium 158.0.8127.37 source, putting each
candidate patch at its series position. The matching baseline replays passed.
Two new cleanup patches were also checked independently on copies whose
hashes match the locked [prepared-source evidence](2026-11-20-dock-icon-appearance.json).

| Upstream update | Benefit | Focused evidence |
| --- | --- | --- |
| [Canvas readbacks](https://github.com/imputnet/helium/pull/2928) | Consistent fingerprinting protection when a site reads a rectangle or the full canvas | Ordered file replay passed with zero fuzz and zero offsets. Test rendering and compatibility in the integrated browser. |
| [Zoom indicator](https://github.com/imputnet/helium/pull/2947) | Keeps the page zoom indicator visible with a long address | Ordered file replay passed with zero fuzz and six candidate hunk offsets. Visually check Lune's narrow floating toolbar. |
| [Certificate components](https://github.com/imputnet/helium/pull/2936) | Enables refreshed certificate trust data and more specific captive-portal or interception errors | Ordered file replay passed with zero fuzz and one candidate hunk offset. Verify Helium service delivery and Lune's update consent. |
| [M158 UI cleanup](https://github.com/imputnet/helium/pull/2934) | Removes the History sign-in prompt and Reading Mode address-bar chip | Both additive patches passed on prepared copies with zero fuzz and zero offsets. Keep Lune's existing Reading Mode access. |
| [Copy Download Link](https://github.com/imputnet/helium/pull/1511) | Adds a convenient way to copy a download's source URL | Git merged cleanly. Ordered replay rejected two headers. Chromium 158's Open With command already occupies the proposed command/metrics numbers. Preserve existing enum values and apply Lune's tracking-cleanup toggle and exceptions to the new clipboard action. |
| [Sync provider exclusions](https://github.com/imputnet/helium/pull/2890) | Keeps provider extension state out of its own sync vault | Git merged cleanly. The source and behavior need testing with the related provider API updates. |

Across all 36 updates, the other ten Git-clean items are tooling or revision
changes. The affected-file passes leave all unrelated source patches in
place. They do not establish generated-resource, compile or runtime behavior.

### Preserving Lune behavior

- Keep the accepted local pin drag, cancellation, animation, haptics and
  pinned-group behavior. Prototype Helium's commit-on-drop shared pin list
  around those local transitions. Check cross-window transfers and cancel
  before enabling profile-wide pin replication, close-to-hibernate or pin
  URL changes by default.
- Map upstream's Spacious density and relocated frame materials onto the
  existing Lune appearance settings. Preserve the native sidebar and
  toolbar layouts, synchronous resize and fullscreen behavior. Keep the
  Sparkle bridge and Lune's consent/channel handling when integrating the
  macOS changes.
- Review the larger [noise token update](https://github.com/imputnet/helium/pull/2850)
  separately from the canvas fix. It extends protection to workers and
  popups and stabilizes audio readbacks, but conflicts in three core patches.
  Check the new push and translation provider APIs alongside the existing
  service endpoint and consent policy.

The full per-commit results, conflict paths and zero-fuzz logs are in the
ignored `.work/input-audit/helium-delta/` directory. Browser pins remain at
the investigation baseline.

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
