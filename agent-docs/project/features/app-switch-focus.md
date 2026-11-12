# Native focus across app switches

The owner accepted the Apple silicon preview on November 12, 2026 and requested commit/push and inclusion in future builds. Signed input `inputs/app-switch-focus-7/macos` selects `e29310e346235dce9ece48c7e283510a870ca2f6`. Published releases retain their frozen inputs.

## Behavior

Cmd-T retains its query, selection and bang scope while Lune loses application focus. Returning restores the native editor after the browser-to-popup key-window handoff. Escape and outside-glass clicks dismiss independently of another widget activation change or an initial interaction with the input; Escape retains the existing provider-scope cancellation behavior.

The background click that reactivates Lune preserves Cmd-T, matching the address bar. The next background click dismisses. Native event timestamps distinguish a click generated before activation even when delivered afterward. Returning by Cmd-Tab still permits immediate Escape or background dismissal, without a grace period or dependence on repaired editor focus. The owner confirmed both sequences.

Address editing and the complete header toolbar persist across app deactivation. The system focus-ring mask appears only while Lune is active, the browser is key, and the editor owns first response. Opening Cmd-T ends address editing. Cmd-L while Cmd-T is open closes the popup before activating the owning browser and focusing its address field.

## Implementation and source

The reusable patch is `patches/helium/ui/native-editor-focus-lifecycle.patch`. A shared `HeliumNativeTextField` captures selection before app deactivation and restores it after Chromium Views completes activation. Popup restoration observes both the parent becoming key and the popup's subsequent key notification, without stealing another window or dialog's focus. Explicit dismissal cancels pending restoration; weak callbacks and teardown remove pending ownership and native event-monitor references.

Signed commits `c1b4b5f02f67386cdb793432e9e5245cd02cbb31` and `e29310e346235dce9ece48c7e283510a870ca2f6` descend from accepted word-navigation input `f90cd9d3c45a540b813c8d4d215f4c73159cede5`. Five iterative focus revisions were consolidated through quilt; the second commit adds activation-click preservation. All accepted toolbar, extension, session, ranking and word-navigation inputs remain in the ancestry. The word adapter bytes and cell/delegate wiring are preserved. An initially proposed address outside-click monitor was fully reverted after the owner clarified that existing address behavior was correct; the final address source is byte-identical to that reviewed revision.

## Validation and completion

The patch replays against retained current-input preimages with zero fuzz and zero offsets, reproducing all five changed source files. This is focused replay rather than a fresh full Chromium preparation. The Helium merge/unmerge roundtrip leaves the exported component unchanged. Patch/translation lint, signed input/commit verification and lock ancestry/tag/tree/gitlink checks pass.

`scripts/check-native-focus-retention.py SOURCE --arch ARCH` compiles the production helper and extracted production address, activation and native-monitor handlers with real AppKit field editors. Both architectures pass repeated selection restoration, parent-to-popup activation timing, inactive-window isolation, header/ring behavior, address-to-popup transfer, Cmd-L ordering, immediate Escape/outside-click handling, scoped cancellation and callback destruction. Left/right activation clicks are tested both before and after activation notification; the next click dismisses without a native editor. Negative controls reject missing activation protection and a guard based only on the app's active state, as well as the preceding ring/ownership/Cmd-L regressions.

Both final browser/ChromeDriver/installer builds and browsing/profile-persistence smoke checks pass. Intel smoke used a task-only 180-second session-creation allowance with the original 60-second page-request limits and unchanged assertions, after one session-start timeout and one first-navigation timeout. Those failures remain in the evidence; their cause was not established. The preceding combined builds also pass packaged UI/settings checks, all 117 production word-navigation cases per architecture, eight GN dependency checks and all 73 tooling tests; those inputs are unchanged by the final activation-click refinement. Intel execution uses Rosetta on Apple silicon. Physical Intel hardware, macOS 13 and broad IME/accessibility acceptance remain unverified.

The identified native preview's framework LC_UUID matches the final arm64 output. CUA checks confirm active-window dismissal and shortcut handoff; it did not establish actual app deactivation in this session. The owner's natural app-switch gestures provide that acceptance. The [validation record](../builds/2026-11-12-native-app-switch-focus.json) retains exact inputs, preview identity, checks and limitations. Detailed logs and reusable sources/build caches remain under `.work/focus-retention/`. No specific GitHub issue was supplied.

The accepted review app and isolated profile have been quit and removed, along with generated replay/negative fixtures and superseded output snapshots. Prepared sources, current build outputs, compiler caches, configuration/quilt provenance and concise evidence are retained.
