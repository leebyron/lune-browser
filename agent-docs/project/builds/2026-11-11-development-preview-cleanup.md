# Development preview cleanup — November 11, 2026

The owner requested cleanup of temporary build artifacts and made issue closure, temporary-build shutdown and disposable-artifact deletion part of the commit completion process. The [shared runbook](../committing.md) is linked from AGENTS and the current project/build/release/website/services guidance.

## Completed cleanup

The accepted address-bar bang preview was stopped through its task-owned fixture shutdown path. Its ChromeDriver session, local catalogue server and browser exited before deletion. No temporary preview app processes remained. The daily-use `/Applications/Lune.app` remained running.

Removed 22 inventoried temporary preview/probe/app-cache copies:

- `.work/search-suggestions/Lune Suggestions Test.app`
- `.work/search-suggestions/cached-Intel-Lune.app`
- `.work/search-suggestions/cached-Default-Lune.app`
- `.work/search-suggestions/Owner reviewed Suggestions Test.app`
- `.work/edge-frame/PopoverProbe.app`
- `.work/address-bangs/Lune Address Bangs Test.app`
- `.work/bang-suggestions/Lune Bangs Final.app`
- `.work/customize-icon/Lune Config Test.app`
- `.work/services-ui/Lune Services Preview 2.app`
- `.work/command-corners/Material Probe.app`
- `.work/issue-24/cached-Intel-Lune.app`
- `.work/issue-24/Lune Update Test.app`
- `.work/issue-24/cached-Default-Lune.app`
- `.work/icon-shape/Icon Verification.app`
- `.work/devtools-header/Lune DevTools Hover Test.app`
- `.work/glass-appearance/Sidebar Glass.app`
- `.work/glass-appearance/Clear Sidebar.app`
- `.work/glass-appearance/Glass Backdrop.app`
- `.work/glass-appearance/Glass Inheritance.app`
- `.work/glass-appearance/Glass Tint.app`
- `.work/glass-appearance/Glass Comparison.app`
- `.work/glass-reveal-probe/Glass Reveal Test.app`

Also removed the completed address-bar task’s disposable test profile, pristine/edited quilt fixtures, patch cache, strict replay trees and platform clone (seven directories). The clone was clean, had no stashes or ignored files, and every local branch head remained reachable in published main or platform history. The exported quilt patch matched the published input byte-for-byte before deleting its temporary copy.

The reusable prepared Chromium tree, both incremental output trees, compiler/download caches, release artifacts and validation evidence were retained. Before/after inode, size and SHA-256 checks matched for both reusable architecture app executables and the installed daily-use executable. All inventoried deletion targets were verified absent. App sizes and APFS clone accounting are not a physical disk-recovery measurement.

## Validation and issue state

Address-bar bang support remains included through main commit `5295b1114b73044b5e753dce2956ed3b83d43ba7` and signed input `inputs/address-bar-bangs-2/macos` at `b060587ba6d6ab55a8949b705672f8d92463f389`. Both browser builds, both smoke checks, focused native/shared-model regressions and all 73 repository tests had passed before cleanup. Native owner acceptance was recorded before adoption.

No open Lune GitHub issue was specifically resolved by the address-bar bang task; no unrelated issue was closed. No browser release or website deployment was part of this cleanup.

The compact local audit is `.work/address-bangs/cleanup-receipt.json`; build, smoke, native/model, lock/provenance and lint logs remain beside it. Feature documentation now records that the preview and generated fixture trees were removed rather than describing them as open or currently available.
