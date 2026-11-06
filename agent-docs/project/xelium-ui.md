# Xelium UI integration — 2026-11-05

The original 157 integration is documented below. The subsequent
[Chromium 158 candidate](builds/2026-11-05-chromium-158-port.md) has passed the
arm64 and Intel builds, arm64 headless/headed and Intel-under-Rosetta smoke tests,
internal artwork checks, French/German attribution checks, and focused native
arm64 sidebar, tab-switcher, and link-preview inspection. The main development
lock now selects those 158 inputs. Native Intel hardware and release validation
remain outstanding; the command bar retains documented upstream limitations.

Status of the original 157 port: reviewed source port. All 47 changed native production object targets
compile on arm64. Strict application of 160 relevant patches, focused GN header
checks, settings TypeScript/lint, onboarding generation, and source-default checks
pass. Svelte checking reports zero errors and warnings. Full arm64 browser compilation
and the packaged headless UI smoke test pass in the isolated 157 diagnostic clone. Native UI, Intel, and release validation remain
outstanding. This is a development candidate, not a current-security release.

## Chromium takes priority

The latest macOS stable version reported by
[Chromium Dash](https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Mac&num=1)
on 2026-11-05 is **158.0.8127.18**. Helium main and the newest ungoogled release
still target **157.0.8103.38**; Xelium's selected release targets **156.0.8078.79**.
The original port retained Lune's 157 baseline; it never downgraded to Xelium's
Chromium. The subsequent reviewed 158 forward port is now the development lock.
`scripts/lune.py discover` now checks Chromium stable independently and exits
unsuccessfully if the locked version is behind, even when ungoogled is current.
Daily scheduling and automatic publication are still disabled.

## Recorded inputs and scope

Source: [minervanet/xelium-macos at c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42](https://github.com/minervanet/xelium-macos/tree/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42).
The original selected patch files were imported unchanged in macOS commit
`22e61e7`, retaining Xelium author ikoshura's attribution. Compatibility changes
are separate commits. Imported licenses and source copyright notices remain.

| Upstream contribution | Author | Reviewed state | Shipped implementation |
| --- | --- | --- | --- |
| [Helium #2747](https://github.com/imputnet/helium/pull/2747), comfortable interface size | dumbmoron | Open, unmerged | Xelium port plus Chromium 157 adaptation |
| [Helium #2367](https://github.com/imputnet/helium/pull/2367), address bar in sidebar | heloess | Closed, unmerged | Xelium port plus Chromium 157 adaptation |
| [Helium #2539](https://github.com/imputnet/helium/pull/2539), visual tab switcher | beeltec | Open, unmerged | Xelium port plus Chromium 157 adaptation |

`manifests/patches.json` records each PR's full base/head, ordered commits,
author, dependencies, rationale, permanent input ref, and adaptation. These PR
heads are provenance snapshots; **the actual shipped patches are Xelium's
adaptations**, not a claim that today's PR commits were directly cherry-picked.
The manifest records both original Xelium and composed patch hashes.

The 22 selected Xelium patches also include native command bar, link preview,
sidebar address bar and pin button, toolbar/top-bar split, app-menu reveal,
comfortable vertical-tab sizing, pinned-tab row limits, and frame sizing/materials.
Experimental workspaces are not in Xelium stable and are not included. Xelium's
branding, bug-report links, updater identity/feed, signing shortcuts, and release
scripts are not imported. Lune retains its own bundle/profile/key identity.

## Reviewed adaptations

- Chromium 157 moved frame sources out of the large UI GN target. Sidebar-header
  and visual-switcher sources are attached to their actual frame targets.
- Vertical-tab constants moved into `tabs::`; density-aware collapsed sizing
  follows those changes. Preserve the new segmented expand-on-hover behavior.
- Preserve the new tab-scroll-button visibility observer while adding pinned-row
  preference observation. Remove references to settings properties retired in 157.
- Chromium refactored `ThumbnailTabHelper`, removing its nested state tracker.
  Connect preview caching to the current readiness/lifecycle API, preserving
  discarded-tab and deferred-restoration protections.
- Xelium's command-bar and link-peek patches duplicate 13 shared plumbing hunks.
  Comparison confirmed identical resulting code; the link-peek port excludes
  those duplicate hunks and depends on the command-bar patch. No feature is dropped.
- Refresh changed contexts and hunk counts with exact matching; never use fuzz.
  Original source and compatibility commits remain independently reviewable.
- New feature strings currently use English fallbacks. Full translation coverage
  and upstream maintainer acceptance are not claimed.

## Lune defaults and attribution

Read only the relevant preferences from the owner's local Xelium profile. Do not
copy browsing history, accounts, extensions, cookies, services consent, or
onboarding-completion state into the repository or new profiles.

- Vertical tabs, aligned right, expanded at 200 px, expand-on-hover enabled.
- Frameless mode, sidebar pinned, top chrome unpinned, address bar in sidebar.
- Standard density, 4 px frame, centered location bar, avatar button hidden.
- Command bar enabled; link peek disabled. Both remain configurable.
- Xelium's visual MRU tab switcher enabled; at most four pinned tabs per row.

These are registration defaults, not migrations that overwrite existing choices.
Kagi appears first during onboarding with a suggestion and paid-account note.
Selecting it explicitly changes the search provider; an existing provider is not
silently overwritten, and DuckDuckGo remains available.

Onboarding and About both say “Built on Helium, with thanks to its authors and
contributors” and link to `https://helium.computer/`. The two credit message IDs
are explicitly excluded from Lune's display-name substitution. Existing upstream
copyright/license information is retained. This does not imply endorsement.

The new [Pelagic Signal icon](../../branding/README.md) uses the paired-lune
geometry and gamut-mapped palette from Lune / Color Atlas. The `.icns` and product
artwork are pinned in the platform component; the editable source and renderer
are on the orchestration branch. A broader onboarding/legal/service-link audit
is still required before public release.

## Build contract and validation

This implements **reviewed composition**, not a generic automatic PR replayer.
The pipeline consumes the already-composed platform commit. Validation checks
its identity, patch hashes and series order, PR source refs, ordered commit
metadata, and dependencies. A new PR head or changed patch requires review,
recomposition, new immutable inputs, and a lock update. Unknown selections fail.

The original successful app/source/output remain under the runner checkout.
Development work uses `.work/ui-port/` (quilt staging and evidence) and an APFS
clone `.work/ui-build-src/` for compilation. Build log:
`.work/ui-port/full-build.log`. These are ignored, not release inputs or published
artifacts. Compilation here is incremental development evidence; release
validation still requires full fresh preparation through the locked wrapper.

Source validation reconstructed all affected files from the hash-pinned Chromium
and onboarding archives, applied the relevant baseline patches in order, then
applied every selected patch with GNU patch `--fuzz=0`. The complete imported
Helium/macOS series is unchanged outside this port. The platform merge/unmerge
round trip leaves the core component unchanged. Lune name substitution was also
run on the reconstructed strings; both Helium credits survive. Twenty orchestration
guardrail tests pass, including detection of Chromium lag while ungoogled is current.
A fresh recursive checkout from GitHub resolves the exact platform/core pair.

CI runs `scripts/check-ui-port.py` and `scripts/check-onboarding.py` after source
preparation. These checks verify defaults, Kagi ordering/text, surviving Helium
credits, and all 80 generated onboarding strings. They do not replace native
behavior checks: sidebar layout/pinning, Cmd+T/L, Ctrl+Tab with thumbnails and
list mode, link peek opt-in, new-profile onboarding, About links, app icon, and
profile isolation must be exercised on the built app on both architectures.

After compilation finishes, run the isolated arm64 smoke test against that output:

```sh
python3 scripts/smoke-browser.py .work/ui-build-src/out/Default \
  --ui --report out/validation/xelium-ui-smoke.json
```

The optional `--ui` checks exercise packaged About/onboarding credits, search
recommendations, registered defaults, and the pinned app icon. They disable
services in the disposable profile before navigating onboarding and block external
DNS resolution. `--headed` shows the test window; neither mode automates native
sidebar/keyboard interaction checks. The extended runner's original browsing and
persistence checks passed against the preserved first app; the new WebUI checks
remain pending until this candidate finishes compiling.

## Packaged diagnostic build result

The Chromium 157 arm64 diagnostic build completed 41,297 actions in 2h4m53s.
`out/validation/xelium-ui-smoke.json` records a passing headless test of page
loading, JavaScript, persistence across relaunch, all 18 expected preferences,
Helium credits in About and onboarding, and the Kagi-first recommendation with
its paid-account disclosure. Kagi remains an explicit user choice; DuckDuckGo is
available and remains selected until the user changes the provider.

The packaged icon matches SHA-256
`3b6224273905dc9a7c789f9a332c81982d75becf75793e1d47e0d152692f3dc0`.
The test uses canonical `chrome://` URLs because WebDriver bypasses the omnibox's
`helium://` alias fixup, and reads engine-name text independently of tooltip text.
Native control interaction is not covered by this headless report. Intel,
signing, packaging, updates, and the [158 build](builds/2026-11-05-chromium-158-port.md)
remain unvalidated.
