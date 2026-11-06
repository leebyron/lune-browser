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
  200px sidebar, compact system-font tabs/favorites, an 8px inset content pane,
  and floating glass toolbar groups. The site follows system appearance with
  Chlorophyll Daylight and Pelagic Signal palettes and monochrome window controls. Below 540px, the sidebar floats over the content.
- During “Just the page,” the sidebar starts pinned. A scroll-driven cursor
  follows a cubic path into its toggle and clicks to unpin it. The content
  expands behind the still-visible floating panel; the cursor then follows a
  second curve out of the window. As it leaves, the panel slides off the left
  edge (260ms, eased translation without a fade). Scrolling back restores the
  floating panel, then the pinned layout. CSS scroll timelines animate the
  cursor and registered `--sidebar-fold` property; JavaScript coordinates the
  pinned/floating/hidden states and supplies the scroll-timeline fallback.
- Hovering the 8px left rail reveals the floating sidebar without resizing the
  content. It stays open across the rail and panel, then slides away on exit.
  The rail also supports keyboard focus and tapping; Escape or tapping content
  dismisses it. The toggle pins/unpins the panel; subsequent scrolling resumes
  the illustrated sequence. Reduced motion omits cursor and slide animations.
  This is an Arc-style interaction approximation, not a claim to reproduce its
  private animation constants; [Arc documents the sidebar toggle](https://start.arc.net/find-focus).
- The glass address toolbar starts hidden. An 8px top rail reveals it; the full
  58px top area, including gaps and all three capsules, holds it open. Leaving
  starts a 700ms one-shot timer; reentry cancels it. Keyboard focus holds it open,
  the rail supports tapping, and Escape/outside taps dismiss it. Closing the
  illustrated app, changing tabs, or deactivating the browser resets it.
- The default toolbar motion slides down from above in 220ms and back up in
  180ms, with a subtle 120ms fade and no bounce. `?toolbar=fade` uses only a
  120ms fade; `?toolbar=slide` explicitly selects the default. Reduced Motion
  removes translation. Both variants interrupt/reverse immediately on reentry.
  These timings are our choices informed by [Apple's motion HIG](https://developer.apple.com/design/human-interface-guidelines/motion),
  which calls for brief, precise, interruptible motion and consistent entry/exit
  directions, not a prescribed toolbar duration. The rail/cooldown and centered
  480×36px address capsule follow the native browser prototype; the address is a
  read-only illustration, while navigation/extension glyphs remain decorative.
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
