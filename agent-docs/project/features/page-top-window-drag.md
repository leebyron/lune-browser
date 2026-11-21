# Page-top window dragging

[Issue #47](https://github.com/leebyron/lune-browser/issues/47). The owner accepted the broader eligibility on November 20, 2026.

## Behavior

- **Allow window dragging from the top of webpages** is enabled by default. Turn it off in Appearance. The preference applies to open windows, and saved choices take precedence over the default. Hold Command at mouse-down to bypass it for that gesture.
- The eligible band uses the floating toolbar height in window coordinates. The current height is 52 logical points, from 36-point controls and two 8-point margins. Page scrolling and zoom do not change the band. Existing toolbar coverage and page insets determine which parts of the band expose page content.
- In a movable window, a primary-button press on exposed blank page space can become a native AppKit window drag after 4 points of movement. Eligibility follows the rendered tab across URL schemes, including Chromium pages, local files and data URLs. Browser controls, resize edges, modal surfaces and docked DevTools retain their ordinary input paths. Fullscreen is excluded.
- The page receives the original press and the first movement before the browser takes over. Blink checks the point where the gesture began. Text selection, links, controls, editable content, scrollbars, embedded views and pointer lock keep their page input. A page can also claim the gesture by canceling the press or movement or by taking pointer capture. Passive observers and delegated handlers that let the gesture proceed can coexist with window dragging.
- If Blink's answer arrives too late or the originating document or surface changes, the page keeps the gesture. Starting the native drag balances Blink's pressed state and uses the existing toolbar presentation hold.

## Validation

Run [the native browser fixture](../../../scripts/check-native-page-top-drag.py) against a built output directory with ChromeDriver. It uses a disposable profile and a loopback page. The fixture posts native Quartz mouse events, confirms the target is the topmost browser window at the press point, and measures the window's displacement through WindowServer. It checks exact travel in both directions, repeat drags after release, the two sides of the 52-point band, the Command bypass, clicks, text selection, pointer capture, iframe input, live Settings changes and the saved preference.

The initial fixture read webpage screen coordinates and reused a synthetic cursor position after release. The settled fixture targets the main browser window by native bounds, supplies mouse deltas, clears hover state before each press, and leaves link interaction until the other gestures finish because previews can cover their coordinates. The settled suite checks displacement and webpage outcomes for every gesture.

The fixture verifies a window drag in a fresh profile before changing the setting. It disables dragging in the same window and restarts the browser with the saved off choice.

The eligibility checks exercise blank space inside inline layout and a landmark with passive and delegated listeners. They cover delegated cancellation, capture on the first movement, a slow renderer, a custom grab cursor, and an ARIA button. The same fixture runs over loopback HTTP, a local file, and a data URL. Native drags also start above and beside the heading on `chrome://media-engagement/`.

See the [original adoption evidence](../builds/2026-11-18-page-top-window-drag.json) and [default-on validation](../builds/2026-11-19-page-top-drag-default.json) for source and build identities.

See the [broader eligibility validation](../builds/2026-11-20-page-top-drag-eligibility.json) for the signed input, paired builds, and native regression results.
