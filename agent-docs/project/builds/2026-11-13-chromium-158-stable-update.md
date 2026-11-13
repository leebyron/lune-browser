# Chromium 158.0.8127.37 release preparation

Status: input review complete; fresh preparation, builds and release validation are pending. This isolated candidate is not selected on main or published.

The official Chromium Dash macOS Stable lookup on November 13, 2026 reports 158.0.8127.37. The prior Lune engine is 158.0.8127.18. The Chromium tag resolves to `b8c2be851f62f6a394ec57955d7f31335d7cb6d4`, matching both verified host metadata archives. The source release is <https://github.com/imputnet/chromium-tarballs/releases/tag/chromium-158.0.8127.37>.

This is a maintenance update of the existing reviewed Chromium 158 port. It retains the ungoogled 157.0.8103.38-1 base and its complete combined Helium patch stack; it does not represent that base as a new ungoogled release. The preceding port review is [retained](2026-11-05-chromium-158-port.md). The candidate retains main `f26546fcd3dd9b69476d0f925f2d3a8fced8085a`, including the accepted tab-group menu, naming and expanded-group separators.

Published archive checksums and both metadata ZIPs were verified. The normalized inventories differ in 1,254 source/dependency entries. GN, Siso, Clang and Rust compiler bytes are unchanged; both bundled PGO profiles change and are pinned in the release recipe. Both host download manifests select the new base and matching host overlay. Fresh complete zero-fuzz preparation remains required; no patch is silently dropped or fuzz-applied.

The official early-Stable announcement is <https://chromereleases.googleblog.com/2026/11/early-stable-update-for-desktop_0520415684.html>. This is an early Stable rollout, not a claim of full rollout. No CVE count is inferred from this announcement. Source fixes overlap with selected backports in Chromium 157.0.8103.78, but the release target remains the newer Chromium 158 branch.

Storage cleanup is limited to the owner's four explicitly approved older generated build trees. Signed releases, frozen source records, concise evidence, component checkouts, download caches and current development/latest-release build caches are retained.
