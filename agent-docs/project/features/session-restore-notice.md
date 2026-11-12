# Session-restore notice

## Removal — November 12, 2026

The owner requested removal of the informational “Continue where you left off” bar. Lune restores saved tabs quietly; the startup choice remains available in Settings. The startup call to `SessionRestoreInfobarController::MaybeShowInfoBar` and its two unused includes are removed from `chrome/browser/ui/startup/infobar_utils.cc`. The change does not alter session restoration, saved startup preferences, other notices, or the separate crash-recovery bubble and crash-report dialog.

The earlier saved-tab eligibility patch remains in the input history; its model no longer has a production startup caller. Published browser releases retain their frozen inputs.

Signed platform commit `810b4ea9b84d347e38ca38ace6a5800aad243075`, based on `af297bc814a9dba21e27433a9e1d3794844f2d6b`, adds `helium/ui/remove-session-restore-notice.patch`. Permanent input: `inputs/remove-session-restore-notice-2/macos`. The change was developed in the prepared Chromium tree with quilt, refreshed, and exported with Helium's merge/unmerge tooling. Replaying the complete locked patch order for the affected file reproduces its final bytes with zero fuzz and offsets.

Both incremental browser builds pass. Real headed launches, without automation or first-run suppression flags and with `SessionRestoreInfobar` explicitly enabled, record no informational notice for fresh, saved-session, or simulated unclean-exit profiles, with setup either complete or incomplete. Saved tabs restore on clean relaunch; the separate crash-recovery bubble appears after a simulated unclean exit. Additional startup-choice checks confirm that the default restores two saved tabs and an explicit New Tab choice does not. Apple silicon execution is native. Intel execution uses Rosetta; its headed matrix uses software rendering in a disposable ad-hoc signed copy whose framework matches the freshly built framework before signing. This does not establish native Intel or production-signed acceptance.

All 73 repository tests and patch lint pass. The broader GN include audit reports two existing dependency errors in the unchanged `startup_browser_creator_impl.cc`, identically on both architectures and the released 26.1111.3 source baseline; the changed file reports no include errors. The updated notice regression rejects the signed 26.1111.3 baseline because a saved-session relaunch records one notice. The [completion record](../builds/2026-11-12-remove-session-restore-notice.json) retains exact inputs, checks, fixture limitations and the initial packaging/runtime attempts. Shared incremental outputs contain unrelated pending focus-retention work; independent affected-file replay binds this removal to the selected input. No specific GitHub issue tracks this request.

Task-owned browser/driver processes have exited. Disposable profiles, the Intel test app, baseline links and replay tree are removed after retaining the validation reports. Current shared build outputs, caches and the prior protected Intel bundle are retained.

## Earlier eligibility fix — November 11, 2026

Requested November 11, 2026: show Chromium's informational session-restore bar only when there were browser tabs to restore, independently of whether setup is complete.

### Cause and behavior

Lune defaults macOS profiles to Continue where you left off. Chromium's session-restore notice previously checked that default and its display limit without checking for a saved session. A fresh profile could therefore display “Lune restores your tabs every time you restart” over the setup page.

The fix reuses the existing local session read, before restored windows are created. It records a profile-owned, in-memory marker when the saved browser session contains a normal or popup window with a tab containing navigation history. The notice requires that marker in addition to its existing eligibility checks. Before a session is read, and after an empty browser-session read, the marker is absent. App-session reads and foreign sessions do not set it; an app read does not erase the browser-session result. Another profile cannot inherit the marker.

No setup preference or setup URL participates in the check. A fresh profile stays quiet with setup either complete or incomplete; a saved browser session remains eligible in either state. The startup preference, actual restoration, explicit startup selections, notice display limit, and separate crash-recovery prompts retain their existing behavior. This suppresses the misleading fresh-profile notice; it does not change the layout of notices that are eligible to appear.

### Source and validation

Signed platform commit `651e911573be598a6cf348467169b4ce25ea6d36`, based on locked platform `bc6e31500baab1551d1ffcee4c3bbc44510b7f25`, adds `helium/ui/session-restore-notice-with-tabs.patch`. Permanent input: `inputs/session-restore-notice-1/macos`. The patch was developed in the shared prepared Chromium tree with quilt, refreshed, and exported through Helium's merge/unmerge tooling. Replaying the locked patches from retained prepared preimages reproduces all five changed files exactly, with zero fuzz and zero offsets. Frozen release sources are untouched.

Both complete browser builds pass. Header dependency checks and platform patch lint pass. Added Chromium model tests cover no prior read, empty sessions, tabs without navigation history, profile isolation, later empty-session resets, app-session isolation, popup tabs, and the existing post-crash exclusion. Those test sources compile for arm64 and x86_64; the complete Chromium unit-test binary was not linked or executed.

All 73 repository tests, locked ancestry/tag/tree/gitlink/hash checks, changed-document link checks and whitespace checks pass. The implementation commit and input tag signatures verify. A fresh recursive GitHub checkout resolves the exact platform and core commits and matches the published patch bytes.

`scripts/check-session-restore-notice.py` launches the real headed browser in disposable profiles, then attaches ChromeDriver. It deliberately omits the automation and first-run suppression flags that would bypass the notice. It checks persisted notice counts, saved-tab restoration, orderly exit, and setup-tab presence.

| Profile and launch | Setup incomplete | Setup complete |
| --- | --- | --- |
| Fresh profile, no saved tabs | No notice | No notice |
| Relaunch with a saved browser tab | Tab restored; notice shown | Tab restored; notice shown |

The complete headed matrix passes on arm64 and on x86_64 under Rosetta. The retained published 26.1111.2 build fails the fresh-profile regression as expected: it records one notice over setup without a saved tab. This establishes that the fixture detects the reported bug. Native Intel hardware was not tested.

Task-owned browsers, ChromeDriver processes and loopback servers exit at the end of each fixture. Disposable test profiles and replay trees are removed after retaining the build results, strict-replay report, model-test compilation results and headed matrix reports. The shared prepared Chromium source and incremental build outputs remain available.

The source input is selected for future main builds. Published 26.1111.2 and its binaries/feeds are unchanged. No specific GitHub issue is associated with this request.
