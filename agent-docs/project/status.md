# Current project status

Updated November 11, 2026. This page summarizes operational state. Exact source and artifact identities live in the linked machine-readable records; dated feature reports retain their original validation scope.

## Release delivery

- **Published:** [26.1111.2](https://github.com/leebyron/lune-browser/releases/tag/v26.1111.2) is latest, with both stable feeds promoted in `6e4717c5df2f60731b5645fb6fafc3137806228f`. Earlier published releases remain available. Each release contains one DMG per architecture, paired appcasts, checksums and compact metadata. The unused, never-uploaded 26.1111.1 entry was removed at the owner's request.
- **Validation:** 26.1111.2 retains signed tag `v26.1111.2`, source commit `e0dcb1e96c6f6ec402f4195840b50f3ad82789b4`. Fresh zero-fuzz preparation, both builds, signing/notarization, browsing/persistence, canonical-feed/consent and installed-update/rejection checks pass. Single-device acceptance passes on the physical Apple silicon Mac; Intel runs under Rosetta. Public HTTPS installed updates from 26.1110.1 pass on both architectures, including relaunch, profile persistence and signature verification. Both public feeds and complete versioned/latest download hashes match the final artifacts; the live website uses these latest links. Native Intel testing remains optional follow-up.
- **Migration limit:** 26.1109.1/26.1109.2 binaries embed the former `lune-downloads` feed URL. No compatibility redirects are retained; manually installing a current release restores stock updating after that repository's deletion.
- **Evidence:** [26.1111.2 release and public readback](builds/2026-11-11-release-26.1111.2.md), [26.1110.1 build evidence](builds/2026-11-10-release-26.1110.1.md), [consolidation](builds/2026-11-10-release-consolidation.md).
- **Process:** future allocations require completed clean preparation, and routine update tests start from the latest actually published release. Notes use that same baseline and omit installation/test boilerplate. Unlocking restored the existing notarization profile without credential re-entry. The publisher launcher preserves configured Git signing and GitHub authentication separately from compilation.

## Inputs and validation

The [development lock](../../manifests/browser.lock.json) is authoritative for current component commits and permanent input tags. The [patch manifest](../../manifests/patches.json) records feature provenance, order and hashes. Frozen release records and their source tags are authoritative for each released or reserved version; later main-branch changes do not alter them.

Current Chromium is **158.0.8127.18**, with the reviewed ungoogled/Helium forward port; this is not a claim that 158 is the official macOS Stable channel. The November 11, 15:57 UTC promotion check observed Stable **157.0.8103.51**. A fresh lookup is required before each publication and promotion. Preserve the ungoogled base identity separately from the Chromium target.

26.1111.2 includes owner-accepted [search-engine suggestions](features/search-suggestions.md): address-bar and Command-T query/website suggestions, typed-search priority, Use defaults enabled, configurable onboarding opt-in, and the visible shared Search engine settings control. The feature entered the development lock through `inputs/search-suggestions-1/macos` and remains in the current platform input; both builds and onboarding paths pass, with Intel runtime under Rosetta. Earlier releases retain their frozen inputs.

The owner-accepted [Customize icon removal](features/trailing-toolbar-controls.md#customize-temporary-icon-removal) is included in 26.1111.2 through signed platform input `inputs/customize-icon-1/macos`. Opening Customize no longer adds a temporary config icon to the trailing strip; both architecture builds and live Apple silicon panel checks pass. Earlier releases retain their frozen inputs.

The owner-accepted [DevTools header hover fix](features/devtools-header-hover.md) is included in 26.1111.2 through signed platform input `inputs/devtools-header-hover-1/macos`. Side-docked DevTools no longer reveal or retain the hover header; page content and the visible tabs sidebar remain eligible. Earlier releases retain their frozen inputs.

The owner-accepted [Command-T bang suggestions](features/command-bar-bangs.md) are included in 26.1111.2 through signed platform input `inputs/command-bar-bangs-1/macos`. Installed bang services participate in typeahead, leading `!` emphasizes bang intent, and recent/frequent use adjusts ordering. Selection applies a provider pill with no remaining completion rows; removing a suggested bang does not insert an untyped trigger. Both architecture builds and focused regressions pass; Intel runtime uses Rosetta. Earlier releases retain their frozen inputs.

The owner-accepted [Helium services footer and update controls](features/services-update-controls.md) are included in 26.1111.2 through signed platform input `inputs/services-update-controls-1/macos`. Browser updates appear last on Privacy and security; the independent Helium update control and changelog collapse with disabled services. Setup enables service updates by default while preserving custom opt-outs. Both builds, setup/settings checks and browsing smoke pass (Intel under Rosetta). Earlier releases retain their frozen inputs.

The owner-accepted [expanded Command-T commands](features/command-bar-actions.md) are included in 26.1111.2 through signed platform input `inputs/command-bar-actions-1/macos`. The catalogue has 53 command identities, including focused tab grouping, vertical controls and conditional media actions. Single `/`, Cmd-/ and Cmd-Shift-P expose commands-only search, with assigned shortcuts, native symbols and local usage ranking. Media commands prefer a playing active tab and otherwise follow the media toolbar across tabs in the profile. Both builds, focused regressions and UI/settings/browsing smoke checks pass (Intel under Rosetta). Earlier releases retain their frozen inputs.

The development lock also includes [native address-bar bangs](features/address-bar-bangs.md), reusing Command-T matching, provider pills, scope editing and local usage. Both builds, focused native regressions and Apple silicon interaction checks pass. The owner accepted the preview on November 11, 2026 and requested inclusion in main builds. Published 26.1111.2 remains unchanged.

The development lock also selects [Downloads pinned by default](features/downloads.md#default-toolbar-visibility) through `inputs/downloads-default-1/macos`. Profiles without saved toolbar customizations show Downloads immediately, saved unpins retain precedence, and Reset to default restores it. Published releases retain their frozen inputs.

Both architectures build on the local Apple silicon Mac. Intel runtime checks use Rosetta unless a report explicitly identifies physical hardware. The owner has Intel Macs on macOS 13.7.8 and 26.6.2 for manual checks; their availability is not acceptance of any particular binary. Publish after single-device acceptance and the technical gates pass; manual Intel results and per-release owner deferrals are not required.

The owner-accepted [stable command-menu glass](features/command-menu-stable-glass.md) is selected for future main builds through `inputs/command-menu-glass-1/macos`. Cmd+T and Cmd+/ keep the existing neutral backing at every result-list size, preventing the transparent tone-switching transition. Both browser builds and native regressions pass (Intel fixtures under Rosetta). Published releases retain their frozen inputs.

The final [setup toolbar dropdown](features/onboarding.md#setup-toolbar-choices--november-11-2026) now offers only On hover and Always for future main builds through `inputs/onboarding-toolbar-options-1/macos`; the native right-click menu retains Always cover (experimental). Strict replay, frontend checks, production bundling and browser preview interactions pass; no full native rebuild is claimed for this change.

The [session-restore notice fix](features/session-restore-notice.md) is selected for future main builds through `inputs/session-restore-notice-1/macos`. The informational bar now requires saved browser tabs from the existing session read, independently of setup state. Both builds and real headed fresh/relaunch checks pass (Intel under Rosetta). Published 26.1111.2 remains unchanged.

The owner-accepted [automatic Older Tabs](features/older-tabs.md) feature is selected for future main builds through `inputs/older-tabs-1/macos`. Inactive tabs move after 1 day by default and close after 3 further inactive days; Keep and drag-out restore regular placement. Pinned/split protection, optional group aging, Never/Immediately behavior, native section/date styling and conditional Keep commands follow the accepted preview. Both builds and startup/settings/lifecycle checks pass, with Intel runtime under Rosetta. Published 26.1111.2 remains unchanged.

The development lock includes the [sidebar drag header fix](features/sidebar-drag-header-retention.md) through `inputs/sidebar-drag-header-1/macos`. Native window dragging preserves the header's existing presentation. Both builds, focused/smoke checks and the post-push setup check pass. The source input and main integration are published; owner-confirmed native gesture acceptance remains pending. Issue #29 stays open.

## Hosting and automation

The public source repository also hosts releases and paired raw-GitHub stable feeds. The [Cloudflare website](website.md) links to fixed GitHub latest-asset URLs. Optional browser services use Helium's hosted service; Lune-hosted services are not deployed.

Use the existing self-hosted Mac runner with no added CI spend. Manual browser builds, setup checks and website deployment are guarded workflows. Scheduled browser builds and unattended publication are not enabled. Credentials stay in Keychain; generated sources, caches and signed artifacts stay in ignored workspaces.

## Completing validated changes

Follow the [commit and completion process](committing.md): close specific fully resolved issues, quit temporary builds and remove disposable artifacts after recording validation evidence. The November 11 [preview cleanup](builds/2026-11-11-development-preview-cleanup.md) removed 22 temporary apps and the completed address-bar fixtures while retaining reusable build inputs and release evidence.

## Known open product issues

The Make default browser sidebar item can be absent on the reported macOS 13 install; Settings > Default browser remains available. Native resize cursors can flicker while Lune is active; resizing remains functional. Do not claim either fixed without new evidence. Other feature reports and open GitHub issues contain their scoped limitations.
