# Sidebar density and top-edge reveal

Accepted November 21, 2026 for [issue #54](https://github.com/leebyron/lune-browser/issues/54). The development lock selects signed platform input `inputs/sidebar-ui-polish-1/macos` over the approved app icon gradient.

## Pinned tabs

- Expanded pinned tiles are 36 logical pixels tall in Standard and 46 in Comfortable. Regular rows are 30 and 36 respectively. Fully collapsed tiles stay square.
- During an individual [tab drag](pinned-grid-tab-drag.md), the floating tab uses its rendered height for vertical content centering. The original vertical grab fraction applies to the rendered height throughout the reversible 240 ms morph. A grab 20% from the top adds 2 px above the pointer and 8 below when a Comfortable tab grows by 10 px. Destination layout uses the final tile size from the start.

## Unpinned sidebar reveal

- The top edge reveals the unpinned sidebar within 112 logical pixels of its side of the window. The rail mirrors for right alignment and works alongside the existing side rail.
- The sidebar shares the toolbar's [top edge entry and retention geometry](native-chrome-hover.md), including the app-fullscreen menu-bar rules. Webpage fullscreen suppresses the sidebar.

## Comfortable layout

- Tab, New Tab, footer and section labels use 14 pt. Date labels use 10 pt. Group headers are 28 px and date rows are 20 px, with the added space distributed above and below their labels.
- Tabs and tab-like footer controls use a 12 px outer corner radius. The 26 × 26 px close targets use a concentric 6 px highlight radius. Trailing tab status icons and group chevrons share the close glyph's horizontal center.
- The expanded sidebar defaults and snaps to 240 px. Standard uses 216 px. A saved width takes precedence in either density.

[Validation record](../builds/2026-11-21-sidebar-ui-polish.json)
