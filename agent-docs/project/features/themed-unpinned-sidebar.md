# Themed unpinned sidebar and 216 px default width

Accepted implementation for [issue #21](https://github.com/leebyron/lune-browser/issues/21).
The owner accepted Test 6 background tones and Test 7 selection colors on
November 9, 2026, then authorized focused commits, pushing and main adoption.

## Behavior

- Detached sidebar glass takes `kColorToolbar` from the mounted sidebar's
  owning color provider as its theme source. Hue and saturation are retained;
  HSL lightness is multiplied by 1.05 in Light (clamped to 1) and .65 in Dark.
  The owner accepted the color saturation, then requested Light 5% lighter than
  the base theme tone and Dark slightly darker again. These tone adjustments
  apply only to unpinned glass.
- Glass tint strength remains 30% Light / 40% Dark. Mounted-overlay strength
  remains 80% / 55%. Header and Command-T tint policy is unchanged. The owner accepted Test 6 tone
  and strength values on November 9.
- System sidebar tint uses its native window-background palette. High-contrast
  glass stays untinted. Header and Command-T tint policy is unchanged.
- The mounted NSVisualEffectView includes its neutral backing and a normal color
  overlay. The detached NSGlassEffectView interprets tint through its glass
  effect. Matching input RGBA does not establish matching rendered appearance.
- Lune active-tab selection uses its stronger palette surface, #2A4C62 in Dark
  and #D6E1D2 in Light, for both active/inactive windows. This is lighter than
  the Dark sidebar base and darker than the Light base. It applies through the
  shared theme roles to mounted and detached rows; other palette surfaces and
  System/custom themes are unchanged. The owner accepted Test 7 selection colors on November 9.
- Detached sidebar selection and hover fills use the owning browser theme's
  existing tab color roles. Selected text uses the matching theme role.
  The actual native glass appearance selects the light/dark provider variant;
  the owning browser window supplies active/inactive state.
- Ordinary labels, disabled controls and focus indications retain AppKit colors.
  New Tab and footer hover fills share the sidebar hover role.
- System row colors remain native. High-contrast and forced-color rows retain
  native fallback; high-contrast glass is untinted.
- Theme changes invalidate the detached widget's colors even while hidden.
  No page sampling, probes, timers or header-dependent adaptation are added.
- Regular glass and Content aware backing policy remain intact. On older macOS,
  row theming applies but NSVisualEffectView does not receive the glass tint.
  Equivalent fallback material coloration is not claimed.
- Expanded-sidebar default and resize snap target are 216 logical pixels
  (AppKit points), up from 200. The 160–400 range and snap tolerance are unchanged.
  The profile preference registration now uses the same constant, removing a
  separate hard-coded 200 px default. Stored widths are preserved; this is not a profile migration.

## Source inputs and validation

Three signed, single-thesis platform commits follow
`inputs/continue-session-default-2/macos` (`bc7e8558`):

1. `46d24c60910c644423e68957840c54dd410d41cc` — theme detached glass and rows from the owning palette.
2. `a8e0b32c327f5ffb583ca1afb1609c505672f661` — use the shared 216 px sidebar default.
3. `d503fa7151b4c8fbead63f0c252677de524be96b` — give Lune selection directional light/dark contrast.

The branch is `topic/themed-sidebar-reviewed`; immutable input
`inputs/themed-sidebar-1/macos` retains the final commit. Main's development
lock selects it for both architectures. The core remains
`49bdc572bee38436250f9058351c8a328cd8c8ad`; inherited development features and
frozen release records are preserved.

- Developed with quilt in prepared Chromium source, refreshed and unmerged.
  Strict zero-fuzz replay from recorded prepared baselines reproduces all six
  changed files exactly.
- Independent archive-backed replay through all 94 relevant current core and
  platform patches passes without fuzz. Native-file line offsets reflect
  inherited changes; the accepted color helpers remain byte-identical.
- Exact composed native-material, frame, palette and tab-preference units
  compile for arm64 and x86_64 against current development headers and flags.
  Full browser and ChromeDriver builds pass for the accepted preview source on
  both architectures. A full rebuild of every concurrently integrated main
  feature is not claimed.
- Production native appearance/lifecycle and sidebar-role fixtures pass on both
  architectures (Intel under Rosetta): owning window, actual glass scheme,
  active/inactive roles, startup, System and accessibility fallbacks.
- Palette checks confirm selection brightness direction and selected-text
  contrast of 7.23:1 Dark / 7.63:1 Light. Native Light inspection confirms mounted
  #E7EDE3 and calibrated glass #F3F6F1 at .3 alpha, with a 216-point sidebar.
- Browser layout checks confirm fresh 216 px and saved 260 px widths on left and
  right, on both architectures. Earlier UI/settings/persistence smoke checks
  pass; the broad matrix was not repeated for each color-only refinement.
- The owner accepted the final identified arm64 preview. Native Intel hardware,
  older macOS visual parity and inactive material tint remain unverified. The
  earlier Intel staging denial was resolved by preserving the incomplete bundle
  and rebuilding into a fresh output path; the final Intel build passes.

[Machine-readable validation](../builds/2026-11-09-sidebar-validation.json)
records the source hashes and checks. Patch lint and lock validation pass.
This source integration does not publish a browser release.

```sh
python3 scripts/check-native-chrome-appearance.py SOURCE --arch arm64
python3 scripts/check-native-sidebar-theme.py SOURCE --arch arm64
python3 scripts/check-sidebar-default-width.py BUILD --report /tmp/sidebar-default.json
python3 scripts/check-sidebar-default-width.py BUILD --saved-width 260 --report /tmp/sidebar-saved.json
```

Repeat native fixtures with `--arch x86_64`. Run browser checks sequentially.

## Native selected-tab background — November 12, 2026

Native color scheme now uses the active tab's background for selected-but-not-active tabs, including hover. Both selected background roles alias the corresponding active background for active and inactive windows. Selected text already used the active foreground; inherited Chromium selected backgrounds could leave that text unreadable. The change is four aliases and a comment in the existing macOS Native color mixer. Its theme, app-controller and forced-color exclusions remain intact.

Signed platform input `inputs/native-tab-selection-1/macos` at `99ca9faf1ae2e4b511cd952728adaa70c165faae` is selected for future main builds. The focused reusable patch is `helium/ui/native-selected-tab-background.patch`; it follows the accepted address-cursor input and excludes the pending pinned-tab-groups topic. Published browser releases retain their frozen inputs. No specific GitHub issue tracks this request.

Production AppKit mixer checks pass for both architectures across light/dark, normal/high contrast, hovered/unhovered selection and active/inactive window roles, with Intel under Rosetta. Non-native/custom/app/forced-color exclusions pass, and the original source fails the same selection equality assertion. Complete affected-file reconstruction from the platform series matches the built mixer with zero fuzz or offsets. Patch lint and lock identities pass. Native Apple silicon inspection shows three selected tabs with identical readable backgrounds in both active and inactive windows; dark/high-contrast visual inspection and physical Intel are not claimed.

Both incremental browser/ChromeDriver/installer builds and UI/settings/browsing/profile-persistence checks pass. The reused review workspace includes the separately pending pinned-tab-groups source; that topic is excluded from this input, and all three patches affecting the mixer independently replay to identical bytes. The isolated preview, test driver and seven disposable artifact trees have been removed; prepared source and incremental outputs remain. The [completion record](../builds/2026-11-12-native-tab-selection.json) retains exact source and validation scope.

```sh
python3 scripts/check-native-tab-selection.py SOURCE --arch arm64
python3 scripts/check-native-tab-selection.py SOURCE --arch x86_64
```
