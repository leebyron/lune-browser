# Initial browser window size

On macOS, a normal browser window with no explicit, active, or saved placement
opens at a target size of 1,316 × 825 points. The target allows 1,100 × 825 points
for content and 216 points for the expanded Standard sidebar.

Lune centers the window in the display’s usable area and caps each dimension
independently at the usable dimension minus 44 points. A 1,280 × 730 point usable
area yields a 1,236 × 686 point window. Centering includes the usable area’s
origin, including space reserved for a side Dock.

[Adoption validation](../builds/2026-11-24-initial-window-size.json)
