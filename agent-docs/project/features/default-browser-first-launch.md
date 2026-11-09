# Missing default-browser sidebar action after installation

Status: source investigation, 2026-11-09. No implementation change or runtime
reproduction on macOS 13 yet.

The owner reports that installed Lune 26.1109.1 is not the system default on
Intel macOS 13, but the sidebar has no “Make default browser” button. The owner
confirmed that a full quit and restart does not restore it. First-launch
suppression therefore cannot explain the whole report. This is separate from
the older-system corner and material issues.

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

## Next verification

The quit/reopen check failed to restore the row. A follow-up asks what
`lune://settings/defaultBrowser` reports. Compare that reported default state
and then inspect only relevant prompt eligibility/preferences and
footer visibility. An absent callback and a present-but-clipped row need different
fixes. Do not infer that default detection is wrong solely from the missing row.

Remove the first-run gap as requested, potentially by refreshing existing prompt
eligibility when setup completes, while retaining explicit dismissals, normal
policy checks and the system confirmation flow. Diagnose the persistent missing
row separately; removing the startup gate alone is not a demonstrated fix for
the owner report. This is a proposed direction, not implemented behavior.
Verify first launch, subsequent launch, default and
non-default states, dismissal and pinned/popover sidebars before acceptance.
