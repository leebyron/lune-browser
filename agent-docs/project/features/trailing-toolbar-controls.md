# Trailing toolbar controls

## Layout and control ownership

- Move the real Chromium Views actions into the transparent floating child widget. Preserve extension artwork, badges, accessibility, command handlers and popup anchors. Restore layout margins and animation modes when transferring back to the ordinary toolbar.
- Size from intended layout visibility, including disabled actions and controls temporarily hidden by animation or overflow. Empty groups hide the material and input region. A single item centers in a 36 pt circle. Multiple items use 4 pt outer padding and 2 pt gaps. The Extensions menu has no gap before the first extension. At standard density, ordinary icon targets are 32 pt and the icon-only ellipsis is 30 pt. Reserve each animated action's final preferred width to keep the ellipsis available.
- Browser-owned symbols share an opaque mask and semantic AppKit colors. Header controls use 16 pt medium except Site Information and Reload/Stop at 14 pt. Tab/footer close uses 11 pt medium. Hover fades over 100 ms in both directions and reverses from the current color. Pressed and disabled states take precedence. Preserve the Profile identity-animation path and handle null icon names from drag placeholders.
- Customize uses the same symbol mapping. Home leads the trailing group when enabled. Back and Forward share a separator when both are shown, center a single control in 36 pt, or hide the navigation pill with both off. Preserve the New Tab row's slot on layout switches and the native Collapse Tabs button's pointer area. With a right sidebar and Collapse Tabs off, the empty header uses a 10 pt inset and the toolbar drag shield yields to sidebar row controls.

## Address and native menus

- Center the address capsule between the navigation and trailing groups. Its collapsed width is limited by the gap between the groups, half the available header region outside the sidebar, and a 700 pt cap. Results extend the glass by 10 pt per side up to 720 pt, with the field, Site Information and Reload held in place. Reload uses a 32 pt target and 2 pt trailing inset. Hiding it returns the target width to the field, preserves the 40 pt leading inset and retains short display-text centering. [Width validation](../builds/2026-11-19-native-search-width.json)
- Right-click, Control-click and a 500 ms hold on Back, Forward and Reload use Chromium's existing menu provider, availability and original commands. Consume a recognized hold before mouse-up can also click. With no menu, allow the ordinary click. Reload's menu retains its DevTools and Reload-state gates.
- A second click on Site Information must leave the bubble closed after release. Observe the bubble widget hiding or destruction during a press over its icon, then suppress that release's reopen action. Clear any unused latch after dispatch. A mouse-down monitor alone lost the race with Chromium focus-loss dismissal.

## Customize temporary icon removal

Disable the side panel's ephemeral toolbar button. Explicitly pinned Customize keeps its visibility and active state. Keep the window-local header/sidebar reveal while the Customize entry is visibly open, including on focus loss. See `customize-chrome-reveal.patch` and `customize-no-transient-toolbar-icon.patch`.

## Header context menu opens Toolbar

The header uses **Customize Toolbar** and `IDC_SHOW_CUSTOMIZE_CHROME_TOOLBAR` to open the Toolbar section. Main-menu appearance remains separate.

### Header and sidebar menu scope correction

Within the visible sidebar's horizontal bounds, including above its first row, route the header click to the sidebar menu. Pinned and popover sidebar menus retain **Customize Lune** and the general appearance destination. Pass the current source at each initialization of the cached menu builder. See `header-customize-toolbar-scope.patch` and the [routing validation](../builds/2026-11-11-header-menu-scope-validation.json).

## Source and validation

Start in the platform's `native-toolbar-symbols.patch`, `floating-toolbar-layout.patch`, `floating-toolbar-preferences.patch` and `responsive-address-capsule.patch`. Use [the native toolbar fixture](../../../scripts/check-native-toolbar.py) for semantic colors, animation and gesture/layout logic. Its stand-ins leave live Views layout, Skia and actual popup interaction to headed browser checks.

The reviewed [issue #9](https://github.com/leebyron/lune-browser/issues/9) stack passed zero-fuzz byte parity, both architecture builds and focused native/headless checks (Intel under Rosetta). Apple silicon inspection confirmed menu dispatch and Reload hold with DevTools. The owner confirmed drag reordering and second-click Site Information dismissal. Later Customize checks covered the focused icon and menu changes. The full interaction matrix remains broader than this evidence.

[Full reviewed stack, exact symbol mappings, preview history and validation limits](https://github.com/leebyron/lune-browser/blob/55e6622e6d5891e36149ba2e646cad543dabc51f/agent-docs/project/features/trailing-toolbar-controls.md)
