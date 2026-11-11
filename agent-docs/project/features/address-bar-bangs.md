# Native address-bar bangs

Implemented November 11, 2026. The development lock selects platform input `inputs/address-bar-bangs-2/macos` (`b060587ba6d6ab55a8949b705672f8d92463f389`). The owner accepted the live Apple silicon preview on November 11, 2026 and requested inclusion in main builds. The isolated preview was quit and removed after acceptance under the [completion process](../committing.md). Published releases retain their frozen inputs.

## Behavior

The floating address bar reuses Command-T's installed-bang model, including provider/trigger matching, typo tolerance, alias deduplication, local frequency/recency ordering and consent-controlled engine eligibility. It adds no catalogue fetcher. Plain text retains Chromium autocomplete priority, with a matching service after ordinary results; a leading `!` places bang completions first. The existing address dropdown keeps its six-row limit and reserves a row for a matching service on plain text.

Pointer, Enter or Tab activation applies the same native provider pill used by Command-T and its completion rows. Explicit input such as `!wik Cats and Dogs` retains its terms; descriptive input such as `github` becomes an empty scoped input. Space after an exact recognized trigger applies scope directly. Marked-text composition is excluded from automatic Space entry.

Scoped input shows the provider pill and `Search <provider>` placeholder with no result rows. It stops Chromium autocomplete and starts no suggestion work. Enter submits directly through the shared search-template resolver; empty or unavailable-provider submissions keep editing open. Ordinary Enter navigates the current tab; Cmd-Enter opens a foreground tab. Only submitted searches update the same local, unsynced usage dictionary as Command-T; the shared recorder excludes Incognito writes.

Escape first leaves scope while retaining query terms; another Escape ends address editing. Backspace at the query start restores the trigger only for directly typed scope entry. Completion-applied scopes clear without inserting an untyped trigger, retaining any query terms and the caret at their start. Selected text and IME composition retain normal deletion. Refocusing with Cmd-L restores normal URL editing. Search-engine/catalogue changes refresh the address results, and activation revalidates the provider.

Each edit resets selection to the highest ranked row. Deliberate keyboard selection follows the same result identity through asynchronous autocomplete updates. Existing address field, navigation controls, current-tab disposition and regular autocomplete providers retain their behavior outside bang scope.

## Implementation and evidence

The reusable platform quilt patch is `patches/helium/ui/address-bar-bangs.patch`. It changes `browser_frame_view_mac.mm` and depends on the existing shared Command-T model and native scope/result renderer. No search matching or usage algorithm is duplicated.

Topic commit `e3161f646192994f5fefa037510df467a22f1e09` descends from platform input `009caf230874153962f9965367ab79e789c8ed36`. The signed integration commit has parents `7e40287873ebf0e5bc465c64960485f76391cd6a` (the current accepted command-menu glass input) and the complete address-bar topic. It appends the address patch after the unchanged current series; the core gitlink is unchanged.

Retained validation logs and JSON reports are under `.work/address-bangs/`. Temporary source/replay fixtures, the platform clone, preview app and disposable test profile were removed after acceptance; see the [cleanup record](../builds/2026-11-11-development-preview-cleanup.md). The entries below describe the completed validation:

- `baseline/` reconstructed the locked prepared frame from its pristine quilt backup using strict patch replay and verified byte parity before development. `quilt-src/` was the isolated source fixture; `quilt-patches/` held quilt's refreshed patch. Helium's merge/unmerge tool exported it into the platform clone; the patch and full source history are retained in the published input.
- `strict-replay.json` and `strict-replay.log` establish zero-fuzz replay and parity with the compiled frame. `composed-input.json` records both parent identities and the integration tree.
- `build-arm64.log` and `build-x86_64.log` pass complete incremental browser, ChromeDriver and installer targets against the existing prepared development tree. These are not fresh full Chromium preparations.
- `strict-stack.json` proves the composed input strictly reproduces all six address/shared model/rendering source files, including the accepted command-menu glass. `lock-validation.log` verifies locked ancestry, signed input identity, trees, patch order/hashes and the core gitlink. All 73 repository tests pass (`repository-tests.log`).
- `gn-check.log` passes the frame target's header dependency check; `lint.log` passes inherited platform patch checks.
- `scripts/check-address-bangs.py` compiles production native scope/layout, query-change and keyboard methods with AppKit and minimal browser/engine doubles. Both architectures pass Unicode query retention, typed/completed Backspace and caret restoration, selection deletion, Escape, narrow layout, stale-provider rejection, Tab/Enter dispatch, exact-Space scope entry, autocomplete cancellation and no suggestion starts while scoped, and unknown-trigger fallback. Intel runs under Rosetta.
- `scripts/check-command-bangs.py` passes on both architectures, covering the shared catalogue matching, ranking, usage, eligibility and stale-entry behavior.
- `native-checks.json` records live Apple silicon interaction: typed `!w ` entry, empty scoped Enter, rowless scope, current-tab search, `!wik Cats and Dogs` completion with retained terms, completion Backspace preserving terms, plain `github` search/history priority, pointer-applied GitHub scope, empty completion removal, typed-trigger restoration and Cmd-Enter opening a new foreground tab. Search destinations were verified through a loopback-only catalogue fixture and actual loaded page URLs.
- `smoke-arm64.json` and `smoke-x86_64.json` record isolated page JavaScript, profile persistence, defaults and settings checks. Intel runtime uses Rosetta on the Apple silicon host.

Native Intel hardware, macOS 13 and broad accessibility/IME acceptance remain unverified. This is a development implementation; it does not publish a browser release.
