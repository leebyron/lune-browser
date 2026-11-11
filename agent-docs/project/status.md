# Current project status

Updated November 10, 2026. This page summarizes operational state. Exact source and artifact identities live in the linked machine-readable records; dated feature reports retain their original validation scope.

## Release delivery

- **Published:** [26.1110.1](https://github.com/leebyron/lune-browser/releases/tag/v26.1110.1) is latest, with both stable feeds promoted. [26.1109.2](https://github.com/leebyron/lune-browser/releases/tag/v26.1109.2) and [26.1109.1](https://github.com/leebyron/lune-browser/releases/tag/v26.1109.1) remain available. Each release contains one DMG per architecture, paired appcasts, checksums and compact metadata. The draft Intel test release was removed.
- **Validation:** 26.1110.1 retains signed tag `v26.1110.1`, source commit `db6982004a67e3c73dc9649db29e3de87717095e`. Fresh preparation, both builds, signing/notarization, browsing/persistence, canonical-feed/consent checks and installed-update software checks pass (Intel under Rosetta). Single-device acceptance passes on the local Apple silicon Mac. Public-feed installed updates pass on both architectures, including relaunch and persistence. Both public feeds and complete versioned/latest download hashes match the final artifacts; the website uses these fixed latest links. Manual Intel testing is optional follow-up, not a publication gate.
- **Migration limit:** published .1/.2 binaries embed the former `lune-downloads` feed URL. The owner will delete that repository manually. No compatibility redirects are retained; a manual install of the next browser release will restore stock updating after deletion.
- **Evidence:** [consolidation](builds/2026-11-10-release-consolidation.md), [26.1109.2 validation](builds/2026-11-09-release-26.1109.2.md), [update-menu validation](features/app-menu-update-check.md), [26.1110.1 build evidence](builds/2026-11-10-release-26.1110.1.md).

## Inputs and validation

The [development lock](../../manifests/browser.lock.json) is authoritative for current component commits and permanent input tags. The [patch manifest](../../manifests/patches.json) records feature provenance, order and hashes. Frozen release records and their source tags are authoritative for each released or reserved version; later main-branch changes do not alter them.

Current Chromium is **158.0.8127.18**, with the reviewed ungoogled/Helium forward port; this is not a claim that 158 is the official macOS Stable channel. The November 10, 15:02 UTC promotion check observed Stable **157.0.8103.51**. A fresh lookup is still required before each publication and promotion. Preserve the ungoogled base identity separately from the Chromium target.

Main now includes owner-accepted [search-engine suggestions](features/search-suggestions.md) for future builds: address-bar and Command-T query/website suggestions, typed-search priority, Use defaults enabled, configurable onboarding opt-in, and the visible shared Search engine settings control. The development lock pins `inputs/search-suggestions-1/macos`; both builds and onboarding paths pass, with Intel runtime under Rosetta. Published release inputs are unchanged.

Both architectures build on the local Apple silicon Mac. Intel runtime checks use Rosetta unless a report explicitly identifies physical hardware. The owner has Intel Macs on macOS 13.7.8 and 26.6.2 for manual checks; their availability is not acceptance of any particular binary. Publish after single-device acceptance and the technical gates pass; manual Intel results and per-release owner deferrals are not required.

## Hosting and automation

The public source repository also hosts releases and paired raw-GitHub stable feeds. The [Cloudflare website](website.md) links to fixed GitHub latest-asset URLs. Optional browser services use Helium's hosted service; Lune-hosted services are not deployed.

Use the existing self-hosted Mac runner with no added CI spend. Manual browser builds, setup checks and website deployment are guarded workflows. Scheduled browser builds and unattended publication are not enabled. Credentials stay in Keychain; generated sources, caches and signed artifacts stay in ignored workspaces.

## Known open product issues

The Make default browser sidebar item can be absent on the reported macOS 13 install; Settings > Default browser remains available. Native resize cursors can flicker while Lune is active; resizing remains functional. Do not claim either fixed without new evidence. Other feature reports and open GitHub issues contain their scoped limitations.
