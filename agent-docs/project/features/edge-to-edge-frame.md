# Edge-to-edge macOS frame

## Geometry and input ownership

- On macOS 26+, the existing Chromium AppKit frame hook and outer content clip use 16 pt corners. Individual web panes have square clips. Fullscreen has square edges. See the [older-macOS fallback](older-macos-appearance.md) for the 12 pt content radius and unmodified native frame on macOS 13–15.
- The page reaches the window edge. The pinned sidebar reserves its width and overlays a non-interactive, one-physical-pixel semantic separator. The unpinned sidebar is square glass flush with the outer edges, with the window providing the outer clip.
- The header is 52 pt high with 36 pt controls and 8 pt vertical clearance on either side. Use matching pinned/popover clearance and a 12 pt minimum adjacent gap. Windowed reveal observes an 8 pt perimeter without occupying layout space. Fullscreen uses four physical pixels at the top and one at the mounted side. [Toolbar mode](toolbar-visibility.md) controls top-edge entry.
- The presented header shields clicks through its top edge. Exclude controls using converted native bounds and let AppKit own native resize hits. The child-window/cursor reservation of 6 pt is independent of the 8 pt reveal band. Keep the existing 5 pt inner sidebar resize handle. [Header scroll routing](header-scroll-through.md) covers wheel and trackpad events.
- Use `TabStripView::IsPositionInWindowCaption` and native blank-area routing for sidebar dragging and menus. Tabs, scrolling, New Tab and resize handles keep their own input paths. The fullscreen menu-bar offset moves the relevant surfaces together.

## Resize behavior and open issue

`BridgedContentView::hitTest:` yields AppKit resize targets even when NSWindow queries the content view directly. During `NSWindow.inLiveResize`, freeze the shared header/sidebar reveal targets while layout continues following the window. Hidden surfaces stay hidden. The input-17 baseline selects Chromium's synchronous resize path and keeps the toolbar fade on content-view alpha. Chromium's compositor bridge owns NSWindow alpha, including while it waits for a correctly sized frame.

Resize cursor flicker remains open in [issue #5](https://github.com/leebyron/lune-browser/issues/5). The owner confirmed usable resizing and input-17 toolbar visibility after fullscreen but still saw flicker. Window, renderer and tracking-area cursor overrides and the sidebar-local coordinate experiment were tried and removed. The synchronous path alone did not fix flicker. Unshown-window hit-test fixtures establish the eight edge/corner targets. Cursor stability needs a physical pointer test. [Window-menu retention](window-menu-retention.md) covers the green-button popover separately.

## Source and validation

Start in `browser_frame_view_mac.mm` and the remote_cocoa AppKit bridge. The platform series includes `edge-to-edge-frame.patch`, `edge-to-edge-separators.patch`, `header-edge-input.patch`, `native-resize-hit-routing.patch`, `live-resize-chrome-retention.patch`, `synchronous-native-window-resize.patch` and `floating-toolbar-content-opacity.patch`. Verify order and active revisions in the [patch manifest](../../../manifests/patches.json).

The input-17 baseline had zero-fuzz replay, paired builds and browsing/settings/profile smoke checks (Intel under Rosetta). Native Apple silicon inspection exercised post-fullscreen toolbar visibility and controls. The owner separately accepted the 52 pt geometry, pinned blank-area drag/menu behavior and live-resize retention. Further cursor work was paused.

[Full input chronology, failed approaches and artifact-specific evidence](https://github.com/leebyron/lune-browser/blob/55e6622e6d5891e36149ba2e646cad543dabc51f/agent-docs/project/features/edge-to-edge-frame.md)
