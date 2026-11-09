# Builds, releases, and automatic updates

Status: local signing, notarization, DMG packaging, Sparkle appcast generation,
and installed-update validation are implemented for the first release candidate.
Public delivery and native Intel acceptance are in progress; stable promotion and
recurring browser publishing are not enabled. See [release bootstrap](builds/2026-11-06-release-bootstrap.md)
and [current build readiness](building.md).
Initial targets: macOS arm64 and x86_64, with separate DMGs and update feeds.

## Daily integration

A scheduled job discovers upstream changes and produces an immutable candidate
lock. Skip rebuilding when all effective inputs are unchanged. Allow manual
dispatch for urgent fixes. Deduplicate candidates by input hash and serialize
promotion per release channel.

Chromium's latest macOS stable release determines the target, independently of
downstream release cadence. Check at input selection and again immediately before
release publication or feed/website promotion. A candidate behind stable is
blocked by default; the owner may explicitly approve a recorded exception for
that release after acknowledging the gap. An unavailable check means freshness
is unknown and blocks promotion. See the [freshness gate](#chromium-freshness-gate)
for evidence and exception requirements. Automatic promotion and this final gate
are not yet implemented.

GitHub Actions can coordinate the jobs; a reliable external cron can dispatch the
same workflow if needed. Use an off-hour-minute schedule and a missed-run monitor:
[GitHub documents](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
that scheduled jobs can be delayed/dropped and inactive public repositories can
have schedules disabled. Do not equate a scheduled workflow with a daily guarantee.

The state machine is:

```mermaid
flowchart LR
  A[Discover and lock inputs] --> B[Compose Git histories]
  B --> C[Prepare and validate Chromium sources]
  C --> D[Build and test arm64 and x86_64]
  D --> E[Sign, notarize, package, verify]
  E --> F[Publish immutable release assets]
  F --> G[Verify downloads and promote feeds]
  G --> H[Update website manifest]
```

Any failed gate blocks promotion. Record the exact component, patch/commit,
Chromium version, logs, and last successful release. Distinguish Git conflicts,
patch rejects, dependency failures, compiler failures, test failures, and Apple
service failures. Keep the previous feed live. Retry transient failures against
the same locked candidate, without reusing a published build number.

## Build environment

The owner requires no additional CI spend. Start with this Mac as a self-hosted
GitHub Actions runner and keep download/compiler caches on local disk. The manual development browser workflow exists; storage/Xcode/Metal preflight
passes. The first arm64 build and headless runtime smoke test passed, with
compilation/linking taking 2h21m29s on this Mac; see [first-build evidence](builds/2026-11-05-arm64.md).
The subsequent [Chromium 158 build](builds/2026-11-05-chromium-158-port.md) passes on
both targets, with Intel compilation taking 3h15m26s and Intel runtime checked
under Rosetta. Final translation-only refreshes took 13s on arm64 and 18s on Intel.
Continue measuring storage, memory, build duration, and cost before promising a daily cadence;
one successful development run does not establish unattended release reliability. Pin Xcode/SDK, compilers, Python,
Sparkle, source archives, and relevant build tools. Namespace caches by toolchain,
architecture, flags, and source inputs, and periodically verify clean builds.

Helium's macOS tooling supports x86_64 builds on Apple silicon. That can simplify
compilation capacity, but still validate the Intel app on Intel hardware. Use
separate source/output directories for architecture-specific configuration and
packaging. Never package whichever binary happens to be left in `out/Default`.

Separate untrusted PR checks from release jobs. Pin third-party Actions and avoid
running arbitrary PR code on a persistent signing host. Build jobs receive no
signing secrets. The signing/publishing step accepts only the exact artifacts
and provenance of the validated candidate; credentials are scoped to that step.

## Release gates

1. Validate the lock, source reachability, clean input trees, PR dependency order,
   core/platform gitlink agreement, and toolchain availability.
2. Run upstream series/config validation and a fresh full source preparation.
   Require patch application without fuzz or rejects. Verify substitutions,
   resources, and generated version metadata, not only patch files.
3. Build both targets and run focused tests for changed features plus browser
   smoke checks: startup, navigation, tabs/windows, profile persistence,
   settings, extension installation/update, and uBlock operation.
4. Check the packaged identity, profile/keychain paths, architecture, minimum OS,
   service endpoints, updater feed, and embedded Sparkle key.
5. Sign nested components using Chromium's signing machinery; notarize/staple
   the app and DMG, then validate signatures and Gatekeeper acceptance.
6. Test an installed previous Lune release updating to the candidate through a
   staging feed on both architectures, followed by relaunch and profile checks.
   Also test a bad signature, incompatible OS, and wrong-architecture offer.
7. Apply the [Chromium freshness gate](#chromium-freshness-gate) before public
   release publication and again immediately before feed/website promotion.
   Verify published downloads, hashes, source/provenance attachments, and feed
   consistency before promotion. Verify feed readback afterward.

At bootstrap, keep public auto-promotion disabled until the two-release update
exercise passes. After that, routine candidates may publish automatically under
these gates without daily manual approval. New feature selection and conflict
resolution remain deliberate changes to the reviewed input policy.

## Reuse Xelium's mechanisms, adapt the implementation

[Xelium's release script](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/release.sh)
builds, packages, invokes Sparkle `sign_update`, creates an appcast, and publishes
with `gh release`. Its [packager](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/sign_and_package_app.sh)
uses Chromium signing scripts, `notarytool`, `stapler`, and a DMG.

Use that sequence with Lune's Developer ID, bundle/profile/keychain identity,
Sparkle key pair, repository, feeds, and artwork. Parameterize architecture and
generate release notes from the lock. Do not copy Xelium's hard-coded arm64 paths,
personal certificate, public key, sibling tool locations, or fixed feature list.

Xelium can replace release assets with `--clobber` and commits its appcast to
`main`. Lune should instead assign a unique version to every public build and
keep release outputs outside the source branch. Its draft mode still reaches
the appcast commit/push block; a Lune draft must never advance a public feed.

## Versioning and publication

The owner selected `YY.MMDD.N` for Lune's release version on November 8, 2026:
for example, `26.1108.1`, then `26.1108.2` for the next release that day.
The daily release counter starts at 1. Use the same string for the outer app's
`CFBundleVersion` and `CFBundleShortVersionString`, Sparkle's `version` and
`shortVersionString`, and human-facing release names. Record the assigned release
date and counter in Git before packaging; rebuilding a commit must not derive a
new version from the host clock.
This is an accepted scheme, not yet implemented: packaging and appcast generation
still use integer build numbers and the locked Chromium version as the display
version. Published builds 1 and 2 retain their original metadata.

The date version supplies Sparkle's increasing update order; no separate lifetime
build counter is needed. Serialize allocation, share the version across both
architectures, and retain the full source SHA separately. Record Chromium,
ungoogled, and Helium identities in the locked inputs and release provenance.
Show Lune and Chromium versions separately in About. See
[release commits and version information](release-commits.md) for the required
input record, calendar rules, preparation procedure, evidence, and migration gaps.

Target artifact naming: `Lune-<version>-macos-<arch>.dmg`, tagged `v<version>`.
Publish DMGs, SHA-256 sums, source locks, patch provenance, corresponding source
availability, and validation results under an immutable release tag on `main`.
Keep permanent component tags reachable as described in [architecture](architecture.md).

Publish and verify both architecture assets before changing either stable feed.
Use a conditional/serialized feed update so a slower old job cannot replace a
newer release. With separate feeds, promotion is not a cross-file atomic
transaction; both feeds must always reference already-available assets, and the
job must detect and repair partial promotion.

## Sparkle delivery

Use Sparkle 2 as Xelium does, with one Lune-owned HTTPS feed per architecture and
channel. The selected feeds are `https://lune.computer/updates/stable/mac/appcast-arm64.xml`
and `appcast-x86_64.xml`, with staging feeds under `/updates/staging/mac/`. Separate
feeds prevent an Intel client receiving an arm64-only enclosure. Test any future
shared-feed filtering before adopting it.

Embed Lune's public key and matching feed URL at build time. Keep the Ed25519
private key in signing storage; Apple code signing and Sparkle update signing
are separate responsibilities. Sign the final notarized/stapled DMG bytes and
do not modify them afterward. Configure automatic checks with a daily interval
and preserve a manual Check for Updates action. Follow
[Sparkle's documentation](https://sparkle-project.org/documentation/) for key
management, appcast fields, and supported OS constraints.

Start with full downloads. Delta updates can follow after the full-update path
works. Retain compatible historical feed entries for older supported OS versions.
Keep staging and public feeds separate and avoid silently changing a user's
chosen channel.

If a release is defective, remove its offer for clients that have not updated.
For already-updated clients, publish a corrective build with a higher version;
do not assume Sparkle can downgrade the app or that an older browser can safely
read a newer profile. Website/download metadata follows successful feed promotion.

## Chromium freshness gate

This applies to every release, including public prereleases, manual releases,
and staging-to-stable promotion. Use the official
[Chromium Dash macOS stable endpoint](https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Mac&num=1)
with `channel=Stable` and `platform=Mac`. Do not substitute the latest Helium or
ungoogled release, another operating system's channel, or a previous discovery
result. Compare the full numeric Chromium version in the frozen release inputs
and packaged app with the freshly returned version. A newer candidate must be
identified as ahead of the observed stable version, not mislabeled as matching it.

Check when selecting inputs and immediately before making a release publicly
available. Recheck immediately before promoting its feeds and website links,
even when the same bytes already passed staging. A stable update arriving during
compilation or acceptance invalidates an earlier claim that the candidate is
current; normally prepare a new candidate on the newer Chromium.

Record the following in release/promotion evidence, without amending the frozen
release commit:

- Lune version, full release commit SHA, target architectures and delivery channel.
- Candidate Chromium version and freshly observed latest macOS stable version.
- Check timestamp in UTC, source URL/channel/platform, and the returned release
  identity or response evidence.
- Comparison result (`current`, `behind`, `ahead`, or `unknown`) and the resulting
  publication/promotion decision.

If the candidate is behind, require an explicit owner-approved exception before
publishing or promoting it. Record who approved it, when, the approval reference,
both Chromium versions, the reason for shipping behind, and the acknowledged
security-freshness gap. Scope approval to the exact release commit, version and
channel; a new upstream stable version or a different promotion needs a fresh
decision. Automation must not infer approval from a clean build, prior exception,
or generic permission to release. Disclose the shipped Chromium version and known
lag in public release notes; do not describe an exception release as current.

A failed, missing, malformed or unavailable lookup yields `unknown`, never a
cached success. Keep the last good downloads/feeds unchanged and retry the check;
this is not the known-version exception path. Freshness exceptions do not waive
failed builds, patch conflicts, signatures, installed-update tests, or other
release gates. Attach promotion evidence as a separate record; do not rewrite
published artifacts or their original evidence.

The existing discovery command checks stable and rejects lag, but it is not a
publication gate. The release/promotion tooling still needs this final check,
evidence schema, explicit exception input, and stale-decision protection. Until
implemented, perform and record these steps manually for each release.

## Security freshness reporting

Record last poll, latest Chromium stable, latest ungoogled stable, selected Helium
base, currently shipped Chromium, the freshness check result and any approved
exception, and the reason for any lag. Notify on meaningful
lag, integration failure, missed scheduling, and promotion failure. A daily rebuild
of old inputs does not improve the browser's security profile.
