# Native address word navigation

Owner accepted the native Apple silicon preview for [issue #32](https://github.com/leebyron/lune-browser/issues/32) on November 12, 2026 and requested commit/push and inclusion in builds. Future main builds include signed input `inputs/native-word-navigation-2/macos` (`f90cd9d3c45a540b813c8d4d215f4c73159cede5`). Published releases retain their frozen inputs.

## Behavior and implementation

Both inputs use Chromium's existing ICU word iterator through `base::i18n::BreakIterator::BREAK_WORD`. Its hostname customization splits ASCII and full-width periods between letter components while retaining decimal-number boundaries. No second punctuation list or ICU ruleset is introduced.

`HeliumWordTextFieldCell` installs a scoped `NSTextStorage` implementation through the public `setUpFieldEditorAttributes:` hook, before typing starts. This uses AppKit's supported TextKit 1 compatibility mode. Installing storage on the first word command would leave earlier typing undo attached to the old storage; the native regression fixture checks that undo remains effective.

The shared adapter handles native visual Left/Right and logical Forward/Backward word commands, including all selection variants. AppKit still performs each action and owns its selection anchor and bidirectional traversal; the storage override supplies only `nextWordFromIndex:forward:` boundaries. The override is enabled only while that action runs. Other commands, word deletion, mouse selection, unrelated controls sharing the window's field editor, and marked-text composition retain native behavior.

The reusable platform patch is `patches/helium/ui/native-word-navigation.patch`. It adds `native_word_navigation_mac.{h,mm}` and a shared GN source set, then configures the cell and delegate in `helium_command_bar_view_mac.mm` and `browser_frame_view_mac.mm`. It is independent of the pending native focus and toolbar topics.

## Source and validation

Signed topic commit `e4ef36463128b2e76892c12c80d983ce31dec43c` contains the standalone feature. Signed composition `f90cd9d3c45a540b813c8d4d215f4c73159cede5` preserves that ancestry and appends the refreshed feature to input `3aa1b256f8b18b802b2d076a293a953417c9697d`. The six affected files were reconstructed through the selected parent stack with zero fuzz, then the new patch was refreshed and replayed with zero offsets. That standalone component excludes the then-pending native focus topic. The later [app-switch focus input](app-switch-focus.md) composes the accepted focus lifecycle after it.

The isolated prepared review tree is `.work/word-navigation/prepared-src`. To reuse the existing development build cache, the review composition also retains the initial pending focus-retention, setup-toolbar, toolbar-visibility and extension-popup patches. `preview-composition.json` lists the exact ordered patches and production file hashes; `preview-strict-replay.log` proves its focused adaptation applies with zero fuzz/offsets. The adapter header and implementation are byte-identical to the independently tested standalone patch. The adaptation only adds the same cell/delegate wiring to the preview's existing native focus field classes. It changes no shared canonical sources or other review apps.

- `strict-replay-initialized.json` verifies zero fuzz, zero offsets and byte parity for all six production files between the exported patch, focused source and the initial standalone build source. The final Helium merge/unmerge preserves the patch bytes; platform patch lint passes.
- `native-final-arm64.json` and `native-final-x86_64.json` record 117 checks against the production adapter and Chromium ICU data before composing the preview. Intel runs under Rosetta. Cases cover native key-event mappings, dotted URL components, numeric decimals, full-width periods, underscores, combining marks, emoji, logical/visual movement, reversed and mixed-direction selection, interleaved character selection, control isolation, native deletion, marked text and typing undo.
- `gn-checks-final.json` records dependency/header checks for the adapter, palette and frame on both architectures.
- `address-bangs-final.json` records both architecture passes for existing native provider scope, query retention, Backspace, Escape and Tab/Enter behavior. This fixture isolates word navigation; the production word adapter is covered by the dedicated fixture.

Run `scripts/check-native-word-navigation.py SOURCE --arch ARCH --report REPORT` on an isolated prepared tree with no active build in the selected output. It temporarily generates a small GN test graph and restores the normal graph without changing product source or GN arguments. `tests/native/word_navigation_mac.mm` is the native fixture.

Both incremental browser/ChromeDriver/installer builds and isolated browsing, persistence, packaged UI/default and Settings checks pass. The owner accepted the native preview; automated full-browser caret mutation checks were not completed before that acceptance. The standalone native fixture covers the actual AppKit movement and selection actions with production ICU. Native Intel hardware, macOS 13 and broad IME/accessibility acceptance remain unverified.

The committed [acceptance and validation record](../builds/2026-11-12-native-word-navigation.json) retains exact source, review-composition and artifact identities. Detailed logs remain under `.work/word-navigation/`. The accepted preview was quit and its app/profile and disposable source fixtures were removed after validation. Prepared browser sources, build outputs, compiler caches and concise replay evidence are retained.
