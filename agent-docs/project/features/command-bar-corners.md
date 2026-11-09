# Command-T glass bounds and layout

Issues: [#13](https://github.com/leebyron/lune-browser/issues/13) and the shared
result-row refinements for [#12](https://github.com/leebyron/lune-browser/issues/12).

## Accepted behavior

The native glass sits inside a 48 pt transparent margin on every side of its
translucent popup window. The native host receives the inner bounds; widget
position and sizing include the margin. This leaves room for native edge effects
instead of cutting them into square corners. Clicking the transparent margin
dismisses the popup through its existing widget lifecycle. Chromium's nearly
transparent window backing and its surface-invalidation workaround are preserved.

A supplemental shadow on the material uses 5% black, 10 pt blur, and a 3 pt
downward offset. Its explicit 20 pt rounded silhouette follows panel resizing.
There is no extra window shadow or clipping mask around the native glass.

The visible panel is at most 600 pt wide and shrinks to leave at least 36 pt
on either side of the browser window. Its top is anchored where a maximum-height
five-row panel (320 pt) would be vertically centered. Shorter lists keep that top
edge. The transparent shadow margin is excluded from visible-panel geometry.

The empty panel is 52 pt tall. The input uses its native fitting height and is
vertically centered; the provider pill shares its center. Results start directly
below the input, with an 8 pt bottom inset only when results exist. Action labels
use `tertiaryLabelColor`, and tab-switch actions read “Switch to Tab”.

Both menus use the shared `HeliumNativeResultRow` renderer. SF Symbols are
configured at 16 pt, medium weight, and drawn at native size without stretching.
Optical point size does not imply a 16×16 image: the native magnifying glass
measures 20×19 pt on the tested macOS. Downloaded favicons fit proportionally
inside a 16 pt slot. The final row geometry adds 2 pt of padding on each side of
the icon relative to the initial shared renderer: the icon center moves right
2 pt, and both text lines move right 4 pt. The trailing action column stays fixed.

Address results start 4 pt below the 36 pt editor and retain 8 pt side/bottom
insets. With results present, the outer glass expands 10 pt per side while the
site-information button, address input, and Reload retain their screen positions.
The wider glass and padded rows align the header and result columns. The outer
expansion disappears when the result list becomes empty.

## Source provenance

The signed, single-thesis platform stack follows shared-row commit `f0e2df52`
on `topic/command-bar-corners-reviewed`:

| Commit | Change |
| --- | --- |
| `471c5dc1` | Room for native glass shadows |
| `5c519619` | Tertiary action-label contrast |
| `6ebb3e54` | Smaller address editor-to-results gap |
| `52b508c7` | Centered, compact Command-T input layout |
| `95732b13` | Dismissal on shadow-margin clicks |
| `6c95434a` | Placement centered against the five-row maximum |
| `c1149c48` | 600 pt maximum width and 36 pt side margins |
| `d16491b9` | Address expansion with fixed header controls |
| `5c2eef52` | Native SF Symbol sizing and proportional favicons |
| `4958eb72` | “Switch to Tab” action label |
| `0a292dd7` | Subtle supplemental Command-T shadow |
| `7b9dda91` | Final shared icon padding and address-column alignment |

The review separates the former mixed layout commit into independent palette
layout, action-label contrast, and address-gap commits. The original stack is
preserved locally as `command-bar-corners-draft`. The reviewed stack reproduces
the exact accepted, built source bytes; no rendering change was introduced by
reorganizing commits. Each implementation remains a quilt patch in the macOS
platform repository. Evidence and portable fixtures are on
`command-bar-corners-evidence`.

## Validation and acceptance

- Strict zero-fuzz replay of 67 relevant patches reproduces all four affected
  source files. Platform patch lint passes; all 12 platform signatures verify.
- Both final browser builds pass for the exact accepted source. Intel runtime
  checks use Rosetta on the local arm64 Mac.
- Native shared-row tests pass on both architectures: selection/clear pixels,
  rounded bounds, Light/Dark/high-contrast invalidation, narrow/wide resizing,
  text truncation, target/action dispatch, focus policy, and optional hover.
  Glyph bounds match an unscaled AppKit image view; rectangular favicons retain
  their aspect ratio; the full “Switch to Tab” label fits its column.
- Native shadow checks pass on both architectures for the intended intensity,
  unclipped rounded silhouette, and empty/full/narrow resizing.
- UI/settings/persistence smoke checks pass on both architectures for Test 5,
  before the final icon-padding and address-width changes. Those final geometry
  changes pass both builds, native row checks, and live arm64 inspection.
- The owner accepted the layout and shadow-click dismissal in Test 3, the
  Command-T geometry in Test 4, and native icons plus darker shadow in Test 5.
  On November 8, 2026, the owner accepted final alignment in **Lune Corners Test 7**
  and authorized single-thesis commits, pushing, and resolving the issue.

Portable checks:

```sh
python3 scripts/check-native-address-suggestions.py .work/chromium-158/macos/build/src --arch arm64
python3 scripts/check-native-address-suggestions.py .work/chromium-158/macos/build/src --arch x86_64
python3 scripts/check-native-command-bar-shadow.py .work/chromium-158/macos/build/src --arch arm64
python3 scripts/check-native-command-bar-shadow.py .work/chromium-158/macos/build/src --arch x86_64
```

Native Intel hardware and the older macOS material fallback remain unverified.
The source candidate does not update the development lock or published binaries.
Local build, replay, native-check, and isolated preview artifacts remain in
`.work/command-corners/`; Test 7 remains available for owner testing.

## Coradial corners and shared tint candidate — November 9, 2026

Source inspection found a 20 pt Command-T panel radius around 10 pt selected-row
corners. Rows have an 8 pt horizontal inset and a 1 pt vertical paint inset,
so the previous 8 pt bottom layout inset produced a 9 pt visible bottom gap.
These corner centers did not align. The local `command-bar-coradial-tint`
candidate uses an 18 pt panel radius and a 7 pt bottom layout inset, producing
an equal 8 pt visible gap on the sides and bottom. The backing, glass, fallback,
and supplemental shadow share the panel radius. Shared row painting is unchanged;
its existing radius and vertical inset are now named constants.

Command-T also uses the address bar's shared `NativeGlassThemeTintColor` helper:
the theme's light/dark HSL midpoint at 5% alpha, or no tint for System theme.
The calculation moved to the existing native material utility, and frame surfaces
call the same implementation. Command-T obtains the owning browser tint when opened,
consistent with its existing appearance/content-awareness setup.

The owner accepted the preview and authorized committing and pushing to main on
November 9, 2026. Two signed platform commits follow the accepted onboarding input:

- `13c6e6177b0be80e6bccc1ee0b22c047ed8ab2be` — Align Command-T glass corners with result selection curves.
- `464c529859cd2b723320d3d43b1ddbd7fada1bc4` — Share the native browser glass tint with Command-T.

The development lock pins `464c529859cd2b723320d3d43b1ddbd7fada1bc4` under `inputs/command-style-2026-11-09/macos`.
Strict zero-fuzz replay from recorded prepared-source baselines matches all six
affected files. Platform patch lint and both full browser builds pass. Native
shadow/geometry, shared-row rendering, and appearance/tint checks pass on arm64
and x86_64 under Rosetta. Live arm64 inspection confirms the selected last row
and keyboard scrolling in **Lune Command Style Test**. Local evidence, build logs,
and the preview screenshot are under `.work/command-style/`.

Native Intel hardware and older macOS fallback visual acceptance remain unverified.
The broader browser/settings smoke matrix was not repeated for this focused
geometry/tint refinement. This updates source and development inputs only; no
published binary or release feed changes.
