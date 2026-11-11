# Expanded Command-T commands

Development candidate for [issue #17](https://github.com/leebyron/lune-browser/issues/17). Includes the requested stateful tab/layout controls and a relevant SF Symbol for every command. Owner visual/runtime acceptance is pending. The development lock and published releases have not adopted this candidate.

## Discovery and interaction

Cmd-/ and Cmd-Shift-P open the same palette directly in commands-only mode with an empty input and the placeholder **Search commands**. Escape closes that palette immediately, including after a query is entered. Both shortcuts defer to the focused webpage or DevTools and open Lune command search only if the renderer leaves the event unhandled. The existing Cmd-T/Cmd-L behavior is retained.

Ordinary input continues to mix commands with navigation/search results. Typed URL/search priority, the nine-result mixed cap, engine/tab scopes and accepted bang behavior are preserved. Leading `/` outside an applied scope opens commands-only search; bare `/` lists the available catalogue in its curated order, using the existing five-row scrolling viewport without the mixed-list cap. `/restore`, `/undo close tab` and `/reopen` find Reopen Closed Tab; `/hard refresh` finds Reload Without Cache. Escape removes the command prefix and returns to mixed results; another Escape closes the palette. An applied engine scope treats `/` as search text. A leading `//` stays in ordinary navigation/search handling, and `>` has no special command behavior.

Recent and frequent invocations promote commands within the same text-match band; an exact match still beats a partial match. Bare `/` puts personal favorites first, falling back to curated order. Usage is stored in the local unsynced `helium.command_bar.command_usage` dictionary under stable registry keys, with saturated counts and last-use timestamps. Only accepted activations count, including opening a dialog even if it is later cancelled. Private windows read regular-profile ordering and never record usage. Queries and page URLs are not stored.

Unavailable commands are hidden. Availability and toggle labels refresh while open and are checked again on activation. A command selected explicitly by keyboard/pointer retains its identity across result updates; if it disappears, Enter has no selected action until a new query or selection. Each row uses the existing shared native result styling and its registry-provided SF Symbol. The right-hand text shows the first currently assigned keyboard shortcut when one exists, using BrowserShortcutService display text; otherwise it says Command. Customized and removed bindings are respected, and contextual Save/Copy/Inspect/sidebar wrapper shortcuts are shown only for the action they currently perform. Toggle symbols change with the resulting action.

Commands target the invoking window's active pane/tab. Activation captures a weak page identity and invocation token, leaves the input event stack, rechecks the target and visible state, closes the palette synchronously, then dispatches. This lets Find, Print, DevTools and dialogs take focus after dismissal, and lets Close Tab destroy its window safely. A replaced/closed target, reopened palette, stale toggle or newly disabled command cannot redirect execution. Repeated Enter/clicks queue only one command.

The registry uses Chromium command support/enablement and dispatch for existing handlers. Pin Tab and Mute Site use focused adapters with Chromium context-menu eligibility, deliberately affecting the active pane even when unrelated tabs are selected. Muting is site-level. Sidebar and toolbar pinning use the existing native view/state controllers. Narrow sidebar collapse is not offered.

## Complete catalogue

There are **42 command identities: 37 additions and five retained commands**. Toggle alternatives share one identity. Layout switching is not offered; Lune supports vertical layout. Sidebar positioning appears in vertical layout, and sidebar/toolbar pinning in Zen mode. Normal and private tabbed windows share the registry, subject to Chromium policy and page availability. App/DevTools-only windows do not expose this catalogue.

| Area | Added commands |
| --- | --- |
| Tabs and windows | Reopen Closed Tab; Duplicate Tab; Close Tab; New Window; New Private Window; Open File; Move Tab to New Window; New Split View |
| Browser UI | Show Bookmarks; Manage Extensions; Customize Lune; Customize Toolbar |
| Navigation | Go Back; Go Forward; Reload Page; Stop Loading |
| Page actions | Find in Page; Find Next; Find Previous; Bookmark This Page; Print Page; Save Page; Zoom In; Zoom Out; Actual Size |
| Developer tools | Toggle Developer Tools; Open Console; Inspect Element; View Page Source; Task Manager; Reload Without Cache |
| Stateful tabs | Pin / Unpin Tab; Mute / Unmute Site |
| Layout | Enter / Exit Fullscreen; Move Sidebar to Right / Left; Pin / Unpin Toolbar; Pin / Unpin Sidebar |

Retained commands: New Tab, Open Settings, Show History, Show Downloads and Copy Page URL. These now share registry metadata, native symbols and browser-command dispatch. New Tab uses the real New Tab command; Copy Page URL uses Chromium's standard URL-copy handler. New Split View adds a split pane using Chromium's existing split/new-tab flow. Print Page opens the existing print UI, including its PDF option. Customize Lune opens the existing appearance panel and uses its existing branded/localized title; Customize Toolbar opens that panel at its toolbar section.

Tab-group pickers, moving to an existing window, deeper DevTools frontend commands, DOM-derived page actions, translation/reading mode, media controls and profile-wide cache deletion remain outside this candidate.

## Source and validation

Reusable platform patch: `patches/helium/ui/command-bar-actions.patch`, developed with quilt in `.work/search-suggestions/platform/build/src`, then refined in isolated `.work/command-actions/quilt-src` while another chat used the shared build tree. The patch is unmerged into `.work/command-actions/platform` on `topic/command-bar-actions` at signed commit `0ced177b`, based on the accepted `inputs/command-bar-bangs-1/macos` input. Core gitlink is unchanged. New palette labels are GRIT messages with English source text; translations are follow-up work under the existing string-localization issue.

Evidence lives under `.work/command-actions/`. Focused registry tests compile the production registry and dispatch with small window/policy doubles for both architectures; these test palette decisions rather than proving Chromium's independent handler behavior. Existing bang and search-ranking/selection checks cover both architectures. The search-model harness now models deliberate selection explicitly and tests disappearing commands. Patch lint and exact zero-fuzz replay cover all 16 exported command files. A separate composition replay verifies seven active patches reproduce all 29 files affected by commands and the concurrent services candidate. The latter remains a separate patch with its own acceptance. This reuses the prepared baseline and does not claim a fresh full Chromium preparation. The native symbol audit resolves all 43 referenced symbols, including toggle alternatives, on the host OS; macOS 13 runtime remains separate.

Build and native runtime results will be recorded after completion. Physical Intel, macOS 13, broad accessibility/IME and exhaustive managed-policy acceptance require separate validation.
