# Dragging individual pinned tabs

Drag an individual tab into the top pinned grid to pin it, or back into the regular list to unpin it. The destination has an empty tab-shaped slot. The dragged tab morphs over 240 ms with easing in and out: its title fades and its icon moves between the initial and final left offsets using the same progress as the tab size. Reversing direction starts from the currently rendered geometry.

The title uses a separate layer only while the pin morph is active during a drag. It then paints with the tab again so group collapse clips the text. [Visual validation](../builds/2026-11-18-tab-group-drag-visuals.json)

Drop selection uses the pointer and final grid cells, including the current destination reservation. It does not use the floating tab's animated width or remove its gap from hit-test geometry. This keeps the chosen slot and the existing sidebar haptics stable while the morph runs. Only the container handling the drag paints a highlighted destination.

When no pinned tiles exist, the first-pin entry uses existing space above the tab list. Starting an ordinary tab drag adds no pinned row, gap, separator, or highlighted cell. Moving into that entry pins the tab and creates its actual destination slot. Ending or cancelling the drag clears temporary presentation. Cancellation retains the original drag snapshot and restores the original pin state; window attachment uses the current pin state.

The feature applies to individual non-split tabs. Split, multi-selection, whole-group and whole-window gestures retain their existing routes. Individual tile pinning remains separate from [pinned tab groups](pinned-tab-groups.md); existing group membership targets and section order remain in place.

With pinned groups present, the grid owns the space above the first group. An eligible individual tab enters a pinned group when the pointer reaches it. A tile entering a group unpins and becomes a member in one model change, including when moving back down from the grid in the same gesture. A small movement margin keeps the group targeted if removing a grid row moves it under a stationary pointer. [Group drag validation](../builds/2026-11-18-tab-group-drag-haptics.json)

The reusable platform patch is `helium/ui/pinned-grid-tab-drag.patch`, selected through signed input `inputs/pinned-grid-tab-drag-2/macos` (`b6b1f3af0ab64fac5fcf05e716042b329386ebcd`). It reparents the live view across pin changes, keeps model destination geometry separate from the applied presentation layout, and uses Chromium's existing pin state and persistence.

The owner accepted the native Apple silicon preview on November 18, 2026. [Validation evidence](../builds/2026-11-18-pinned-grid-tab-drag.json) binds fresh preparation, complete source parity after a whitespace-only export cleanup, paired builds and checks to the adopted input. Intel runtime uses Rosetta. [Focused regressions](../../../scripts/check-pinned-tab-drag.py) cover insertion stability and production paint/empty-entry policy with lightweight fixtures; they do not establish automated native pointer delivery or a complete split, focus-mode, window-transfer and older-macOS gesture matrix. [Issue #38](https://github.com/leebyron/lune-browser/issues/38)
