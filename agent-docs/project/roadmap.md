# Implementation roadmap

Status: documentation, website, component imports, locked checkout/build tooling,
and local signing identities are bootstrapped. No browser has been compiled.
See [build readiness](building.md) and [website status](website.md).

## 1. Prove the repository model

Imported branches and permanent input tags are published. Lock validation, numeric
discovery, and workspace guardrails are implemented. PR replay/retirement and
automated composition remain stage 3 work; nonempty selections currently fail.

- Define manifest schemas and a small local command interface for fetching,
  composing, validating, building, and releasing.
- Import upstream histories into the proposed component branches with namespaced
  tags; pin the first core, macOS, and services inputs.
- Prove the macOS gitlink can resolve the composed core from the same remote.
  Clone it from scratch, including its submodule, without relying on local objects.
- Ensure automation loads Lune's agent/policy guidance when working in component
  checkouts, where `main`'s `AGENTS.md` is not automatically present.
- Test no-change discovery, exact PR pinning, upstreamed-PR retirement, and
  conflict reporting using small fixtures before downloading Chromium.

Acceptance: a clean checkout reconstructs the locked component workspace; all
input commits are durable and inspectable. Fall back to separate component forks
if same-remote branches complicate this unnecessarily.

## 2. Build the baseline on both architectures

- Use the complete compatible Helium stack first, without extra experimental PRs.
- Build arm64 and x86_64; measure disk, memory, cache effectiveness, and elapsed time.
- Add Lune's name, bundle/profile/keychain identity, artwork, and explicit versioning
  in isolated distribution commits.
- Validate browser behavior on Apple silicon and Intel with a separate test profile.

Acceptance: both local builds run, coexist with Helium, and pass baseline checks.
No signing/publishing credential is needed to establish this baseline.

## 3. Establish repeatable patch integration

- Select the first PRs and Lune feature topics deliberately; Xelium's selection
  is research input, not an automatic inclusion list.
- Implement ordered replay, provenance, dependency checks, upstream merge
  detection, and source preparation without fuzz.
- Exercise one new ungoogled release, a deliberate conflict, and retirement of
  a merged PR. Preserve the last good lock on failure.

Acceptance: candidates are reproducible from their lock, and integration failures
identify the exact upstream change or patch without silently dropping features.

## 4. Prove signing and updating

- Supply Lune's Developer ID/notarization credentials and create a distinct
  Sparkle key pair. Choose stable bundle ID and feed/domain paths.
- Parameterize packaging for both architectures; isolate signing from builds.
- Produce two successive staging releases and test N to N+1 installation,
  relaunch, profile persistence, wrong architecture, and invalid signatures.
- Verify asset-first publication, unique build numbering, and partial-feed
  promotion recovery.

Acceptance: a signed/notarized app updates correctly on both architectures.

## 5. Deploy services and website

- Domain selected: `lune.computer`, registered at DNSimple; website on Cloudflare
  Workers Static Assets. Choose a separate host for the Compose services.
- Deploy the pinned Compose stack with Lune config, TLS, secrets, and health checks.
- Audit and change client endpoints, then verify real browser traffic.
- Publish a website driven by the release manifest, with source and attribution.

Acceptance: browser services work independently under Lune's domains and website
downloads match the promoted release. Service rollback does not require rebuilding
the browser.

## 6. Enable unattended releases

- Configure scheduled discovery plus manual urgent dispatch, build capacity,
  candidate deduplication, signing, validation, and promotion.
- Run initial scheduled candidates without publication to establish reliability.
- Enable automatic promotion after all previous acceptance criteria pass.
- Monitor upstream lag, failed integration, missed runs, and update delivery.

Acceptance: a new upstream release flows to both architectures automatically when
every gate passes, and a failed candidate leaves the installed update path intact.

## Inputs still needed during implementation

| Decision | Current position |
| --- | --- |
| Platforms | Confirmed: macOS arm64 and x86_64 |
| Helium selection | Full stack selected for first development build |
| Additional PRs/features | Not selected |
| Git layout | Same-remote component branches and permanent input tags published |
| Build machines | No added CI spend; this Mac as a self-hosted Actions runner. Storage/Xcode/Metal ready; first CI build and Intel runtime validation pending |
| Signing | Developer ID and Sparkle keys in local Keychain; notarization setup pending |
| Domain and hosting | `lune.computer`; Cloudflare website, services host undecided |
| Minimum macOS version | Derive from selected source/toolchain and test matrix |
| Stable/preview policy | Stable first; staging required; preview optional |
| Scheduler | GitHub Actions initially; external dispatch if reliability requires it |

The website has its own deployment workflow. No recurring browser job, service
deployment, or browser release is enabled by this documentation.
