# Native tab status indicators

On macOS, media, capture, sharing, device and VR alerts use SF Symbols in
ordinary tabs and in their hover-card footers. In ordinary tabs the alert
occupies the trailing close-button position. The close button takes that
position on hover or when it has keyboard focus. The tab context menu offers
**Mute Tab** and **Unmute Tab**. Recording, sharing, device and VR alerts report
status. Pinned and icon-only tabs show the highest-priority alert in the
compact icon area.

| Status | SF Symbol | Fallback when unavailable |
| --- | --- | --- |
| Picture-in-Picture | `pip` | |
| Audio playing | `speaker.wave.2` | |
| Audio muted | `speaker.slash` | |
| Camera | `video` | |
| Microphone | `microphone` | `mic` |
| Camera and microphone | `video.badge.waveform` | `record.circle` |
| Tab sharing | `interface.window.on.rectangle` | `macwindow.on.rectangle` |
| Screen or window sharing | `display` | |
| Bluetooth connected or scanning | `antenna.radiowaves.left.and.right` | |
| USB device | `cable.connector` | |
| HID device | `gamecontroller` | |
| Serial device | `cpu` | |
| VR headset | `vision.pro` | `eyeglasses` |

Recording and outbound tab and screen sharing use AppKit’s system red in
both surfaces. The media icons in the tab strip use the tab label color.
A connected Bluetooth device shows a steady antenna. Scanning cycles
through the native symbol’s variable-opacity waves from the inside out in
the tab and hover card. Reduce Motion gives the scanning alert a steady
symbol. The shared mapping uses Chromium’s artwork when AppKit cannot
resolve a suitable symbol.

See the [adoption validation](../builds/2026-11-21-tab-status-symbols.json)
for the owner review, source replay and browser builds.
