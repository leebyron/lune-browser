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
the UI candidate's platform and core inputs. They are not published build inputs.
`downloads-arm64.ini`, archive metadata, and preparation logs are retained there.

## First compatibility finding

Strict binary pruning stopped on 29 paths absent from Chromium 158. Comparison
with the verified pristine archive inventories identifies removed test fixtures,
the removed glmark2 tree, and JPEG XL's move from `jxl-v0_7` to `jxl-v0_8`.
The required dither-data exclusion must follow that dependency rename. New test
fixtures also need review; deleting stale list entries alone is insufficient.

Restore the exact previously pruned inputs from the verified archives, regenerate
proposed pruning/domain lists with upstream tooling, and review their differences.
Then rerun strict pruning and quilt application. Do not suppress missing-file
errors, weaken domain substitution, or use fuzzy patch application. All selected
UI features, Lune defaults, Kagi recommendation, attribution, and artwork remain
required in the forward-port.
