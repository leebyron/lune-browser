# Page-top window dragging

[Issue #47](https://github.com/leebyron/lune-browser/issues/47). The owner accepted the Apple silicon preview on November 18, 2026.

## Behavior

- **Allow window dragging from the top of webpages** is an opt-in Appearance setting. The preference applies to open windows. Hold Command at mouse-down to bypass it for that gesture.
- The eligible band uses the floating toolbar height in window coordinates. The current height is 52 logical points, from 36-point controls and two 8-point margins. Page scrolling and zoom do not change the band. Existing toolbar coverage and page insets determine which parts of the band expose page content.
- In a movable window, a primary-button press on exposed blank webpage background can become a native AppKit window drag after 4 points of movement. Browser controls, resize edges, modal surfaces and docked DevTools retain their ordinary input paths. Fullscreen is excluded.
- The original press reaches the page immediately. Blink checks the hit target in the top-level HTTP or HTTPS document and preserves page input for text, links, controls, editable content, scrollbars, frames, pointer lock, interactive event listeners and uncertain targets. A late eligibility result leaves the gesture with the page. Starting the native drag balances Blink's pressed state and uses the existing toolbar presentation hold.

## Validation

Run [the native browser fixture](../../../scripts/check-native-page-top-drag.py) against a built output directory with ChromeDriver. It uses a disposable profile and a loopback page. The fixture posts native Quartz mouse events, confirms the target is the topmost browser window at the press point, and measures the window's displacement through WindowServer. It checks exact travel in both directions, repeat drags after release, the two sides of the 52-point band, the Command bypass, clicks, text selection, pointer capture, iframe input, live Settings changes and the saved preference.

The initial fixture read webpage screen coordinates and reused a synthetic cursor position after release. The settled fixture targets the main browser window by native bounds, supplies mouse deltas, clears hover state before each press, and leaves link interaction until the other gestures finish because previews can cover their coordinates. The settled suite checks displacement and webpage outcomes for every gesture.

See the [adoption evidence](../builds/2026-11-18-page-top-window-drag.json) for the selected source, build identities, and validation scope.
