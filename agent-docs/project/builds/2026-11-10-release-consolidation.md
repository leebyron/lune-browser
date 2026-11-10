# Release repository and asset consolidation

Status (2026-11-10): production releases 26.1109.1 and 26.1109.2 are published in `leebyron/lune-browser`; 26.1109.2 remains latest. The former `lune-downloads` repository is left for the owner to delete manually. No compatibility feed or redirect is retained.

## Published assets

Each production release now has seven assets: `Lune-macos-arm64.dmg`, `Lune-macos-x86_64.dmg`, both architecture appcasts, `release.json`, `validation.json` and `SHA256SUMS`. Release-tag URLs identify immutable browser bytes. Latest-download URLs select those same assets through GitHub's latest-release pointer. The website requires no release-specific deployment.

The owner requested removal of duplicate version-named DMGs and the draft Intel test release. Both retained DMGs were compared against original signed files and GitHub's server-computed SHA-256 digests. Appcasts, delivery metadata and checksums were updated and verified before deletion. Both stable feeds and their delivery manifest were committed together on main; public raw feed readback confirmed the retained URLs before the duplicate assets were deleted. Browser bytes, signatures, source tags and frozen release records were unchanged.

The draft `acceptance-kit-26.1109.1` release and its test ZIP were removed. No corresponding test tag existed. Both production releases remain published.

## Verification

Anonymous readback matches the revised appcasts, release metadata and checksums for both versions. Version-specific URLs for all four retained DMGs return HTTP 200, as do both latest-download URLs. GitHub confirms exactly seven matching assets per release. Retained browser hashes match the previously completed full anonymous-download verification; the cleanup check uses fresh server digests and URL reachability rather than downloading identical binaries again.

Local receipts and verification are under `.work/release-asset-cleanup/`; the preceding repository-move receipts and full browser-download hash checks remain under `.work/release-consolidation/`. Both release descriptions were rewritten to be terse and factual, with natural line wrapping, and verified against GitHub readback.

The old production apps still embed the former repository's updater URL. Hosting cleanup does not change their signed binaries. After the former repository is deleted, users must manually install a new browser build with the canonical feed URL. Issue #24 and that URL change are accepted and adopted on main; frozen release 26.1110.1 is being built from signed source tag `v26.1110.1`, commit `db698200`.
