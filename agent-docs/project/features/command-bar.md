# Native glass Command-T palette

Development prototype requested November 6, 2026. The owner requested native
glass, prominent navigation/search actions, and Helium bangs. The owner also
explicitly rejected explanatory UI such as “Esc to exit”; the provider name appears as an inline pill at the start of the input.

## Behavior

On macOS 26+, the palette uses AppKit `NSGlassEffectView` with a native
`NSTextField` and native result buttons. Earlier macOS versions use
`NSVisualEffectView` with the popover material. Native semantic text and selection
colors follow the profile's Light/Dark choice, or the OS in System mode. Favicons
keep their source artwork. The material has a 20 pt corner radius; results use
52 pt rows. The panel shows at most five results at once, with a native scroll
view for the remaining results. Up/Down scrolls the selected row into view,
including wraparound; changing the result list resets the scroll position.
Other platforms retain their existing Views implementation.

URL-looking input uses Chromium's omnibox classification, including local hosts,
IP addresses and internal browser pages. The direct URL action is first, even
when an existing tab matches. For other text, the direct default-engine search
is first when it is the only result and otherwise no lower than second. Promotion
happens before the nine-row cap, so matching tabs/history cannot remove that
action. Existing new-tab-page reuse is preserved.

Helium's `TemplateURLService` stores bangs with their leading `!`; the palette
now preserves that prefix and uses the installed catalogue, search templates,
active-engine rules and user keyword precedence. Partial bang triggers offer
completion. A recognized keyword followed by Space enters the provider scope;
Enter runs its search, and Tab can activate a scope hint. Escape leaves a scope,
then dismisses the palette. Backspace at the start of the query converts the
provider pill back into its original editable bang text, preserving the query
and placing the caret immediately after the trigger. Text selection and IME composition
retain normal deletion behavior. Search
terms that happen to start with the active keyword are kept verbatim. Pasted
multiword queries with trailing whitespace are not discarded by scope entry.
Catalogue and engine changes refresh the visible results. Reopening always
populates the newly created view, including when its query matches the previous
invocation.

The scoped input has no placeholder: the installed Helium catalogue and
`TemplateURL` model have no registered placeholder field. No placeholder is
generated from the provider name. Leaving the scope restores the ordinary
search/address placeholder.

The implementation adds no separate bang fetcher or new service preference.
Unknown/disabled bangs remain ordinary query text outside a scope.

## Inputs and validation

Platform input: `inputs/command-bar-3/macos`, commit
`5e18e95fed03fbe6907bc71debcf7c3caff0cb82`.
The source input is retained by an immutable Git tag. No browser release has
been published for this feature.
The quilt patch is `patches/helium/ui/native-glass-command-bar.patch`, developed
in the prepared Chromium tree, refreshed, and unmerged into an isolated platform
clone at `.work/command-bar/platform` on `command-bar-glass`. It depends on the
existing Xelium command palette and current native floating-chrome inputs.

Validation evidence is in `.work/command-bar/`:

- `model-test.json`: ten focused C++ regression cases execute the production
  ranking and keyword resolver functions, including 30 matching tabs and distinct
  bang/plain keywords. Service/URL types are minimal test doubles; this does not
  replace a complete Chromium unit-test suite.
- `replay.json`: strict zero-fuzz replay reproduces all eight changed source files.
- `gn-check.log`: command-palette header dependency check passes.
- `test-backspace.py`: production handler restores empty and nonempty bang
  queries, retains Unicode text, and positions the caret after the trigger.
- `token-layout-test.json`: native pill/input layout, long provider names,
  five-row viewport, and scrolling first/last results fully into view pass.
- `repository-tests.log`: all 44 repository tests pass.
- `component-checks.log`: locked platform/core patch and translation checks pass.
- Native Apple silicon inspection verifies native glass and text input, search
  second among 12 matching tabs, direct URL first beside a matching tab,
  repeated opening, and typed `!w cats` resolving through a locally served
  Helium-format catalogue to a new tab at `/wiki?q=cats`.
  Final native inspection verifies the five-row viewport, Down selecting the
  seventh result while scrolling it fully into view, the empty scoped
  placeholder, and Backspace restoring the pill plus `cats` to plain `!w cats`.
- `build-arm64.log` and `build-x86_64.log`: both final builds pass.
- `smoke-arm64.json` and `smoke-intel.json`: final page/JavaScript, profile
  persistence, UI default, and settings checks pass on both architectures
  (Intel runs under Rosetta on the Apple silicon host).

The isolated native test app uses a different development bundle ID and a
throwaway profile so it can be distinguished from the owner's other Lune
previews. Its local catalogue tests the real loader/resolver without depending
on a live remote service. It is not a published browser artifact.

Native Intel hardware, pre-macOS-26 fallback, Reduce Transparency, VoiceOver,
IME composition, fullscreen, and broad pointer/keyboard acceptance remain open.
No signed release, update feed, deployment, or release acceptance is implied.

## Catalogue-wide suggestions candidate

The November 10 [bang suggestions candidate](command-bar-bangs.md) adds provider/trigger matching on ordinary text, explicit bang priority, personal frequency/recency, and immediate scope application on selection. Its record distinguishes the candidate from the current development lock and frozen releases.
