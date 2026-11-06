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
- CSS scroll timelines handle the story, with a JavaScript fallback when those
  timelines are unavailable. Reduced motion removes the launch bounce and zoom.
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

- `public/assets/lune-icon.svg` and `lune-mark.svg`: Lune's Pelagic Signal artwork
  from [`branding/lune.svg`](../branding/lune.svg), with the mark cropped out of
  the app-icon tile for the intro and final page.
- `public/assets/wallpaper.jpg`: the cyanotype-inspired artwork generated for
  this website's design exploration.
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
