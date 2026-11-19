# Sidebar tab drag haptics

On macOS, dragging a sidebar tab produces a tick when the preview moves to a new valid insertion position or group. Tearing the tab off produces a tick when the new window appears. Hovering at the same position, moving through an invalid target, and moving an entire window stay silent.

**Tab drag haptics** is enabled by default in **Settings → Appearance & Behavior → Behavior**. The per-profile preference controls both insertion and tear-off feedback. Both use AppKit’s Generic pattern through the system feedback performer, which respects the current input device and system settings. The new label uses the English fallback until translations are available.

Dragging a group header uses the same tick when its reorder slot or pin state changes, or when the group tears off into a new window. Group targets use the stationary rows and a small boundary margin to avoid repeat ticks when a separator appears or disappears. The owner accepted the updated drag behavior on November 18, 2026. [Group drag validation](../builds/2026-11-18-tab-group-drag-haptics.json)

The owner accepted the Apple silicon preview on November 18, 2026. Fresh zero-fuzz preparation matched the reviewed source with four license-header corrections. Both builds passed browser smoke checks and verified the toggle default and persistence. Intel runtime checks used Rosetta. [Build evidence](../builds/2026-11-18-sidebar-tab-drag-haptics.json) · [Issue #48](https://github.com/leebyron/lune-browser/issues/48)
