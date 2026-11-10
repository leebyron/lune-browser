# Remaining roadmap

Read [current status](status.md) for published releases, the active release and validation limits. This page describes future work, not authorization to activate schedules or deployments.

## Established foundations

- Public source and browser releases in one GitHub repository, upstream-derived component histories, permanent input tags and hash-locked composition.
- Fresh strict source preparation and arm64/x86_64 builds on the local Mac, with native Apple silicon and Rosetta browser checks.
- Developer ID signing, notarization, stapling, Sparkle signatures and installed-update acceptance tooling.
- Paired GitHub stable feeds, one DMG per architecture, version-specific downloads and fixed latest links on the Cloudflare website.
- Owner/main/repository guards on the free self-hosted Mac workflows.

## Finish the active release

Build 26.1110.1 from its frozen source tag, validate the signed apps and installed updates on both architectures, then prepare its unpublished GitHub draft. Publication must pass current freshness, artifact-bound acceptance and asset/readback gates. Physical Intel checks or an explicit version-bound owner deferral remain separate from Rosetta results. Existing .1/.2 users need a manual install after deletion of the old feed repository.

## Improve upstream integration

Target the latest official macOS Chromium Stable independently of Helium, ungoogled-chromium and Xelium release cadence. Recheck at input selection and before publication/promotion; do not permanently encode the present engine as the target. Preserve the separate ungoogled base and reviewed forward-port provenance.

- Automate upstream discovery and candidate deduplication by effective input hash.
- Exercise ordered PR replay, upstreamed-PR retirement and deliberate conflict reporting with small fixtures.
- Preserve upstream authorship and independently upstreamable browser features.
- Stop on conflicts or failed validation without dropping optional features or downgrading Chromium silently.

## Strengthen platform acceptance

- Complete artifact-specific native Intel installation, browsing, persistence and update checks on the owner's macOS 13.7.8 and 26.6.2 Macs.
- Verify older-macOS fallback appearance and the reported default-browser prompt behavior without claiming Rosetta covers them.
- Keep focused native UI regression tests and explicit owner acceptance for visual changes.
- Resolve open UI issues in individual scopes and single-thesis commits.

## Consider unattended releases

Scheduled builds and automatic publication are not enabled. Before activating them, validate no-change discovery, serialized version allocation and promotion, cache invalidation, failure recovery, and monitoring. Keep signing credentials separate from compilation and untrusted checks. Use the local Mac without added CI spend unless the owner changes that constraint.

Acceptance: changed upstream inputs can produce both validated browser artifacts, while a failed candidate leaves the last good release and feeds intact. Daily polling reduces avoidable delay; it does not guarantee every security fix is available immediately.

## Optional service hosting

Continue using Helium-hosted optional browser services with independent consent and clear attribution. Lune-hosted services are not deployed; previous Cloudflare Containers work was abandoned without deployment. Self-hosting is separate future work, requires an explicit request and validated hosting, and must not block browser releases. See [services](services.md).
