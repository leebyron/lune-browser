# Current project status

Updated November 10, 2026. This page summarizes operational state. Exact source and artifact identities live in the linked machine-readable records; dated feature reports retain their original validation scope.

## Release delivery

- **Published:** [26.1109.2](https://github.com/leebyron/lune-browser/releases/tag/v26.1109.2) is latest; [26.1109.1](https://github.com/leebyron/lune-browser/releases/tag/v26.1109.1) remains available. Both releases now contain one DMG per architecture, paired appcasts, checksums and compact metadata. The draft Intel test release was removed.
- **Building:** 26.1110.1 is frozen at signed tag `v26.1110.1`, source commit `db6982004a67e3c73dc9649db29e3de87717095e`. Its [release record](../../manifests/releases/26.1110.1.json) pins the accepted update-menu feature and canonical Sparkle URL. Fresh source preparation and both frozen builds pass. Both smoke checks and version staging pass. The owner restored `lune-notary`, and authenticated Keychain access passes. Signing/notarization and packaging have resumed; installed-update acceptance is pending. The source tag does not imply a published browser release.
- **Migration limit:** published .1/.2 binaries embed the former `lune-downloads` feed URL. The owner will delete that repository manually. No compatibility redirects are retained; a manual install of the next browser release will restore stock updating after deletion.
- **Evidence:** [consolidation](builds/2026-11-10-release-consolidation.md), [26.1109.2 validation](builds/2026-11-09-release-26.1109.2.md), [update-menu validation](features/app-menu-update-check.md), [26.1110.1 build evidence](builds/2026-11-10-release-26.1110.1.md).

## Inputs and validation

The [development lock](../../manifests/browser.lock.json) is authoritative for current component commits and permanent input tags. The [patch manifest](../../manifests/patches.json) records feature provenance, order and hashes. Frozen release records and their source tags are authoritative for each released or reserved version; later main-branch changes do not alter them.

Current Chromium is **158.0.8127.18**, with the reviewed ungoogled/Helium forward port; this is not a claim that 158 is the official macOS Stable channel. The November 10, 09:02 UTC input check observed Stable **157.0.8103.51**. A fresh lookup is still required before each publication and promotion. Preserve the ungoogled base identity separately from the Chromium target.

Both architectures build on the local Apple silicon Mac. Intel runtime checks use Rosetta unless a report explicitly identifies physical hardware. The owner has Intel Macs on macOS 13.7.8 and 26.6.2 for manual checks; their availability is not acceptance of any particular binary. Prior version-bound deferrals do not automatically cover a new release.

## Hosting and automation

The public source repository also hosts releases and paired raw-GitHub stable feeds. The [Cloudflare website](website.md) links to fixed GitHub latest-asset URLs. Optional browser services use Helium's hosted service; Lune-hosted services are not deployed.

Use the existing self-hosted Mac runner with no added CI spend. Manual browser builds, setup checks and website deployment are guarded workflows. Scheduled browser builds and unattended publication are not enabled. Credentials stay in Keychain; generated sources, caches and signed artifacts stay in ignored workspaces.

## Known open product issues

The Make default browser sidebar item can be absent on the reported macOS 13 install; Settings > Default browser remains available. Native resize cursors can flicker while Lune is active; resizing remains functional. Do not claim either fixed without new evidence. Other feature reports and open GitHub issues contain their scoped limitations.
