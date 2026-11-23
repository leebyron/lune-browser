# Automatic Picture-in-Picture

[Issue #50](https://github.com/leebyron/lune-browser/issues/50).

Switching tabs can move an eligible playing video into Chromium’s
Picture-in-Picture window. Returning to its source tab closes the automatic
window and returns the video to the page. An open manual Picture-in-Picture
window keeps its place. A site that registers a Media Session
`enterpictureinpicture` handler controls how its automatic window opens,
including Document Picture-in-Picture.

On macOS, AppKit draws the rounded video frame and the traffic lights in the
top-left corner. The button group fades with the header and shows its native
glyphs when the pointer enters the shared 36-point-high hover box. Close
dismisses PiP and pauses the video. Minimize dismisses PiP and keeps playing.
Fullscreen opens the source video in media fullscreen, with the Move & Resize
menu disabled for this button. The icon-only **Open Tab** button uses
`pip.exit` in a round glass surface at the top right. It returns to the source
and keeps playing. The header shows only the traffic lights and Open Tab.
Empty areas in all three regions let AppKit drag the window. The separate
permission prompt identifies the site.

Play/pause uses a white 33-point SF Symbol inside a 72-point translucent button.
The skip buttons use white 18-point symbols on 40-point buttons. Play/pause,
both skip buttons, **Open Tab**, and mute share the same glass tint, rim, and
brighter pressed state. The playback row stays
vertically centered at all window sizes. Play/pause scales the two symbols
through zero over 240 ms. Each skip arrow turns once around its circle in the
direction it points, easing out over 570 ms while both digits stay still.
The other playback and call controls use medium-weight SF Symbols.

The pointer controls visibility from the moment the window opens. In the header
strip, only the header and its gradient appear. In the footer strip, only the
footer and its gradient appear. Between the strips, both bars and the center
controls appear with a full-window dim that keeps the edge shadows' darkness and
softens toward the middle. Outside the window, an edge strip reveals
from up to 16 points away and stays visible within 64 points. A newly approached
edge takes precedence over retention from the opposite edge. Both hover strips
are 72 points high, and the footer includes room for track-skip controls.
Below 216 points tall, the middle band cannot fit the play button, so all
controls reveal together. During a window resize drag, all controls and their
shadows fade out. Layout keeps tracking the window, and hover is recomputed
when the drag ends. An active scrubber drag retains its controls. The controls
and their shadows fade together and honor Reduce Motion.

After 2.5 seconds without pointer movement, the visible controls and shadows
fade away. The pointer also hides over unobscured PiP video while Lune is the
active app. The first movement restores the pointer and reveals the controls
for its position. An active mouse gesture or keyboard navigation keeps the
relevant controls available. The pointer stays visible outside the PiP
window and while another app is active.

The playback footer groups elapsed time, the seek rail and playhead, and
minus-prefixed remaining time in one glass pill. The side padding and clock
spacing leave room for both times and the seek target at the minimum window
size. Hovering within the seek target animates the rail thickness and grows
the thumb from zero to 12 points. The seek target extends past both ends of
the rail. The separate speaker button has equal 12-point insets from the
bottom and trailing edge. Clicking it toggles mute and shows `speaker.slash`
while muted. Both the scrubber and speaker use the standard arrow cursor. Live
video shows its live status and speaker.

See [native tab status indicators](tab-status-indicators.md) for the PiP,
playing audio and muted audio badges and their hover cards.

Use **Settings → Privacy and security → Site settings → Automatic
picture-in-picture** to manage the default and site exceptions.
**Ask** remains the default. Chromium asks at eligible sites with sufficient
local media engagement and offers **Allow this time**, **Allow on every
visit**, and **Don't allow**. Explicit Allow skips the engagement threshold.
Playback still needs audio focus and recent audibility. For browser-initiated
video there must be a single eligible player in the primary main frame.
Incognito treats Ask as blocked.

On macOS, Lune offers to turn on automatic PiP the first time the user
opens video PiP manually for a site set to **Ask** in a regular profile.
The same in-window permission dialog names the domain in the question and
places **Allow** above **Not Now**.
**Allow** saves a site exception. **Not Now** dismisses the offer and
keeps the site on **Ask**. Both choices keep the current video playing. The
profile remembers that it has shown the offer for that origin.

Lune’s macOS input enables Chromium’s
`BrowserInitiatedAutomaticPictureInPicture` feature by default. The existing
`chrome://flags/#browser-initiated-automatic-picture-in-picture` flag can turn it off. Site handlers, permission decisions, tab
activation, and window lifetime use Chromium’s existing implementation.
Lune’s build has Safe Browsing disabled and Chromium uses its build-time
fallback for the URL reputation check. Lune also excludes Chromium’s
preloaded engagement scores. The separate window-occlusion flag retains its
disabled default.

## Validation

See the [implementation evidence](../builds/2026-11-19-automatic-picture-in-picture.json)
for the source parity and browser checks.

See the [manual permission offer validation](../builds/2026-11-20-manual-pip-auto-permission.json)
for the signed input, paired builds, and YouTube checks.

See the [idle controls validation](../builds/2026-11-21-pip-idle-controls.json)
for source parity, paired builds, and native pointer checks for [issue #55](https://github.com/leebyron/lune-browser/issues/55).

See the [glass controls validation](../builds/2026-11-23-pip-glass-controls.json)
for source parity, paired builds, native button and seek checks, and the
minimum-size layout.
