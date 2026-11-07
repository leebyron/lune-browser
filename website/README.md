# Lune website

Buildless HTML, CSS, and JavaScript served by Cloudflare Workers Static Assets.
Edit `public/index.html`, `public/styles.css`, and `public/main.js` directly.
There is no conversation-preview runtime or client-side framework dependency.

From this directory, `npm run dev` starts the local site and `npm run check`
validates the deployment. Pushes to `main` deploy through the existing Website
workflow. See [the deployment runbook](../agent-docs/project/website.md).

## Behavior

- The desktop fills the viewport. The browser window is at most 720px tall and
  twice as wide as its height, centered in the desktop space above the Dock.
- Launch starts after 96px of scrolling. Clicking the chevron or Lune Dock icon
  stops at 180px, where the intro has fully faded. Inner reading starts at 182px,
  which also bypasses any remaining launch delay and fade for fast scrolling.
- Normal launches bounce for 660ms; the window and running dot appear at 320ms.
  The tooltip shares the icon's bounce. Returning to the top resets the launch.
- CSS scroll timelines handle one continuous story, with a JavaScript fallback
  when those timelines are unavailable. Sections have natural heights and share
  one background; there are no fixed-height slides or alternating panels. A
  ResizeObserver measures the content to set the scroll distance and reading
  indicator, including after fonts load or the viewport changes. Reduced motion
  removes the launch bounce and zoom.
- The browser shell follows the [mounted-left Figma design](https://www.figma.com/design/I39uQunZpu6LsS7mDjcGSh/Untitled?node-id=14-50):
  200px sidebar, compact system-font tabs/favorites, a 4px inset content pane,
  and floating glass toolbar groups. The site follows system appearance with
  Chlorophyll Daylight and Pelagic Signal palettes and monochrome window controls. At widths of 700px or less, the complete browser UI renders at half scale,
  preserving its sidebar, navigation and trailing controls. The page requests a
  fixed viewport scale and restricts touch gestures to vertical panning; browsers
  may still override viewport zoom restrictions for accessibility.
- During “Just the page,” the sidebar starts pinned. A scroll-driven cursor
  enters from the screen’s left edge, curves into the header’s right-side toggle,
  and clicks to unpin it. The toggle is a bare glyph, including on hover. The content
  snaps to full width behind the still-visible floating panel; the cursor then
  follows a second curve out through the screen’s top edge. The cursor renders
  on the desktop so the window does not clip its entrance or exit. Once it is more than 48px beyond
  the panel, the panel slides off the left
  edge (260ms, eased translation without a fade). Scrolling back restores the
  floating panel, then the pinned layout. CSS scroll timelines animate the
  cursor and registered `--sidebar-fold` property; JavaScript coordinates the
  pinned/floating/hidden states and supplies the scroll-timeline fallback.
- Hovering the 4px left rail reveals the floating sidebar without resizing the
  content. It stays open until the pointer is more than 48px from the panel's
  outer rectangle (Euclidean distance, including corners), then slides away.
  The floating surface is inset 8px from the window on its top, bottom,
  and left, placing it 4px inside the content pane. Floating tabs and favorites have 8px inner margins; the mounted
  panel reduces its horizontal padding to 4px, producing an effective 8px
  margin from the window edge and content pane. The mount toggle sits at the header’s right edge and follows the panel
  padding. Pinned tabs and the tab list keep identical vertical coordinates
  when pinning changes; only horizontal margins shift. A “New tab” row sits
  below the pinned tabs and above the regular tabs. Window controls live directly in the window, outside the
  sliding sidebar and all glass groups, with a fixed resting position. They stay
  visible while either the sidebar or glass toolbar is visible; when both hide,
  they follow the last panel to leave and become inert: horizontally with the
  sidebar (260ms), or with the toolbar’s 180ms fade. When both are hidden,
  the first panel revealed determines their entrance direction. The top rail
  reveals both together, and hovering or focusing the controls keeps them open.
  The illustrated cursor clicks the mounted toggle position. The floating radius is 18px,
  concentric with the 26px window radius across its 8px inset.
  The rail also supports keyboard focus and tapping; Escape or tapping content
  dismisses it. The toggle pins/unpins the panel; subsequent scrolling resumes
  the illustrated sequence. Reduced motion omits cursor and slide animations.
  This is an Arc-style interaction approximation, not a claim to reproduce its
  private animation constants; [Arc documents the sidebar toggle](https://start.arc.net/find-focus).
- The glass address toolbar starts hidden. A 4px top rail or the first 44px of either
  visible sidebar reveals it. Once open, the entire window-width header strip
  retains it until the pointer moves more than 48px below the glass;
  there is no timer. Glass groups sit 8px from the top and right window edges
  and 12px beyond the floating sidebar. With the sidebar mounted, the navigation
  group sits 4px inside the content pane and uses a concentric 18px radius. Their width reserves space for either a pinned or visible
  floating sidebar, independently of the content pane. Its available width
  animates with the sidebar using the same 260ms easing in both directions,
  keeping a gap between the panels throughout the slide. A hidden sidebar still leaves room for the fixed
  window controls. Reenter the rail to reveal it again. Keyboard focus holds it open,
  the rail supports tapping, and Escape/outside taps dismiss it. Closing the
  illustrated app, changing tabs, or deactivating the browser resets it.
- All three header glass groups fade in and out together over 180ms, with no
  vertical movement, matching the native build. The old slide/fade query-string
  comparison is retired. Window controls still follow the sidebar horizontally
  when it is the first surface to enter or the last to leave. Hovering the window
  controls also reveals the collapsed sidebar and header. Reduced Motion removes
  sidebar translation. The address remains a read-only illustration.
- The pinned sidebar shares the painted window material. The detached popover
  uses translucent, blurred glass with a softer shadow and neutral selection/text
  colors, approximating the native NSGlassEffectView in CSS. Its inset is 8px;
  the bare 36×36px toggle has a 4px trailing inset when pinned and 2px when floating.
  The toggle center stays at y=26px; tab rows retain their vertical positions.
  Navigation is 76×36px, all glass groups are 36px tall, and the address is centered
  in the available space between navigation and trailing controls (maximum 480px).
  These dimensions and interactions were checked against the browser build thread
  and its native source on 2026-11-06; CSS glass is an approximation of AppKit.
- Mounting/unmounting snaps the content pane width at the click, without a layout
  tween. The content pane has a 22px radius, concentric with the 26px
  outer window across its 4px inset. Native Safari and Photos
  windows informed the larger radius and inset top row; these are CSS
  approximations of AppKit geometry. The window uses a non-layout inset hairline and a soft shadow; the content pane
  shadow is horizontally symmetric, offset 1px downward with a 4px blur and
  restrained opacity in each appearance.
- The content keeps a stable reading width while the pane expands, preventing
  text reflow from moving the animation's scroll boundaries.
- Close and minimize return to the desktop. The third control uses the browser's
  Fullscreen API, when available. Window controls have monochrome styling and
  reveal their glyphs on group hover or keyboard focus.
- Screenshot and feature captures remain placeholders. Both Download buttons
  select the matching build when macOS User-Agent Client Hints report `arm` or
  `x86`. Unsupported, denied, or unknown hints (and other platforms) retain a
  native popover with explicit Apple silicon and Intel choices. Legacy
  `MacIntel`/user-agent strings are not used to infer chip architecture.
  Downloads remain disabled and labeled Coming soon until validated public
  releases are available. When publishing, link both the detected build button
  (`data-architecture="arm64"` or `"x86_64"`) and the explicit choice buttons to
  the corresponding release; never link to an unvalidated development build.

## Assets and attribution

All runtime assets are served locally; no font or icon CDN requests are needed.

- `public/assets/lune-icon.svg`, `lune-mark.svg`, and `favicon.svg`: adaptive
  light/dark artwork generated from [`branding/palettes.json`](../branding/palettes.json),
  with the approved 30% wider lunes. The mark omits the app tile.
- `public/assets/wallpaper.jpg`: the cyanotype-inspired artwork generated for
  this website's design exploration. Light mode uses a quieter luminosity treatment.
- The PNG, ICO and Apple touch fallbacks use the dark tile. All logo assets are
  regenerated by `python3 scripts/branding/render-assets.py` on macOS.
- `public/assets/favicons/`: the same Gmail, Google Calendar, YouTube, Reddit,
  Wikipedia, and Google icons used in the Figma sidebar, copied from the local
  design-source assets. These belong to their respective sites; they illustrate
  sample tabs and are served locally, with no runtime third-party requests.
- Finder and Trash images: macOS system artwork, used in the illustrative Dock.
  Apple retains ownership; these are not Lune artwork or relicensed by this repo.
- Syne 800 and Inter 400/500: Latin WOFF2 subsets from Google Fonts, Syne v24 and
  Inter v20. SIL Open Font License notices are in `public/licenses/`.
- Inline interface icons: Lucide (download, arrow-up-right, chevron-down,
  panel-left, maximize, shield). Its ISC/MIT notices are in
  `public/licenses/lucide.txt`.
- Window glyph proportions were checked against [Apple's macOS reference](https://support.apple.com/guide/macbook-pro/are-you-new-to-mac-apd7ae4404d0/mac).
  They are CSS approximations, not native AppKit controls.

The final page credits and links Helium and ungoogled-chromium, followed by the
Lune author credit. Preserve that attribution when replacing the placeholder
feature content or changing the story length.

## Security and privacy draft

The in-window copy credits both upstream projects in each section. Its sources:

- [Helium](https://helium.computer/): HTTPS, ad/tracker/cookie-banner blocking,
  third-party-cookie defaults, and fingerprinting resistance.
- [Helium source overview](https://github.com/imputnet/helium): bundled uBlock
  Origin, open browser components and services, ungoogled-chromium ancestry.
- [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium):
  removal of Google web-service dependencies and their background requests.
- [Chromium Site Isolation](https://www.chromium.org/Home/chromium-security/site-isolation/):
  sandbox and process isolation, described as defenses rather than guarantees.

Reviewed 2026-11-06. Lune's pinned `inputs/chromium-158-1/helium` includes the
uBlock integration, default-enabled Helium Noise, and third-party-cookie blocking
in `patches/inox-patchset/modify-default-prefs.patch`. This is source review and
upstream documentation, not a new runtime security audit. The draft makes no
claim of complete anonymity, Google Safe Browsing (removed upstream), automatic
Lune updates, or a validated public release. Review shipped defaults and service
behavior again before publishing browser downloads.

The sidebar revision was checked against the current Figma desktop canvas and
its existing source assets on 2026-11-06. The Figma MCP connector was unavailable
at its Starter-plan call limit, so generated design context could not be used.
The window remains an illustrative HTML/CSS composition, not an app screenshot.
