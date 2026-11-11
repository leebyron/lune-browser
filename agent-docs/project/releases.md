# Release policy

Use [current status](status.md) for operational state and [release delivery](release-delivery.md) for executable commands, URLs and acceptance records. [Release commits](release-commits.md) defines frozen inputs and version identity. This document defines policy; it does not activate schedules or publish a release.

## Platforms and build environment

Support macOS arm64 and x86_64 with separate DMGs and Sparkle feeds. Use the local Mac runner without additional CI spend. Pin source archives, component commits, Xcode/SDK/Metal, compilers, Python, Sparkle and relevant build tools. Reuse caches only after comparison with a fresh preparation from locked inputs; retain the original caches and validation evidence. Bit-for-bit binary reproducibility remains unproven.

Build only reviewed sources on the signing host. Keep untrusted PR/fork jobs off that host, and keep signing credentials out of compilation environments. Signing and publishing consume the exact validated artifacts and their provenance. Intel-under-Rosetta checks do not establish physical Intel acceptance.

## Release gates

1. Validate the lock, source reachability, clean input trees, PR dependency order, core/platform gitlink and pinned toolchain.
2. Prepare fresh sources through the complete upstream pipeline, including substitutions, localization, resources and generated versions. Require patch replay without fuzz or rejects. Wait for complete successful preparation before selecting and reserving a version; failed or still-running preparation must not consume a version number. Bind the reservation to the completed report and exact browser lock.
3. Build both architectures. Run focused changed-feature tests and applicable browser checks for startup, navigation, tabs/windows, persistence, settings, extensions and uBlock.
4. Check packaged identity, profile/keychain paths, architecture, minimum OS, service endpoints, both effective updater feed selection and bundle metadata, and the Sparkle public key.
5. Sign nested components with Chromium's signing machinery. Notarize/staple the app and DMG; verify signatures and Gatekeeper acceptance.
6. Exercise the latest published release updating through a local feed serving the exact final signed DMG, then relaunch and check profile persistence on both architectures. Verify invalid-signature, incompatible-OS and wrong-architecture rejection. The legacy build-2 migration is no longer a recurring gate. Local fixtures are not a public delivery channel.
7. Bind acceptance to the version, source commit and exact DMG hashes. Acceptance on one physical device is sufficient for publication. Keep both architecture builds and automated software/update checks; Intel may execute under Rosetta. Publish the authorized release once these and the other technical gates pass, without waiting for manual Intel acceptance, another owner confirmation or a per-release deferral. Native Intel and additional OS testing are optional compatibility follow-up. This policy supersedes older hardware gates in historical evidence.
8. Apply the freshness gate before publication and again before promotion. Verify uploaded bytes, anonymous source refs and provenance before moving feeds. Verify both public feeds, latest links and the installed update path afterward.

Unpublished GitHub drafts are preparation tools. Use production/stable delivery, without a public staging channel or prerelease. Do not enable unattended publication merely because manual releases pass. New feature selection, conflict resolution and activation of automation require deliberate review and authorization.

## Versioning and publication

Use `YY.MMDD.N` consistently for the outer app, release tag/name and Sparkle version fields, following [the identity contract](release-commits.md#identity-and-version-rules). Allocate versions serially in Git. Never derive a new version from the build clock, reuse a published version or amend frozen inputs to include later changes. Keep Chromium's engine/framework version separate.

Source and releases belong in public `leebyron/lune-browser`. Each release uploads one `Lune-macos-ARCH.dmg` per architecture, paired appcasts, SHA-256 sums and compact release/validation metadata. The release-tag URL versions the asset; the fixed latest URL selects the same asset through GitHub's latest pointer. Do not upload duplicate DMGs, source kits, Git bundles or unchanged dependency archives. Verify signed source tags, permanent component refs and recorded dependency hashes, preserving licenses and attribution.

Publish and verify immutable browser assets before moving either feed. Commit both architecture feeds together using serialized fast-forward Git operations. GitHub's latest pointer is a separate operation: detect and repair partial promotion without replacing browser bytes or regressing to an older release. Preserve the last good delivery state on failure.

## Release-note style

Keep release notes terse and factual. Lead with new features, then bug fixes and security changes, followed by a compact engine-version/freshness note. Omit Downloads and compatibility and Testing and known issues sections. Keep routine installation instructions, test inventories and recurring boilerplate in the runbook and validation evidence.

Describe concrete changes without humor, lighthearted framing, marketing language or an internal work log. Tie each change to the frozen inputs and previous published version. Do not invent security fixes or imply an engine upgrade when Chromium is unchanged. State the exact engine and freshness status; keep test scope and limitations in validation evidence.

Keep each paragraph and list item on one source line. Allow natural wrapping; do not insert manual line breaks or hard-wrap prose.

Publication notes may be clarified later while browser binaries, tags and frozen records remain unchanged. Store revised publication notes separately from hash-locked historical notes, and verify GitHub readback.

## Sparkle delivery

Use one Lune-owned HTTPS stable feed per architecture, with the [canonical URL contract](release-delivery.md#public-url-contract). No former-repository feed or website redirect is retained. Both the plist and Sparkle delegate must select the canonical feed; changing only `SUFeedURL` is insufficient in this integration.

Apple code signing/notarization and Sparkle Ed25519 signing are separate. Keep both private credentials in Keychain. Sign the final notarized/stapled DMG bytes, then leave them unchanged. Embed the public key at build time, retain daily automatic checks and the manual Check for Updates action, and preserve independent update consent. Optional Helium service consent must not be required for Lune browser updates.

Use full downloads initially; delta updates are future work. Enclosures use immutable release-tag URLs, never moving latest URLs. If a defective release must stop being offered, withdraw its feed offer and publish a corrective higher version for installed clients. Do not assume Sparkle supports downgrades or that older code can safely open a newer profile.

The implementation follows Xelium's Chromium signing, notarization, DMG and Sparkle mechanisms under Lune's identity. Xelium's personal paths/keys and asset-clobber/draft-feed behavior are not Lune policy. See [the source research](research.md#4-xeliums-macos-release-path-is-concrete-and-reusable) for the original comparison.

## Chromium freshness gate

Use [Chromium Dash's official macOS Stable endpoint](https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Mac&num=1) at input selection, immediately before public release publication and again before feed/website promotion. Do not substitute downstream release versions, another platform/channel or a cached discovery result. Compare the complete numeric Chromium version in frozen inputs and packaged apps. Label a newer candidate as ahead of the observed Stable version, not as matching Stable.

Record Lune version/source commit, target architectures/channel, candidate and observed Chromium versions, UTC check time, source URL/channel/platform, response evidence, comparison (`current`, `ahead`, `behind`, `unknown`) and publication decision. Keep observations separate from frozen source records. A Stable update during building/acceptance can invalidate an earlier freshness claim.

Unknown, failed or malformed lookups block publication and promotion; preserve existing delivery and retry. A known lag requires explicit owner approval scoped to the exact version, commit and channel, with both engine versions, reason and acknowledged freshness gap disclosed. A new upstream Stable version or a different promotion needs a fresh decision. Approval never follows from a clean build, an old exception or generic permission to release, and does not waive any other gate.

The current publisher fails closed for lag and lookup failure. It has no automated known-lag exception input; using an exception requires a separately reviewed implementation and scoped owner approval. Discovery alone never satisfies this gate.

## Future automation

Scheduled integration and unattended publication are not enabled. The intended flow discovers latest macOS Stable independently of downstream cadence, attempts reviewed compatible integration, deduplicates by effective input hash, builds both targets and serializes version allocation/promotion. It stops on conflicts or failed validation and preserves the last good release. Never downgrade Chromium to satisfy optional UI patches or silently discard them.

Track latest Stable/ungoogled releases, selected Helium base, currently shipped engine, freshness decisions, lag and failed runs. Notify on meaningful changes or required action when monitoring is explicitly enabled. Rebuilding unchanged old inputs does not improve security freshness. See [remaining roadmap](roadmap.md).
