# Native tab status indicators

On macOS, media, capture, sharing, device and VR alerts use SF Symbols in
ordinary tabs and in their hover-card footers. In ordinary tabs the alert
occupies the trailing close-button position. The close button takes that
position on hover or when it has keyboard focus. Recording, sharing, device
and VR alerts report status. Pinned and icon-only tabs show the highest-priority
alert in the compact icon area.

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

## Tab context menu

**Mute Tab** and **Mute Site** appear when a tab targeted by the menu has a
controllable media session or its current page has played audible audio. This
covers paused media and audio that already ended. Muted tabs and sites can
still be unmuted, including either site in Split View. **Hibernate** is omitted
when the clicked tab is already hibernated.

The owner accepted the arm64 preview. Fresh preparation, both architecture
builds, smoke checks, and native sidebar menu checks passed. The Intel checks
ran under Rosetta on Apple silicon. See the
[adoption validation](../builds/2026-11-23-contextual-tab-menu.json).

### Tab grouping menu

An ungrouped tab's menu starts with **New Tab Below**, **Group Tab** or
**Group Tabs**, **Add Tab to Group** or **Add Tabs to Group** when a destination
exists, **Add Tab to New Split View** or **Add Tabs to New Split View**, and
**Move Tab to New Window** or **Move Tabs to New Window**. Grouping creates a
new group. The Add submenu contains existing destinations.

A grouped tab's menu offers **Remove From Group** and, when another group
exists, **Move Tab to Group** or **Move Tabs to Group**. The submenu excludes
the clicked tab's group, including for selections that span groups. Tab
commands apply to the selection when the clicked tab is selected, and otherwise
to the clicked tab or split. Existing split arrangements retain their contextual
controls.

[Adoption validation](../builds/2026-11-23-tab-grouping-actions.json)

## Page loading progress

Each loading tab shows a two-pixel line along its bottom edge, including
background and pinned tabs. It follows the same navigation progress, easing,
pulse and completion fade as the address-bar indicator. The halo above the
line uses 30% of its original opacity. Native uses the system tab-loading
blue, lightened in light mode. Both Lune appearances use the dark theme’s
teal button highlight. Other themes shift an analogous hue toward blue,
and high-contrast and forced-color modes use the system primary color.

**Show page loading progress in tab** is enabled by default under
**Appearance and behavior**. Turning it off immediately hides the line and
halo and stops their animations across the profile. Turning it back on
during a load shows the current progress. The address-bar indicator has
its own setting.

See the [loading progress validation](../builds/2026-11-21-tab-loading-progress.json) for the
paired browser builds and preference checks.
