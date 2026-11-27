# Trailing toolbar controls

## Layout and control ownership

- Move the real Chromium Views actions into the transparent floating child widget. Preserve extension artwork, badges, accessibility, command handlers and popup anchors. Restore layout margins and animation modes when transferring back to the ordinary toolbar.
- Size layout and the child window from the same intended control visibility, including disabled actions and controls temporarily hidden by animation or overflow. Empty groups hide the material and input region. Icon-only trailing controls occupy 36 pt square slots and wider actions reserve their preferred widths.
- The glass background highlights immediately across a single-button surface. Groups highlight a 30 pt inset circle in the hovered slot. Gate pointer feedback on the actual pointer and receiving window when chrome appears. Back and Forward hide their shared separator when an arrow is hovered or has keyboard focus.
- Browser-owned symbols share an opaque mask and semantic AppKit colors. Header controls use 16 pt medium except Site Information and Reload/Stop at 14 pt. Tab/footer close uses 11 pt medium. Native header symbol tint fades over 100 ms in both directions and reverses from the current color. Pressed and disabled states take precedence. Preserve the Profile identity animation path and handle null icon names from drag placeholders.
- Customize uses the same symbol mapping. Home leads the trailing group when enabled, an explicitly enabled Extensions button can open its empty menu, and the app menu stays last. Keep the toolbar revealed while the Extensions menu is open. Preserve the New Tab row's slot on layout switches and the native Collapse Tabs button's pointer area. With a right sidebar and Collapse Tabs off, the empty header uses a 10 pt inset and the toolbar drag shield yields to sidebar row controls.
- Reorder pinned browser actions and pinned extensions within their respective groups. Hold the toolbar visible for the drag and compute the drop from logical slots while icons move. Use the same drop highlight color as the sidebar. Home and the Extensions launcher have fixed positions. The final app menu is outside the drop area.

## Address and native menus

- Center the address capsule between the navigation and trailing groups. Its collapsed width is limited by the gap between the groups, half the available header region outside the sidebar, and a 700 pt cap. Results extend the glass by 12 pt per side up to 724 pt. Site Information sits 2 pt closer to the leading edge and shares its horizontal position with the focused icon and result icon column. Idle Reload uses a 32 pt target and 2 pt trailing inset. When Reload is hidden by preference, short display text stays centered. See [address focus behavior](floating-address-bar.md).
- Right-click, Control-click and a 500 ms hold on Back, Forward and Reload open AppKit context menus at the cursor using Chromium's existing items and commands. Keep the toolbar visible while the menu tracks. Consume a recognized hold before mouse-up can also click. When the menu is unavailable, allow the ordinary click. Reload offers its menu in Reload mode with DevTools open or closed. Its existing shortcuts appear in AppKit's trailing shortcut column. [Native menu validation](../builds/2026-11-27-native-toolbar-menu-adoption.json)
- A second click on Site Information must leave the bubble closed after release. Observe the bubble widget hiding or destruction during a press over its icon, then suppress that release's reopen action. Clear any unused latch after dispatch. A mouse-down monitor alone lost the race with Chromium focus-loss dismissal.

## Site Information popover

The address capsule opens Site Information in a transient AppKit popover.
AppKit provides the glass, pointer, and edge placement. Center the pointer
under the Site Information button and offset the positioning rectangle
down 1 pt. The popover hosts the existing pages and actions.

Keep the floating toolbar visible while the Site Information popover is open,
including when the pointer moves into the popover below the hover area. The
popover holds the owning window's toolbar reveal until dismissal, then the
selected hover mode resumes. [Toolbar retention validation](../builds/2026-11-24-site-info-toolbar-retention.json)

Use SF Symbols in the primary label color for popover icons, with yellow
for the security warning triangle. Omit trailing external-link glyphs.
Center the title on the main page and subpages at the standard 13 pt
label size and regular weight. Subpages show only their own titles.
Omit Close. In subpages, center Back and the title vertically in the
compact header. Give Back the same top and leading inset and show its
circular hover highlight immediately. Omit the divider below the subpage
header.
Use a 344 pt minimum content width for website information so the English
connection warning fits on one line. Use the same typography and icon
column as the secure connection row. Use the same inset rounded hover
highlight as Downloads. Let the AppKit material show through the
permission list, including the Automatic downloads row. Use regular-weight
labels and headings. Distinguish headings, row titles, and details with size
and color.
Clicking the Automatic downloads row or its switch changes the site setting.
Keep its `arrow.down.circle` icon in both states. When the site has an
override, show a small AppKit **Reset** button immediately before the switch
that restores the default for Automatic downloads.

[Downloads and browser chrome validation](../builds/2026-11-24-downloads-popover.json)

[Original popover validation](../builds/2026-11-23-site-info-popover.json)

## Customize temporary icon removal

Disable the side panel's ephemeral toolbar button. Explicitly pinned Customize keeps its visibility and active state. Keep the window-local header/sidebar reveal while the Customize entry is visibly open, including on focus loss. See `customize-chrome-reveal.patch` and `customize-no-transient-toolbar-icon.patch`.

## Header context menu opens Toolbar

The header uses **Customize Toolbar** and `IDC_SHOW_CUSTOMIZE_CHROME_TOOLBAR` to open the Toolbar section. Main-menu appearance remains separate.

### Header and sidebar menu scope correction

Within the visible sidebar's horizontal bounds, including above its first row, route the header click to the sidebar menu. Pinned and popover sidebar menus retain **Customize Lune** and the general appearance destination. Pass the current source at each initialization of the cached menu builder. See `header-customize-toolbar-scope.patch` and the [routing validation](../builds/2026-11-11-header-menu-scope-validation.json).

## Source and validation

Start in the platform's `native-toolbar-symbols.patch`, `floating-toolbar-layout.patch`, `floating-toolbar-preferences.patch` and `responsive-address-capsule.patch`. Use [the native toolbar fixture](../../../scripts/check-native-toolbar.py) for semantic colors, animation and gesture/layout logic. Its stand-ins leave live Views layout, Skia and actual popup interaction to headed browser checks.

The hover, fixed-slot sizing, and drag changes are implemented in `glass-toolbar-hover.patch` and `glass-toolbar-drag-reordering.patch`. See the [paired adoption checks](../builds/2026-11-25-glass-toolbar.json).

The reviewed [issue #9](https://github.com/leebyron/lune-browser/issues/9) stack passed zero-fuzz byte parity, both architecture builds and focused native/headless checks (Intel under Rosetta). Apple silicon inspection confirmed menu dispatch and Reload hold with DevTools. The owner confirmed drag reordering and second-click Site Information dismissal. Later Customize checks covered the focused icon and menu changes. The full interaction matrix remains broader than this evidence.

[Full reviewed stack, exact symbol mappings, preview history and validation limits](https://github.com/leebyron/lune-browser/blob/55e6622e6d5891e36149ba2e646cad543dabc51f/agent-docs/project/features/trailing-toolbar-controls.md)
