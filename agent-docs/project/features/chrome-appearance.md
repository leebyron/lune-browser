# Native chrome appearance

## Material and foreground

On macOS 26+, the floating header and sidebar use regular `NSGlassEffectView`. Preserve the material, attached controls, editor focus and selection across **Content aware** toggles. The independent profile preference `helium.browser.content_aware_chrome` defaults true and preserves a saved false. With it off, a neutral 80%-opacity backing uses the browser's Light/Dark/Device choice to bound sampled page luminance. With it on, glass samples the page directly. Older macOS uses the [visual-effect fallback](older-macos-appearance.md).

Native foregrounds belong inside `NSGlassEffectView.contentView` to inherit its effective legibility appearance. The profile or explicit view appearance alone cannot predict the rendered glass. Separate transparent Views windows need a per-host appearance bridge and color/image cache invalidation. Preserve extension artwork, weak widget ownership and teardown of callbacks.

Large regular glass may appear more opaque and adapt differently from small toolbar pills. Keep the sidebar's own foreground bridge. Header-driven adaptation lagged and stopped when the header hid. The accepted policy uses native primitives and avoids page capture or polling.

## Theme tint

The shared `NativeGlassThemeTintColor` helper takes the HSL midpoint of the owning theme's light and dark `ui::kColorSysPrimary` values at 5% alpha. Use the shorter hue arc and the chromatic endpoint's hue when one endpoint is achromatic. Derive light/dark providers from the same browser key so custom and incognito state survive. System theme leaves the header untinted. Handle theme notifications before widget attachment and refresh hidden surfaces as well as visible ones.

Later changes give the [unpinned sidebar its own palette policy](themed-unpinned-sidebar.md), share the [tint with Command-T](command-bar-corners.md#coradial-corners-and-shared-tint-candidate--november-9-2026) and keep the [Command-T backing visible at every size](command-menu-stable-glass.md). The sidebar and menu have distinct material policies.

## Header shadows and inactive windows

Navigation, address, trailing controls, the sidebar toggle and Customize close use an `NSShadow` with 5% black, 10 pt blur and 3 pt downward offset. Update the rounded shadow path with bounds, including suggestion height, and keep it attached to the material's fade. Direct layer-shadow values were reset by AppKit appearance changes. The sidebar background has no added header shadow. The tint has no activation-dependent clearing. Earlier inspection never reached a genuinely inactive window, so the reported inactive tint change still needs native evidence.

## Sidebar toggle

The sidebar toggle uses a 36 pt native glass container with the same tint,
shadow and older macOS fallback as Back and Forward. Its 32 pt button stays
inside the glass content and inherits its foreground appearance.

The toggle sits 8 pt below the sidebar top and 8 pt inside the divider. The
adjacent Back and Forward pill on the left or the tools pill on the right sits
8 pt into the content from the same divider. Pinned and fully revealed sidebars
share this geometry. The toggle fades with the sidebar and follows its existing
visibility preference.

[Sidebar toggle validation](../builds/2026-11-23-sidebar-toggle-glass.json)

## Source and validation

Start with the platform's `glass-icon-appearance.patch`, `glass-material-appearance.patch` and `native-header-glass-shadows.patch`. Issue [#7](https://github.com/leebyron/lune-browser/issues/7) used the accepted stack through `622ccfac`. Use [the appearance fixture](../../../scripts/check-native-chrome-appearance.py) for material identity, appearance bridge, editor focus and shadow geometry, then inspect contrast and active/inactive transitions in a headed browser.

Strict replay matched 17 files. The final 5% tint and shadow passed paired builds and native fixtures (Intel under Rosetta). The broader Settings smoke matrix was last run at an earlier tint strength. The owner accepted the final light appearance and persistent controls. Fullscreen, accessibility and the complete active/inactive matrix remain outside the cited evidence.

[Full issue #7 history, AppKit comparisons and validation records](https://github.com/leebyron/lune-browser/blob/55e6622e6d5891e36149ba2e646cad543dabc51f/agent-docs/project/features/chrome-appearance.md)

## Toast contrast

Browser toasts use the surface foreground (`ui::kColorSysOnSurface`) for the
label, icon, and controls on the omnibox container background. Native Light
provided white selected-tab text on a white toast surface. The AppKit color
mixer measured 14.94:1 in Native Light and 12.23:1 in Native Dark with the
surface foreground. The same ratios held with increased contrast enabled.

The macOS platform selects `helium/ui/native-toast-contrast.patch` after the
Helium toast patch. The arm64 and x86_64 browser builds and smoke checks passed,
with x86_64 running under Rosetta. The color fixture exercised both architectures.
The Mac was locked during on-screen verification.

The **New tab opened** toast uses the `plus.square.on.square` SF Symbol at the
existing toast icon size. It uses the toast foreground color and falls back
to the registered vector icon if AppKit cannot supply the symbol.
[Build and native toast checks](../builds/2026-11-23-sidebar-background-input.json)
