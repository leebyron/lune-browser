# Toolbar retention for extension popups

Requested and accepted November 12, 2026. The owner confirmed: “Extension bug seems fixed. We can commit that.” Signed component commit `1aecd0bcfe68e2e74140fa84e812850981d57c61` keeps this fix separate from the toolbar hover-mode work. The development lock selects signed input `inputs/extension-popup-retention-1/macos` for future main builds.

## Behavior and cause

Extension buttons move into the floating toolbar's separate native child widget. They are outside the top-container ancestry checked by the generic bubble scan, so an open extension action popup could lose the toolbar supporting its icon.

An extension popup now explicitly acquires the existing window-local top-toolbar reveal hold before showing. This reveals a hidden toolbar for a programmatic open and keeps it mounted as focus or the pointer enters the popup. Hiding or destroying the popup releases the hold; the scoped weak release also covers cancellation and browser teardown. Independent holds remain counted separately. No password-manager-specific logic, persistent pinning or new timer is introduced. Rectangle anchors are supported without relying on an anchor View.

The independent quilt patch is `helium/ui/extension-popup-toolbar-retention.patch`. Its input base `7ccbf6d4c324dc8f62e81cbf2fc6b52467a7d931` preserves the selected-search-engine bang preference adopted during this task. The [toolbar hover modes](toolbar-visibility.md) are a separate change.

## Validation

The patch was developed in the prepared-source quilt workflow, refreshed and exported through the platform unmerge tool. Exact retained-preimage replay passes with zero fuzz and zero offsets. The extension-popup GN dependencies pass for both architectures. Both final browser builds and browsing checks pass; Intel executes under Rosetta. The final validated candidate also includes the independently committed hover modes.

An inert local extension opens a real action popup in the isolated native Apple silicon review app. Read-only inspection records `HeliumFloatingAddressBar` as presented, unhidden and not editing while the popup is open. The debugger detached successfully. The owner then confirmed the reported bug is fixed. This verifies shared extension-popup infrastructure; no personal password-manager account or vault was accessed. Native Intel hardware and a complete extension compatibility matrix were not tested.

No specific GitHub issue tracks this request. Published browser releases and frozen inputs remain unchanged.

The [validation record](../builds/2026-11-12-extension-popup-retention.json) retains source identities, paired-build hashes and the test-artifact diagnosis. Earlier test copies silently updated to published 26.1111.3 through Sparkle; final Settings tests disable update access only in their disposable profile and use a loopback feed. The final Intel package matches the compiled main/framework inputs and stays unchanged through Settings, browsing and setup checks. Production updater policy is unchanged.
