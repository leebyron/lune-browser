# Current project status

Updated November 11, 2026. This page summarizes operational state. Exact source and artifact identities live in the linked machine-readable records; dated feature reports retain their original validation scope.

## Release delivery

- **Published:** [26.1110.1](https://github.com/leebyron/lune-browser/releases/tag/v26.1110.1) is latest, with both stable feeds promoted. [26.1109.2](https://github.com/leebyron/lune-browser/releases/tag/v26.1109.2) and [26.1109.1](https://github.com/leebyron/lune-browser/releases/tag/v26.1109.1) remain available. Each release contains one DMG per architecture, paired appcasts, checksums and compact metadata. The draft Intel test release was removed.
- **Validation:** 26.1110.1 retains signed tag `v26.1110.1`, source commit `db6982004a67e3c73dc9649db29e3de87717095e`. Fresh preparation, both builds, signing/notarization, browsing/persistence, canonical-feed/consent checks and installed-update software checks pass (Intel under Rosetta). Single-device acceptance passes on the local Apple silicon Mac. Public-feed installed updates pass on both architectures, including relaunch and persistence. Both public feeds and complete versioned/latest download hashes match the final artifacts; the website uses these fixed latest links. Manual Intel testing is optional follow-up, not a publication gate.
- **Migration limit:** published .1/.2 binaries embed the former `lune-downloads` feed URL. The owner will delete that repository manually. No compatibility redirects are retained; a manual install of the next browser release will restore stock updating after deletion.
- **Evidence:** [consolidation](builds/2026-11-10-release-consolidation.md), [26.1109.2 validation](builds/2026-11-09-release-26.1109.2.md), [update-menu validation](features/app-menu-update-check.md), [26.1110.1 build evidence](builds/2026-11-10-release-26.1110.1.md).
- **Next release:** [26.1111.2](builds/2026-11-11-release-26.1111.2.md) is frozen at `e0dcb1e96c6f6ec402f4195840b50f3ad82789b4`. Both final DMGs are signed/notarized; signed runtime, canonical-feed/consent and installed-update/rejection checks pass, with single-device acceptance on Apple silicon (Intel under Rosetta). Unlocking restored access to the existing Keychain profile without credential re-entry. Publication remains pending; stable feeds still offer 26.1110.1. The unused, never-uploaded 26.1111.1 entry was removed at the owner's request. Future allocations require completed clean preparation, and routine update tests use the latest published release.

## Inputs and validation

The [development lock](../../manifests/browser.lock.json) is authoritative for current component commits and permanent input tags. The [patch manifest](../../manifests/patches.json) records feature provenance, order and hashes. Frozen release records and their source tags are authoritative for each released or reserved version; later main-branch changes do not alter them.

Current Chromium is **158.0.8127.18**, with the reviewed ungoogled/Helium forward port; this is not a claim that 158 is the official macOS Stable channel. The November 10, 15:02 UTC promotion check observed Stable **157.0.8103.51**. A fresh lookup is still required before each publication and promotion. Preserve the ungoogled base identity separately from the Chromium target.

Main now includes owner-accepted [search-engine suggestions](features/search-suggestions.md) for future builds: address-bar and Command-T query/website suggestions, typed-search priority, Use defaults enabled, configurable onboarding opt-in, and the visible shared Search engine settings control. The feature entered the development lock through `inputs/search-suggestions-1/macos` and remains in the current platform input; both builds and onboarding paths pass, with Intel runtime under Rosetta. Published release inputs are unchanged.

The owner-accepted [Customize icon removal](features/trailing-toolbar-controls.md#customize-temporary-icon-removal) is included in future builds through signed platform input `inputs/customize-icon-1/macos`. Opening Customize no longer adds a temporary config icon to the trailing strip; both architecture builds and live Apple silicon panel checks pass. Published releases retain their frozen inputs.

The owner-accepted [DevTools header hover fix](features/devtools-header-hover.md) is included in future builds through signed platform input `inputs/devtools-header-hover-1/macos`. Side-docked DevTools no longer reveal or retain the hover header; page content and the visible tabs sidebar remain eligible. Published releases retain their frozen inputs.

The owner-accepted [Command-T bang suggestions](features/command-bar-bangs.md) are included in future builds through signed platform input `inputs/command-bar-bangs-1/macos`. Installed bang services participate in typeahead, leading `!` emphasizes bang intent, and recent/frequent use adjusts ordering. Selection applies a provider pill with no remaining completion rows; removing a suggested bang does not insert an untyped trigger. Both architecture builds and focused regressions pass; Intel runtime uses Rosetta. Published releases retain their frozen inputs.

The owner-accepted [Helium services footer and update controls](features/services-update-controls.md) are included in future builds through signed platform input `inputs/services-update-controls-1/macos`. Browser updates appear last on Privacy and security; the independent Helium update control and changelog collapse with disabled services. Setup enables service updates by default while preserving custom opt-outs. Both builds, setup/settings checks and browsing smoke pass (Intel under Rosetta). Published releases retain their frozen inputs.

The owner-accepted [expanded Command-T commands](features/command-bar-actions.md) are included in future main builds through signed platform input `inputs/command-bar-actions-1/macos`. The catalogue has 53 command identities, including focused tab grouping, vertical controls and conditional media actions. Single `/`, Cmd-/ and Cmd-Shift-P expose commands-only search, with assigned shortcuts, native symbols and local usage ranking. Media commands prefer a playing active tab and otherwise follow the media toolbar across tabs in the profile. Both builds, focused regressions and UI/settings/browsing smoke checks pass (Intel under Rosetta). Published releases retain their frozen inputs.

Both architectures build on the local Apple silicon Mac. Intel runtime checks use Rosetta unless a report explicitly identifies physical hardware. The owner has Intel Macs on macOS 13.7.8 and 26.6.2 for manual checks; their availability is not acceptance of any particular binary. Publish after single-device acceptance and the technical gates pass; manual Intel results and per-release owner deferrals are not required.

## Hosting and automation

The public source repository also hosts releases and paired raw-GitHub stable feeds. The [Cloudflare website](website.md) links to fixed GitHub latest-asset URLs. Optional browser services use Helium's hosted service; Lune-hosted services are not deployed.

Use the existing self-hosted Mac runner with no added CI spend. Manual browser builds, setup checks and website deployment are guarded workflows. Scheduled browser builds and unattended publication are not enabled. Credentials stay in Keychain; generated sources, caches and signed artifacts stay in ignored workspaces.

## Known open product issues

The Make default browser sidebar item can be absent on the reported macOS 13 install; Settings > Default browser remains available. Native resize cursors can flicker while Lune is active; resizing remains functional. Do not claim either fixed without new evidence. Other feature reports and open GitHub issues contain their scoped limitations.
