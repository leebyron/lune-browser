# Missing default-browser sidebar action after installation

Status: unresolved on the reported macOS 13 installation; investigation updated November 10, 2026. Local first-launch and acceptance/cooldown candidates exist but are not included in the published 26.1110.1 platform input. The older-macOS appearance fixes are separate and already adopted.

The owner reports that installed Lune 26.1109.1 is not the system default on
Intel macOS 13, but the sidebar has no “Make default browser” button. The owner
confirmed that a full quit and restart does not restore it. First-launch
suppression therefore cannot explain the whole report. This is separate from
the older-system corner and material issues.

The owner then checked `lune://settings/defaultBrowser`: it correctly reports
that Lune is not the default and offers Make default. This verifies the Settings
state and action availability on the affected installation, not successful
execution of the system-default change. It narrows the persistent missing row
to startup eligibility, sidebar prompt delivery or rendering; there is no
evidence of a general macOS 13 default-detection or API-availability failure.

The owner also explicitly requires the action on the first launch: do not
retain first-launch suppression as intended Lune behavior. Preserve explicit
dismissals and system policy, but do not require a restart after installation.

## What the release source establishes

Inspected platform `1cabd52145c9dc2ef1b3459c71b0133a81b6c4b4` and its
prepared Chromium source:

- `chrome/browser/ui/views/frame/sidebar_footer_view.cc` shows the default row
  only when `SetDefaultBrowserPrompt` receives an accept callback. It does not
  independently query default-browser state and has no macOS-version gate.
- `chrome/browser/ui/startup/default_browser_prompt/default_browser_infobar_manager.cc`
  supplies these callbacks to the vertical sidebar when its prompt is active.
- `chrome/browser/ui/startup/infobar_utils.cc` explicitly runs the default-browser
  prompt only when `is_first_run == IsFirstRun::kNo`. The first browser launch
  therefore does not request this sidebar row through that startup path.
- That caller also respects “Don't ask me again” and the
  `--no-default-browser-check` / `--no-first-run` switches. The prompt manager
  respects saved decline counts and cooldowns. Do not clear these preferences
  or bypass an intentional dismissal as part of a visibility fix.
- `default_browser_prompt.cc` requires `NOT_DEFAULT`, permission to set the
  default, and no version suppression. Managed policy can skip the check.
- `chrome/browser/shell_integration_mac.mm::GetDefaultBrowser` compares the
  running outer app's bundle identifier with the registered HTTP handler. No
  macOS 13-specific exclusion appears in this function.
- `chrome/browser/ui/webui/settings/settings_default_browser_handler.cc`
  queries state separately for Settings. `lune://settings/defaultBrowser`
  provides a useful diagnostic/action path without the sidebar startup gate.

## Saved preferences and attempted repair

The owner reports never dismissing this row. It remains absent after restart and New Tab. Settings correctly reports that Lune is not default and offers Make default. Local State is at `~/Library/Application Support/computer.lune.browser/Local State`, rather than `~/Library/Application Support/Lune/Local State`.

The owner's read-only check found both decline counters at 1, matching decline timestamps, and no permanent rejection. A later check found both counters at 2. This establishes saved cooldown state but cannot identify which action wrote it. The owner accepted the existing 21-day dismissal cooldown. A backed-up repair removed only the four cooldown fields while Lune was quit; reopening still did not show the row. Cooldown therefore does not fully explain the reported installation. Do not keep resetting preferences or treat this issue as fixed.

## Acceptance and setup source findings

The shared Settings handler calls `UpdatePrefsForDismissedPrompt` on Make default before macOS confirms success. Menu, infobar and sidebar acceptance paths also call that helper. An accepted-but-unsuccessful request can therefore increment counters whose names suggest dismissal. The original reported timestamp corresponds to November 9 at 15:46:47 Pacific; the saved data does not identify its entrypoint.

The inspected setup's Use defaults and Finish paths save preferences and open a new tab; they do not invoke the default-browser setter or record a decline. Setup retains an unused `askToBeDefault` wrapper. Merely reading default-browser status does not write decline counters. Do not describe ordinary setup completion as an implicit decline.

## Unpublished candidates and historical checks

The older compatibility worktree retains two default-browser candidates alongside the adopted appearance fixes:

- `b090690a`, `sidebar-default-browser-availability.patch`: run existing eligibility checks on first launch with vertical tabs. Preserve horizontal first-run policy, managed policy, exclusions, rejection and the 21-day cooldown.
- `00ae8d22`, `default-browser-acceptance-cooldown.patch`: route accepted attempts through a distinct helper. Leave macOS prompt preferences unchanged while native confirmation is asynchronous; retain explicit Close cooldowns, permanent rejection, successful-default reset and existing non-macOS policy. Do not erase saved declines that might be intentional.

These candidate changes are not in the published `9ceaaad8a2f71ece40aab464c6504ee1f356312f` platform's patch series. Do not mark them shipped or silently add them while cleaning documentation or release branches.

Recovered November 9 candidate notes report both architecture builds and smoke checks for the initial three-patch compatibility stack (two appearance patches plus first-launch eligibility), focused fallback/appearance fixtures and an in-memory preference-function fixture on both architectures. The final fourth-patch full rebuild was not recorded as complete. On the local macOS 26 Apple silicon host, historical disposable-profile checks reproduced released first-launch suppression, showed the candidate row, preserved explicit dismissal across restart and restored eligibility after a 22-day-old test timestamp. Intel execution used Rosetta. These checks did not change the system default or establish behavior on the affected macOS 13 installation.

The unfinished work and local helper remain under `.work/release-26.1109/delivery-policy`; preserve them until the investigation is completed. Integrating these notes does not adopt the candidate browser patches or claim a fix. Further diagnosis should trace live eligibility and sidebar delivery on the affected profile, then validate a bounded fix. Additional Intel hardware checks are optional compatibility follow-up under the current [single-device release policy](../releases.md#release-gates), not a publication gate.
