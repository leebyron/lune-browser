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
