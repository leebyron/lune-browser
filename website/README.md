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
- Interface surfaces are not text-selectable; headings, prose, attribution links,
  and the address field remain selectable. The sidebar has three pinned tabs and
  no divider above New tab. Light chrome uses the palette’s sage frame; dark chrome
  mixes the frame with 15% of its blue accent for a cooler contrast to the desktop.
- The illustrative shell mirrors the native edge-to-edge frame and sidebar-footer
  revisions reviewed on 2026-11-07: 16px outer corners, no content gutter, inner
  radius, outline or shadow. Only the outer window clips the page. A physical-pixel
  semantic hairline separates the pinned sidebar from content.
- Pinned and floating sidebars have identical 200px widths, flush top/bottom/left
  edges and square inner corners. Pinned mode shares the window material;
  floating mode uses a CSS approximation of native glass with semantic tab colors.
  Pinning changes the content width instantly without moving any sidebar/header
  controls. It does not tween page layout.
- The header is 52px tall: 36px controls and 8px vertical insets. The toggle has
  a 4px inner-edge inset. Glass groups leave a 12px gap beside either sidebar mode.
  Window controls use 14px circles at 23px center spacing in an 82×36px container,
  8px from the window edges. When the sidebar hides, navigation leaves 8px after
  that container. Its available width follows the sidebar’s 260ms slide.
- Tabs follow the native standard density: 30px heights, 8px corners, 2px row
  gaps, and 9px side margins (4px region inset plus 5px row margin). Icons have
  a 9px leading inset and a 7px gap before the label.
  Three filled pinned tiles use 6px spacing and
  a 6px gap before New Tab. New Tab stays above the independently scrolling tabs,
  with the same colors and spacing as a regular row and no tooltip.
- Sample tab close marks appear only on hover, including the selected tab. The
  32px close region holds an 11px glyph centered 15px from the trailing row edge.
  Labels yield space and fade before the close mark without changing row height.
  The illustration omits default-browser and update prompts.
- During “Just the page,” a scroll-driven cursor enters from the left of the
  screen, clicks the sidebar toggle and exits through the top. The page immediately
  fills the window, while the glass sidebar remains until the cursor is more than
  48px away. The sidebar then slides left over 260ms. Scrolling back reverses it.
  CSS scroll timelines own the cursor and layout state, with a JavaScript fallback.
- Windowed reveal bands are 8px at the top and left edges and consume no layout
  space. The sidebar’s full 52px header also reveals the toolbar. Revealed glass
  stays until the pointer is 48px away; the header retains the full window-width
  top strip. An input shield prevents clicks and wheel events reaching the page
  through visible header gaps. Keyboard focus retains controls; Escape dismisses.
- All header groups fade over 180ms without vertical movement. The fixed window
  controls remain while either sidebar or toolbar is visible, following the last
  surface to leave. Hovering their group reveals the sidebar and header. The
  address remains read-only and navigation/extension glyphs remain illustrative.
  The glass colors follow system appearance, not underlying page content.
- The site keeps Chlorophyll Daylight / Pelagic Signal colors and monochrome
  window controls. At 700px or less, the complete browser renders at half scale.
  It requests a fixed viewport scale and vertical touch panning; browsers may
  override zoom restrictions for accessibility. Reduced Motion removes cursor,
  launch bounce and sidebar translation.
- Native OS menus, window dragging/resizing, fullscreen menu-bar offsets and the
  Command-T palette are not simulated by this marketing illustration. The actual
  browser’s remaining glass/toolbar issues stay tracked in its own threads.
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
  The prepared download buttons and explicit choices use permanent GitHub
  `releases/latest/download/Lune-macos-ARCH.dmg` URLs. This revision must not be
  deployed until both aliases resolve to the accepted production release. The
  stable feed redirects likewise require verified GitHub targets; historical
  staging XML remains unchanged.

## Assets and attribution

All runtime assets are served locally; no font or icon CDN requests are needed.

- `public/assets/lune-icon.svg`, `lune-mark.svg`, and `favicon.svg`: adaptive
  light/dark artwork generated from [`branding/palettes.json`](../branding/palettes.json),
  with the approved 30% wider lunes. The mark omits the app tile.
- `public/assets/wallpaper-light.jpg` and `wallpaper-dark.jpg`: finished local
  cyanotype color treatments shared with onboarding. Light uses blue specimens on
  pale paper; dark uses light specimens on deep blue. No runtime blend, tint, or
  wash is applied. Their sampled 64x64 center colors are #F1F6F2 and #012034.
  The original `wallpaper.jpg` remains as the source/reference artwork.
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

## Privacy and security draft

The story runs Private, Secure, then Minimal. Short, staggered notes and original
SVG diagrams replace the two-column lists. Privacy highlights ungoogled-chromium
and uBlock Origin, with Helium credited for its integration. Security focuses on
HTTPS and site isolation. The closing attribution retains both upstream projects.
Its sources:

- [Helium](https://helium.computer/): HTTPS, ad/tracker/cookie-banner blocking,
  third-party-cookie defaults, and fingerprinting resistance.
- [Helium source overview](https://github.com/imputnet/helium): bundled uBlock
  Origin, open browser components and services, ungoogled-chromium ancestry.
- [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium):
  removal of Google web-service dependencies and their background requests.
- [uBlock Origin](https://github.com/gorhill/uBlock): content filtering.
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

The light variant uses the owner-requested softer blue specimens, approximately
half the initial contrast against the pale paper, baked into the JPEG.

Latest owner-approved light refinement: near-white paper with a small contrast
increase from the palest draft (requested +20%). The final sampled center is
#F1F6F2. Dark remains #012034. Website root/body/stage and setup root/body/main
all match their respective asset center. Built-in image generation prompt: keep
the near-white background unchanged and gently deepen only the pale blue
cyanotype specimens by approximately 20%, preserving all composition and detail.

Website prose and calls to action match the setup welcome page: regular Inter
15px/24px body copy, regular 16px/20px pill buttons, teal/cyan primary fill,
and the outlined ghost secondary action. Headings and native browser-demo
controls retain their existing typography.

The Dock uses light/dark PNG exports from the same Apple-compiled app icons as
the browser, including the enlarged mark and native tile edge. These are copied
by `render-app-icons.py`; no extra CSS glass frame is painted over the Lune icon.

## Release download links

The download chooser uses GitHub latest-release aliases Lune-macos-arm64.dmg
and Lune-macos-x86_64.dmg. Explicit architecture hints select the matching link;
otherwise both remain available. Keep these names identical across stable
releases so website redeployment is unnecessary for each new browser version.
Canonical feeds live under `lune-browser/main/updates/stable/mac/`; legacy
website redirects and historical staging feed files are removed.
Deploy these enabled links only after both latest assets and stable feeds pass
public readback. See [release delivery](../agent-docs/project/release-delivery.md).

The website GitHub link points to `leebyron/lune-browser` for browser releases.
Source is public in `leebyron/lune-browser` at exact release and component tags.
Browser releases upload DMGs, appcasts, checksums and compact metadata; do not
re-upload Git bundles or unchanged source/dependency archives. See the delivery
runbook for source reachability and paired-feed promotion checks.
