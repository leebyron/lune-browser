# Selected address-bar suggestions

Issue: [#12](https://github.com/leebyron/lune-browser/issues/12).

## Behavior

The selected native address-bar suggestion has a rounded background, using
`selectedContentBackgroundColor` at 25% opacity, a 10 pt corner radius, and a
1 pt vertical inset. The title uses semantic label color in every row.

At the owner's request, both address suggestions and Command-T use the same
`HeliumNativeResultRow` button and shared geometry constants. The renderer lives
in `chrome/browser/ui/helium/native_result_row_mac.{h,mm}` with a small macOS-only
GN target depended on by both callers. The address dropdown adopts Command-T's
52 pt rows, 8 pt outer insets, 16 pt semantic icons, 13 pt primary text, and 11 pt
secondary text. URL titles appear above their address; searches retain their
query as primary text. Command-T retains its optional action label and favicon
updates. Untagged rows use the available text width; narrow rows prioritize text.

The shared button draws selection, icons, and text and invalidates when selection
or effective appearance changes. Colors resolve at draw time; no layer color is
cached. Callers retain result sources, ranking, count limits, activation, index
tags, and keyboard handling. Hover selection remains enabled only for Command-T;
address rows do not install tracking areas. Both keep focus in their editor.
The separate popover material/corner investigation remains in issue #13.

## Provenance

Developed in the prepared Chromium 158 tree with quilt and unmerged into the
macOS platform as `helium/ui/address-suggestion-selection.patch` followed by
`helium/ui/shared-native-result-rows.patch`. The first signed platform commit is
`3379baa00fd622288991b641815762f55b78878a`, based on the accepted
header-scroll candidate `d0c49b0a`. The shared-renderer refinement is signed
commit `f0e2df52f03072644fca10e66cd6cf429fcbaa1a`, the head of
`topic/address-suggestion-selection`.
This candidate does not update the development lock or published binaries.

## Validation

Strict zero-fuzz replay of 79 relevant patches reproduces all six changed source
and build files from the canonical core/platform series. Platform patch lint passes.

The native fixture compiles and renders the production button class on arm64
and x86_64 under Rosetta. It checks selected/cleared pixels, transparent rounded
corners, Light/Dark/high-contrast appearance invalidation, narrow/wide sizing,
truncated primary/secondary text, autoresizing, target/action/index dispatch,
editor focus policy, and optional Command-T-only hover tracking.

```sh
python3 scripts/check-native-address-suggestions.py .work/chromium-158/macos/build/src --arch arm64
python3 scripts/check-native-address-suggestions.py .work/chromium-158/macos/build/src --arch x86_64
```

Both browser architecture builds pass. Live arm64 inspection confirms:

- Matching native row styling in the address dropdown and Command-T.
- Exactly one initial and keyboard-selected highlight, including Up/Down wrapping.
- Correct reset when typing replaces five results with one, and no rows/fill
  after clearing the query.
- Readable primary/secondary labels at 760 pt and 1354 pt window widths.
- Light, Dark, and Device profile appearances, including switching appearance
  and reopening the dropdown.
- Suggestion clicks, Return navigation, Command-Return opening a second tab,
  Escape dismissal, and focus-loss dismissal.
- Command-T keyboard selection scrolling beyond its five visible rows.

The first preview mistakenly enabled `zen_mode_top_chrome_pinned`, which disables
the floating address bar in this layout. The isolated profile was corrected and
restarted before these checks. The identified preview is **Lune Suggestions Test**
(`computer.lune.browser.suggestionstest`), with test pages served only on loopback.

Browser UI/settings/persistence smoke checks pass on arm64 and Intel under
Rosetta. Native Intel hardware and owner visual acceptance remain unverified. The fixture does not change the
user's macOS accent setting or establish live accent-change acceptance.

Local build, replay, native-check, and preview evidence is under
`.work/address-suggestions/`.
