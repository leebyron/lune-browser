# Pinned toolbar and page inset

The reviewed [issue #11](https://github.com/leebyron/lune-browser/issues/11) implementation entered the November 8 development input. [Onboarding integration](onboarding.md) later removed the launch flag. Use [toolbar hover modes](toolbar-visibility.md) for the current choices and settings order.

## Layout contract

| Mode | Page behavior |
| --- | --- |
| On hover edge or On hover sidebar | Full-height viewport with no header-driven inset. |
| Always | Reserve a browser-owned 52 pt top band and translate ordinary page layout below it. Keep the renderer surface full height and let the document scroll behind the toolbar. Apply protection even to pages declaring `viewport-fit=cover`. The header adds no CSS safe-area value in this mode. |
| Always cover (experimental) | Honor desktop `viewport-fit=cover`. Opted-in pages use the full viewport and receive the header through `env(safe-area-inset-top)`, 52 CSS px at normal zoom. They can paint behind the controls. Ordinary pages retain the inset. |

Keep layout, root/background painting, hit-test clips and the per-WebContents inset in sync, including existing and background tabs. The protective band takes the root or propagated body color. Background images extend behind the toolbar on opted-in experimental cover pages. Reuse compositor scrolling and the existing viewport update path. Protective mode solves the observed Apple and Substack overlap, where desktop fixed headers declared cover without applying top safe-area padding.

## Settings and Customize content

The native menu and Appearance settings share profile preferences, updating open windows immediately. On macOS the default Lune Panels position follows the opposite side of the tab sidebar. The derived position is read-only in Settings. Per-panel overrides remain configurable. The vertical-only selector change hides Classic, Dynamic and Compact choices while preserving saved layout values. The shared macOS Customize content has 52 px top padding with its existing height and native close control.

## Source and validation

Start with the platform's `obscured-header-prototype.patch`, `obscured-header-cover-prototype.patch`, `obscured-header-modes-prototype.patch`, `obscured-header-settings-prototype.patch` and `customize-content-top-inset.patch`. Follow `BrowserFrameViewMac::HasFloatingAddressBar`, WebPreferences and the Settings appearance page. The [reviewed input](reviewed-ui-integration.md) records integration.

The original headed and headless renderer fixtures checked ordinary and opted-in viewport geometry, live transitions, scroll position, fixed and nested clicks, and zero layout/style recalculations during the measured wheel scroll. Settings checks covered mode/sidebar persistence and menu synchronization. The reviewed stack replayed 31 affected files and the final 52 px Customize change passed native Apple silicon review. Those checks leave native Intel, fallback, zoom, fullscreen, split panes, accessibility and nonstandard content/windows outside the demonstrated matrix.

[Full prototype history, compatibility traces and fixture locations](https://github.com/leebyron/lune-browser/blob/55e6622e6d5891e36149ba2e646cad543dabc51f/agent-docs/project/features/header-inset-prototype.md)

## Regression checks for #11

Run the packaged browser check with the matching ChromeDriver. Use a separate
report for each architecture and scale. The example uses the standard arm64
build path.

```sh
(
  for scale in 1 2; do
    python3 scripts/smoke-browser.py .work/arm64/macos/build/src/out/Default \
      --arch arm64 --toolbar-inset --device-scale-factor "$scale" \
      --report ".work/arm64/toolbar-inset-${scale}x.json" || exit
  done
)
```

The [loopback fixture](../../../scripts/fixtures/toolbar-inset.html) exercises
all four Settings modes through the packaged control, using ordinary and cover
pages that stay loaded across changes in separate windows. At 80%, 100%, and
125% browser zoom, the report checks five viewport height measurements,
52 pt of inset where required, sticky and fixed positioning, and the CSS safe
area. It measures live changes to `viewport-fit`, trusted renderer clicks and
wheel events, form typing, webpage fullscreen entry and exit, and the saved
cover preference after a browser restart. The smoke report includes the browser
and framework hashes, requested scale, per-case measurements and failures.
ChromeDriver delivers input to the page. Use the headed checks below for AppKit
hit testing and presentation.

[Release staging](../release-delivery.md#commands-and-gates) requires both scales
for each candidate build and preserves the two smoke reports with the staged
artifact.

Run the adjacent production fixtures on the same prepared source with
`--arch arm64` and `--arch x86_64`.

- [Toolbar mode and engagement](../../../scripts/check-toolbar-visibility.py)
  and [fullscreen geometry](../../../scripts/check-fullscreen-header-hover.py).
- [DevTools hover](../../../scripts/check-header-devtools-hover.py),
  [wheel routing](../../../scripts/check-native-header-scroll.py),
  [drag and resize retention](../../../scripts/check-header-drag-retention.py),
  and [activation and focus](../../../scripts/check-native-focus-retention.py).
- [Fallback material and bounds](../../../scripts/check-native-fallback-surfaces.py).

### Headed acceptance

Use an isolated profile and the same build as the automated report. Open the
fixture as a local page and append `?cover` to opt into cover. Record the mode,
sidebar state, display scale, OS and execution architecture for failures.

| Scenario | Check |
| --- | --- |
| App fullscreen | Start in **Always**. Enter fullscreen with the green button. Check that the page's top link clears the toolbar, opens the anchor, and remains clickable as the menu bar shows and hides. Exercise a menu bar that overlaps the content as well as a visibly reserved menu-bar area, and check that the page and toolbar return to their windowed positions on exit. Repeat with **Always cover (experimental)** on both fixture URLs. |
| Two windows and native controls | Switch active windows and switch away from Lune while editing the address. Open and cancel the toolbar, sidebar and window menus. Use Customize, drag and resize, then check that the header resumes the selected mode and neither window keeps a stale hover or focus hold. Repeat with pinned and unpinned sidebars on both sides. |
| Split panes, infobars and PDF | Check both panes when switching focus and moving the divider. Open a browser infobar and use its action and dismissal controls. Open a standalone PDF and an embedded PDF, then try the viewer's toolbar, document scroll and text selection. Check that the page, viewer and browser controls remain reachable in both Always modes. |
| Accessibility and platform | With the toolbar visible, use keyboard navigation and VoiceOver to reach the toolbar, sidebar and page controls. Check focus visibility, labels, navigation order and the Show toolbar and Sidebar position controls. Inspect Light, Dark, System and Increase Contrast on an actual pre-26 system for fallback rendering. Record physical Intel separately from Intel under Rosetta. |

[Issue #52](https://github.com/leebyron/lune-browser/issues/52) tracks the compact
toolbar for narrow windows. [Issue #53](https://github.com/leebyron/lune-browser/issues/53)
tracks pointer input in side-docked DevTools in Split View.

### November 20, 2026 results

The locked Chromium 158.0.8127.37 builds at macOS input
`622464d3bfb4ecb0f1da565d6556b12d1d3f38f6` passed all 40 cases per run
at forced display scales 1× and 2× on both architectures. The Intel build ran
under Rosetta on macOS 26.6.2. The combined arm64 UI, Settings, artwork, and
toolbar smoke passed, as did all seven focused production fixtures on both
architectures and the repository suite of 107 tests with one skip.
Detailed reports and framework hashes are in `.work/toolbar-inset-acceptance/`.

The release smoke commands also passed all four configurations on locked macOS
input `27d3bb1ca55104221386ef4a592d0b3d6a7ad728`, with 40 toolbar cases per
configuration and Intel under Rosetta. The staging gate accepted the reports
against the exact [built framework hashes](../builds/2026-11-20-page-top-drag-eligibility.json).
The repository suite ran 108 tests with one skip, including staging rejection
of absent, failing, wrong-scale, and mismatched reports.

The headed arm64 check kept the toolbar visible on entry to app fullscreen,
activated the fixture's top link with a pointer click, and restored the
windowed toolbar on exit. Positive menu-bar overlap, the full headed
interaction matrix, PDF and infobar controls, VoiceOver, and actual older macOS
remain to be checked.
