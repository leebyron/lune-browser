# Chromium 158 integration work

Status: source inputs verified and extracted; integration incomplete. This is a
separate workspace from the running Chromium 157 UI validation build. No build,
runtime check, or release validation of 158 has passed yet. The main lock remains
unchanged until a reviewed candidate is ready.

Target: macOS stable **158.0.8127.18**, Chromium commit
`6449d9f9a6a906edff724b7b220199b3fde4615c`, confirmed against Chromium Dash and the
archive's pinned dependency metadata. Both ungoogled and Helium still target 157
at this inspection. Lune continues to use their combined patch stack: ungoogled
commit `de09e0c70c6bc1ac83d4ecdfd0e82c7e250c9a3c` is an ancestor of core commit
`42da6c50c04f3b411879d5bdb1304f4d78ea9c81`. This port does not replace that stack
with stock Chromium.

## Inputs and workspace

Source: [imput's Chromium 158 archive release](https://github.com/imputnet/chromium-tarballs/releases/tag/chromium-158.0.8127.18).
The downloaded `SHA256SUMS` matches the GitHub asset digest
`8d12ad31273497cb5dee97c264e179b6fbc1b740d66a23de1617fee7535fb42c`.

| Verified input | SHA-256 |
| --- | --- |
| Base source archive | `3186d708deaa8dcf622b0f3ce696c8716894b1e047abf7afcef3117796461f34` |
| macOS arm64 host overlay | `fe8f6035fcbf735b8634d28cc5a34756a37450719a3bcd7cde1af7fa13ef17ff` |
| macOS arm64 metadata | `11337ad69b15d025d42c43ae87f8476ee54b2375da82859efe6cb1524ea08b4e` |
| macOS x64 metadata | `ec222d6ecbb31bf060b233c7eab0056a20cb5224aaca0dc30346ed20ed6fb9ec` |

The arm64 host overlay supports both target architectures. The x64 host archive
has not been downloaded; its metadata was retrieved for inspection. Onboarding,
search data, uBlock, and Sparkle archives retain their existing pinned hashes.

Ignored working directory: `.work/chromium-158/`. Native Git clones under `macos/`
and `macos/helium-chromium/` use local `integration/chromium-158` branches based on
the UI candidate's platform and core inputs. Core work is checkpointed on
`integration/chromium-158/helium`; these are not locked build inputs.
`downloads-arm64.ini`, archive metadata, and preparation logs are retained there.

## Preparation and patch-port progress

Strict binary pruning initially stopped on 29 paths absent from Chromium 158.
All previously pruned inputs were restored from the verified archives before
regenerating the pruning and domain-substitution lists with upstream tooling.
The JPEG XL dither-data exclusion now follows `jxl-v0_7` to `jxl-v0_8`; an obsolete
Windows toolchain-file exclusion was removed after confirming the file is gone.

Reviewed core pruning changes add 120 paths and remove 29; domain-substitution
changes add 103 and remove 160. New host-overlay and Sparkle vendor paths were
excluded from the core lists to preserve their separate platform treatment.
Removed domain-list entries that still exist were checked against the unchanged
upstream substitution rules. Strict pruning now passes. Configuration and list
changes are retained in core commit `4074a04d`.

Core commit `d5acb513` adapts the initial privacy patches for changed declarations,
Google URL helpers, profile-avatar checks, GCM startup, and AI integration. The
AI patch also disables Chromium 158's new ScreenAI-backed text-detection binding,
while preserving unrelated lazy service initialization.

Core commit `f139ea99` adapts the Safe Browsing compatibility patch. This preserves
its existing disabled-service behavior across changed checks and moved GN
entries. Chromium removed the entire V2 security-survey handler; its obsolete
hunks were retired after checking both implementation and declarations. The
remaining survey handler is still disabled by the original patch. The cloud
content-scanning test dependency moved into a conditional and is removed there.

The first **23 patches apply with zero fuzz**. Application currently stops at
`ungoogled-chromium/remove-unused-preferences-fields.patch`, with conflicts in
20 files requiring review. No patch has been skipped or forced. Full preparation,
GN generation, compilation, and runtime validation remain incomplete for 158.
The older 157 UI validation build is still a separate diagnostic build.

All selected UI features, Lune defaults, Kagi recommendation, Helium attribution,
and artwork remain required in the forward-port. New immutable component tags
and the main lock will be published only when the candidate is ready.
