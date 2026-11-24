# Native chrome hover and fullscreen

The November 18, 2026 baseline was adopted in signed input `inputs/native-chrome-hover-1/macos` at `ae139acca1c433e899f08028cdb9485a1f741d2f`. It addresses [fullscreen header hover](https://github.com/leebyron/lune-browser/issues/39), window proximity, and [webpage fullscreen sidebar suppression](https://github.com/leebyron/lune-browser/issues/19). Published browser releases retain their frozen inputs.

## Behavior

- The side reveal distance is 16 logical pixels and retention is 128 pixels, extending inward past the revealed sidebar and outward from the window edge. Top reveal extends 4 logical pixels inside and 16 above the window edge. Retention extends 64 pixels below the glass and 64 pixels above a windowed content edge. Chromium DIPs correspond to AppKit points. Fullscreen's one-pixel rule below uses the physical backing scale. In **On hover sidebar**, the top rail reveals the toolbar above a visible
  sidebar within its horizontal bounds. The upper 52 points of the visible sidebar also reveal it.
- In both app and webpage fullscreen, any menu-bar or camera-safe strip above the available content is eligible for top reveal, together with one physical pixel inside that content. With no such strip, top entry uses the ordinary 4-point interior distance. The same 64-pixel retention below the header applies. Other screens remain excluded, and webpage fullscreen never gains side reveal.
- The active native window polls the pointer every 100 ms because window mouse events do not cover exterior proximity. This proximity poller stops on deactivation; independent editing/menu retention keeps its existing behavior.
- Webpage and extension fullscreen suppress the sidebar at its shared eligibility and native presentation boundaries. Side rails, traffic-light hover, direct reveal, saved pinning, menu/focus holds and stale animation state cannot expose a sidebar or its input hosts. Preferences remain unchanged, and ordinary windowed or app-fullscreen behavior returns on exit.
- App and webpage fullscreen derive header placement from the live content window and the visible menu-bar fraction. Only menu-bar space that overlaps the content contributes an offset. An always-visible menu or camera area already outside the window is not counted twice, including on initial fullscreen entry. Menu animation and changing the visibility setting use the same calculation. Native fullscreen exit controls remain available.

## Source and validation

The platform patches are `helium/ui/fullscreen-header-hover.patch`, `helium/ui/window-chrome-proximity.patch`, `helium/ui/content-fullscreen-chrome.patch`, `helium/ui/chrome-hover-distances.patch`, and `helium/ui/fullscreen-menubar-geometry.patch`. They are developed with quilt against the adopted sidebar-drag input, with temporary logging excluded from the patches.

`scripts/check-fullscreen-header-hover.py` compiles the production native geometry and sidebar eligibility methods with display/window fixtures. Cases cover 1x/2x scale, offset displays, menu-bar/camera gaps, initial and animated menu-bar offsets, changing visibility settings, the side and top reveal and retention boundaries, the one-physical-pixel fullscreen content rail, and content-fullscreen exclusion on either sidebar side. Existing DevTools, toolbar-mode and header-drag fixtures also cover the candidate. Intel fixtures execute under Rosetta.

The owner accepted the native arm64 behavior, then explicitly approved the final top 16/64 distances and 64-pixel space below the open toolbar. Complete zero-fuzz preparation reproduces the approved source and generated resources byte for byte. Both final browser builds, UI/Settings/artwork/browsing/persistence smoke checks, focused native fixtures and affected GN target checks pass; x86_64 executes under Rosetta. The complete source inventory is unchanged through both builds. See the [compact adoption evidence](../builds/2026-11-18-native-chrome-hover.json); detailed logs and timings remain under `.work/fullscreen-header/`.

The November 19 update narrows interior entry in `helium/ui/narrow-top-toolbar-reveal.patch` and matches it in the [website browser illustration](../../../website/spec/experience.md#browser-illustration). Paired builds, smoke tests, native hover fixtures, and windowed pointer checks pass. The [validation record](../builds/2026-11-19-top-toolbar-reveal.json) includes the observed boundaries and website checks.

The [November 21 sidebar update](sidebar-ui-polish.md#unpinned-sidebar-reveal) reuses the toolbar's top-edge geometry to reveal the unpinned sidebar within 112 px of either configured side.

The November 24 update synchronizes the sidebar toggle with the toolbar, gives
the visible sidebar header the native top reveal rail, and narrows the shared
interior rail to 4 points. The right toggle moves into its own trailing glass
unit on the toolbar. [Combined adoption evidence](../builds/2026-11-24-sidebar-toolbar-hover.json).
