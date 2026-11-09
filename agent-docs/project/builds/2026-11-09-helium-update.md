# Helium upstream integration, November 9, 2026

Status: adopted development input. Chromium remains 158.0.8127.18.
This is a development input, not a browser release or stable promotion.

## Inputs and behavior

The core merge retains Lune's Chromium 158 port and imports Helium main through
`0a5feb312977be6feefca0766fcdd3c6a10ac9dd`. The previous upstream base was
`42da6c50c04f3b411879d5bdb1304f4d78ea9c81`; the previous composed core was
`3c3726b5935203480de96fdb08c9839a814fc2b9`.

The two upstream commits are:

- [`cfedec96`](https://github.com/imputnet/helium/commit/cfedec96da151aca255dae6480fdb3739cb4962c):
  separate history and bookmark autocomplete settings, enabled by default, with
  an Address bar settings section. Disabling history suggestions preserves the
  direct URL match. This changes providers; it does not replace Lune's native
  address-suggestion or Command-T rendering.
- [`0a5feb31`](https://github.com/imputnet/helium/commit/0a5feb312977be6feefca0766fcdd3c6a10ac9dd):
  a developer utility for trivial patch conflicts. Importing it does not enable
  automatic conflict resolution in Lune's pipeline.

The macOS candidate descends from main's reviewed UI input
`464c529859cd2b723320d3d43b1ddbd7fada1bc4`, preserving the accepted onboarding,
Command-T corner, and shared-tint changes published while integration was underway. The ungoogled base remains 157.0.8103.38-1; this update
neither upgrades nor downgrades Chromium.

The final core is `49bdc572bee38436250f9058351c8a328cd8c8ad` under
`inputs/helium-2026-11-09/helium`. The platform is
`ad51e3c36faf6097d0407ead1109e90a88dcaaaf` under
`inputs/helium-2026-11-09-4/macos`. The earlier `-3/macos` candidate remains preserved; `-4/macos` includes
the concurrent accepted Command-T refinement.

## Merge and source adaptations

The Git merge reported six conflict blocks across four patches: keyboard-shortcut
settings, profile-avatar settings, privacy-noise settings, and shortcut layout.
Comparison with the merge base proved the upstream side changed only hunk headers
in these files. The reviewed resolution preserves the existing Chromium 158 patch
bodies and context. Original upstream ancestry and authorship remain intact.

Strict source replay then required two context adaptations in the new patches:

- Chromium 158 removed redundant namespace qualifiers and reformatted nearby
  preference registrations in `omnibox_prefs.cc`.
- Chromium 158 added search-engine picker strings beside the settings resource
  registration insertion point.

Both patches were refreshed with quilt and unmerged into the core repository.
The platform service-disclosure patch had an existing no-final-newline assumption
for two XML files. Archive-backed replay exposed it; a separate platform commit
preserves the source's final newline without changing the disclosure text.
The newly published onboarding stack had the same final-newline assumption in
its update-consent and setup patches. Two setup patches also expected three
already-renamed body strings and a page title. Their removal-side context now
matches Helium's pre-substitution text. Added strings and behavior are unchanged;
name substitution still follows patch application. These repairs are separate
from the upstream feature integration.
No fuzzy patch application or feature removal was used.

## Validation

- Verified SHA-256/SHA-512 of all archives in the arm64 host download manifest.
  The host archive contains tools for both target architectures.
- Extracted the source files touched by the combined series directly from those
  archives, including onboarding, Sparkle, and uBlock inputs.
- All 524 core/platform patches apply with the normal `patches.py apply --no-fuzz`
  command across the 1,853 patch-touched paths. This is archive-backed patch replay,
  not a complete fresh source download/prune/build invocation.
- Core/platform patch lint, translation lint, input hashes, ancestry, permanent
  refs, and the platform core gitlink pass. All 44 orchestration tests pass.
- Full `chrome` and `chromedriver` builds pass for arm64 and x86_64.
- The seven autocomplete checks pass on both architectures: enabled defaults,
  packaged Settings controls, real bookmark/history results, independent toggles,
  both providers disabled with direct URL entry preserved, restart persistence,
  and re-enabling suggestions. Intel runtime checks use Rosetta.
- Existing browser smoke checks pass on both architectures: bundle/version and
  artwork, page loading and JavaScript, profile persistence, packaged UI,
  Settings bindings, and flag filtering.
- The packaged onboarding flow passes on both architectures, including service
  and update consent, selected search engine, appearance/layout choices, Back/Done
  behavior, and retained preferences. The onboarding XML generator passes for all
  102 messages with and without an XML declaration.

Validation uses a separate copy of the prepared source and build outputs under
`.work/helium-update/`. All patch-touched files are replaced from the archive-backed
replay and normal resource/name/translation processing is applied before building.
The existing development source and onboarding preview are not modified. Copied
Siso state contains absolute paths. Its `fs export` omits command history, so it
is insufficient for relocating an incremental build cache. The local validation
copy retains all original command/dependency/digest records and rewrites only
schema-defined filesystem paths; modified sources undergo normal dependency
checks. The final output/dependency snapshot was copied after the original build
was idle. Initial sandbox/cache relocation failures are not source failures and
are retained in the local logs. This cache experiment is not a pipeline change.
The first link exposed a stale native UI object after a newer original cache
snapshot was copied. Source timestamps differing from either cache snapshot were
then invalidated, forcing those files and their dependents to rebuild. The six
concurrently adopted Command-T source files match the final strict replay exactly.
The cache schema is [documented in Siso's source](https://chromium.googlesource.com/build/+/refs/heads/main/siso/hashfs/proto/state.proto).

The runtime fixture is `scripts/check-autocomplete-settings.py`. It checks default
preferences, packaged Settings controls, history and bookmark results, disabled
providers, direct URL preservation, restart persistence, and re-enabling providers
using a temporary profile and local fixtures. The diagnostic WebUI is enabled
only in that temporary profile. The history fixture is visited in a separate tab
and closed before querying, excluding open-tab matches. Native Intel hardware, older macOS,
signing, and installed updates remain outside this development validation.

Local evidence and build/runtime logs are in `.work/helium-update/`. The committed
lock and patch manifest identify the adopted components and exact patch hashes.
