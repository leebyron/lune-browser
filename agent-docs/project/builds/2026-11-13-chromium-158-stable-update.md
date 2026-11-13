# Chromium 158.0.8127.37 release preparation

Status: input review complete; fresh preparation, builds and release validation are pending. This isolated candidate is not selected on main or published.

The official Chromium Dash macOS Stable lookup on November 13, 2026 reports 158.0.8127.37. The prior Lune engine is 158.0.8127.18. The Chromium tag resolves to `b8c2be851f62f6a394ec57955d7f31335d7cb6d4`, matching both verified host metadata archives. The source release is <https://github.com/imputnet/chromium-tarballs/releases/tag/chromium-158.0.8127.37>.

This is a maintenance update of the existing reviewed Chromium 158 port. It retains the ungoogled 157.0.8103.38-1 base and its complete combined Helium patch stack; it does not represent that base as a new ungoogled release. The preceding port review is [retained](2026-11-05-chromium-158-port.md). The candidate retains main `f26546fcd3dd9b69476d0f925f2d3a8fced8085a`, including the accepted tab-group menu, naming and expanded-group separators.

Published archive checksums and both metadata ZIPs were verified. The normalized inventories differ in 1,254 source/dependency entries. GN, Siso, Clang and Rust compiler bytes are unchanged; both bundled PGO profiles change and are pinned in the release recipe. Both host download manifests select the new base and matching host overlay. Fresh complete zero-fuzz preparation remains required; no patch is silently dropped or fuzz-applied.

The official early-Stable announcement is <https://chromereleases.googleblog.com/2026/11/early-stable-update-for-desktop_0520415684.html>. This is an early Stable rollout, not a claim of full rollout. No CVE count is inferred from this announcement. Source fixes overlap with selected backports in Chromium 157.0.8103.78, but the release target remains the newer Chromium 158 branch.

Storage cleanup covers the owner's ten explicitly approved historical generated source/build trees. Complete source-difference archives and quilt metadata are retained against the unchanged 26.1111.3 preparation inventory. Signed releases, frozen source records, concise evidence, component checkouts, download caches and current development/latest-release build caches are retained.

## Approved translation-helper adaptation

The archive-backed strict patch-target replay stopped at core patch 145, `helium/core/degoogle-context-menu.patch`: Chromium renamed `CanPartiallyTranslateTargetLanguage` to `CanPartiallyTranslate` while restoring partial translation for PDFs. The owner approved the exact two-name patch adaptation on November 13. Core commit `e5049134` changes only the function name in the context and the removed upstream call; both full-page and partial-translation eligibility still return false. No hunk is dropped or fuzz-applied. Restarted strict replay and complete preparation remain required.

## Approved noise-patch context refresh

Strict patch-target replay next stopped in `helium/core/noise/core.patch`: Chromium replaced a srcdoc TODO comment with the new navigation-check explanation. The owner authorized the proposed one-line context refresh when continuing on November 13. Core commit `14053646` changes only this context comment. The complete main-frame noise-token synchronization insertion and its position before srcdoc handling remain unchanged. Complete zero-fuzz source preparation is still required.

## Scoped storage exception

The owner authorized a one-time 170 GiB source-preparation floor when continuing on November 13, after the approved historical cleanup left approximately 179 GiB free. This exception applies only to preparing Chromium 158.0.8127.37 for this release. The normal 200 GiB policy remains unchanged, as do the 80 GiB pre-build floor and every source/build/signing/runtime/update/publication gate. The [machine-readable exception](2026-11-13-preparation-storage-exception.json) retains the exact selected component identities.
