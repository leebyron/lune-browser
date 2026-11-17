# Floating native address capsule

The vertical browser chrome uses a centered native address capsule with separate navigation and browser-action groups. The original [Figma reference](https://www.figma.com/design/I39uQunZpu6LsS7mDjcGSh/Untitled) was reviewed from the desktop export `02-mounted-right-design.png`. Use the [edge-to-edge frame record](edge-to-edge-frame.md) for geometry and the [project inputs](../status.md) for inclusion.

## Behavior

- Cmd-L or the first click enters native address editing, selects the full address and opens suggestions. Later clicks position the caret. Focus uses Chromium's `GetFormattedFullURL()`. New Tab starts with empty editing text, while an explicit visit to `about:blank` retains the literal URL.
- Chromium's profile-aware `AutocompleteController` supplies matches. Up/Down changes selection, Return opens the result, Cmd-Return opens a foreground tab and Escape restores the page address. Cmd-T keeps its separate [command palette](command-bar.md). See [suggestion selection](address-suggestion-selection.md), [bangs](address-bar-bangs.md), [cursor behavior](address-bar-cursor.md) and [overflow padding](address-overflow-padding.md) before editing those paths.
- Editing and browser bubbles retain the controls. [Toolbar mode](toolbar-visibility.md) determines entry. Pointer retention extends 48 pt below the revealed header. The header surfaces and trailing controls fade together. Left traffic lights follow the top toolbar or visible left sidebar and keep their left position with a right sidebar.

## Source and constraints

- In `chrome/browser/ui/views/frame/browser_frame_view_mac.mm`, follow `HeliumFloatingAddressBar` and `HeliumGlassSurface`. Start with the platform's `native-floating-address-bar.patch`, `glass-address-editor.patch` and `native-address-editing-text.patch`. The [toolbar record](trailing-toolbar-controls.md) covers responsive width, Site Information, Reload and menu anchors.
- Keep the native field and its capsule focus-ring mask. Call the editor's idempotent shutdown on profile destruction while keyed services are alive. Detach text/key callbacks and guard deferred edit completion. See `floating-address-lifecycle.patch`.
- Keep actual Views actions in their shadowless child widget so extension actions and menus retain their anchors. For bottom-edge resize, use actual AppKit content height for top-anchored native views and align child windows to the actual native bounds. Pending compositor geometry can move the header before AppKit applies the window frame.
- `performWindowDragWithEvent:` can return before physical mouse-up. Use the initiating-button latch for drag retention. Keep controls and native resize targets outside the drag region.

## Validation and evidence

The November 7 inputs passed strict replay, paired builds and browsing/settings/profile smoke checks (Intel under Rosetta). A native AppKit resize harness checked alignment during pending-versus-applied frame changes. The owner confirmed top anchoring on Apple silicon and the headed checks confirmed both empty New Tab editing and explicit `about:blank`. Synthetic clicks could not reliably exercise real pointer reveal, fullscreen edge entry or every hover transition.

Start with [native suggestions](../../../scripts/check-native-address-suggestions.py), [cursor](../../../scripts/check-address-field-cursor.py) or [overflow](../../../scripts/check-address-overflow.py) for focused changes. For native review, exercise Cmd-L and first click, a long URL, suggestions during close, and pointer reveal with both sidebar positions when affected.

[Full prototype history, design references, input IDs and test records](https://github.com/leebyron/lune-browser/blob/55e6622e6d5891e36149ba2e646cad543dabc51f/agent-docs/project/features/floating-address-bar.md)
