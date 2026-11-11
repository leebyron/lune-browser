# Lune website

Buildless HTML, CSS, and JavaScript served by Cloudflare Workers Static Assets.
Edit `public/index.html`, `public/styles.css`, and `public/main.js` directly.
There is no conversation-preview runtime or client-side framework dependency.

From this directory, `npm run dev` starts the local site and `npm run check`
validates the deployment. Pushes to `main` deploy through the existing Website
workflow. See [the deployment runbook](../agent-docs/project/website.md).

## Behavior

- The desktop fills the viewport. The browser window is at most 720px tall and
  at most 10/6 as wide as its height, centered in the desktop space above the Dock.
- Launch starts after 96px of scrolling. Clicking the chevron or Lune Dock icon
  stops at 180px, where the intro has fully faded. Inner reading starts at 180px,
  which also bypasses any remaining launch delay and fade for fast scrolling.
- The personal note and ten botanical paragraphs use locally served Rock Salt
  at 16px/32px. The note has two separate paragraphs: “I made Lune for myself”
  and “I wanted a browser that stayed out of my way”. The second begins
  1200ms after the first, leaving a 400ms pause after the first 800ms wipe.
- The flower begins the owner's ten-line sequence: Chromium, removed Google
  services, extension proxying, uBlock Origin, Mac details, the command menu,
  Helium's !bangs, the disappearing toolbar, vertical tabs and open source.
  Named projects link to their official sites or repositories; !bangs links to
  Helium's directory. Only handwritten links use the sketched SVG underline,
  in the text's full ink color: an upward arc thickens toward a dot on the
  right. Hover or keyboard focus redraws it with a 600ms left-to-right clip
  wipe; Reduced Motion keeps it still. Footer and other normal text retain
  regular link underlines.
  The command-menu line spells the shortcut as Cmd-T.
  The cursor holds at one-third of the window's top edge for the toolbar
  line, then demonstrates the sidebar during the vertical-tab line.
- Reading copy lifts by 6px and fades in over 600ms, with a gentler 800ms
  feathered left-to-right wipe using ease-in-out timing. It fades out over
  200ms. Scroll selects
  the target state, and transitions finish even when scrolling stops. Point copy
  enters at 85% of the browser viewport and stays visible above that threshold,
  including past the top edge. Scrolling back below the lower threshold fades it
  out. The personal note triggers when its first line's resting center reaches
  68% of the browser viewport, while the logo is still opening. Reversing below
  the threshold cancels the stagger immediately. Reduced Motion shows settled, fully unmasked text.
  The earlier 85% trigger advances each point by 10% of the browser viewport
  (72px in the 720px desktop window). Local inspection confirms the flower
  copy is visible at an 81.8% resting-center position, before the former 75%
  threshold. The text transition timings remain unchanged.
- The inner logo starts at 70% of the pane height and opens over 65% of a
  viewport of scrolling (previously 50% and 22%). The note stays 128px below
  the logo center. The prelude spans 1.28 viewports, followed by 168px before
  the flower section, adding 40px of breathing room before the flower.
- Both Lune wordmarks use Syne 800. The opening title has an explicit 40px
  fallback so removing a size variable cannot invalidate its font shorthand.
- The Cmd-T sentence opens a passive glass-menu illustration when its center
  reaches 70% of the pane, after the prose reveal begins. It starts as a 52px
  empty input without open-tab options. The following !bangs sentence triggers
  `!wiki` typing when its center also reaches 70% of the pane; elapsed time
  finishes the sequence at rest, while scroll
  progress can advance it to keep up with faster reading. The website intentionally
  shows no autocomplete results, during typing or after applying the scope.
  At completion, the query becomes the Wikipedia provider pill followed by the
  placeholder “Search Wikipedia”. The pane remains 52px tall throughout.
  It holds until a separate, later scroll threshold, then fades away at its
  current height. Dismissal begins at least 20% of a pane after completion and
  at least 8% of a pane after the cursor journey starts,
  before the cursor arrives at its header hold. Scrolling back restores the
  pill; returning above the bang sentence resets typing to an empty menu.
  Reduced Motion hides this illustration. It takes no focus or input and makes
  no search, suggestion, or navigation requests.
- Cmd-T geometry follows the native implementation: 600px maximum width,
  36px minimum side margins, 18px panel corners, 52px input height, and a
  28px provider pill in 13px medium system type. Its top
  stays anchored against the native five-row maximum even with fewer rows.
  The supplemental shadow is exactly 5% black with 10px blur and a 3px downward
  offset, following the rounded silhouette. CSS approximates the native glass.
- The closing brand group uses a 57.6px logo, 40px wordmark and 12px gap, with
  36px of vertical space above the download actions.
  The coda adds 6⅔% of a pane of scrolling below the ground, increasing the
  root-to-logo gap while keeping the brand/actions centered in the final pane.
  The soil extends through the full coda; the thanks and byline retain their
  positions relative to the actions and bottom edge. Dark roots use the stem
  ink mixed 15% toward the soil color, making them slightly darker than the
  stem. Light roots retain the stem ink. Both reveal layers share this color.
- Normal launches bounce for 660ms; the window and running dot appear at 320ms.
  The tooltip shares the icon's bounce. Returning to the top resets the launch.
- CSS scroll timelines handle one continuous story, with a JavaScript fallback
  when those timelines are unavailable. Sections have natural heights and share
  a continuous background, darkening below the soil contour; there are no fixed-height slides or alternating panels. A
  ResizeObserver measures the content to set the scroll distance and reading
  indicator, including after fonts load or the viewport changes. Reduced motion
  removes the launch bounce and zoom.
- The inner page uses `assets/cotton-paper.jpg`, a generated scan-style cotton
  paper material blended over the page and soil colors. Dark uses `overlay`;
  Light uses `multiply` with brighter, higher-contrast fibers so they remain
  visible on the pale surface. It moves
  with the page. Adjust `--paper-texture-opacity` on
  `.pages::after` to change its strength (`.68` Dark, `.24` Light). Both appearances
  use a 768px square tile for finer fibers. It ignores pointer events.
  In Dark, the existing `overlay` texture blends above the `#FFFFFF98` reading
  copy as well as the page, giving the letters the same paper surface.
  Light keeps the texture beneath its softer cyanotype-blue `#315E73` copy.
  Text reveal animations remain independent.
  Generated with the built-in image tool using the prompt: "Flatbed-scan style
  neutral midgray cotton rag drawing paper, fine interwoven cellulose fibers,
  uniform diffuse illumination, seamless edges, no text, folds, pits or blotches."
- Stamens use sun-yellow tips and halos in Light and vivid button-like teal in
  Dark. Light uses `color(display-p3 .929206 .81535 0)`: the existing `#EBD039`
  hue and OKLCH lightness, with chroma increased from 0.16134 to 0.20499 at
  the P3 gamut boundary. The original yellow remains the sRGB fallback.
  Dark uses `color(display-p3 0 1 .9)` with an sRGB teal fallback. The filaments use a quieter matching teal.
  Seventeen seeded mote groups, including two close pairs and three singles anchored 48px, 72px and 96px up the stem from the root crown, follow measured points along the stem, sharing the tips'
  color and small-area glow. Each companion has its own slightly smaller float path, reverse traversal, shifted phase, different speed and origin offset by about 23px, while sharing its partner's scroll anchor. Usually two or three groups are visible at once. Inner
  groups trace wide, shallow 26–42 second figure eights; outer groups spread outward with
  cubic scroll progress, starting gently near the lower edge and accelerating
  toward the top. Scroll reversal restores their proximity to the stem. Only
  visible motes run their idle animation; Reduced Motion keeps them stationary
  relative to their stem anchors. Layout remeasurement preserves their idle phase.
- Interface surfaces are not text-selectable; headings, prose and attribution
  links remain selectable. The address is static text with an arrow cursor,
  no focus target and no focus outline. The sidebar has two pinned tabs and
  no divider above New tab. Chrome uses the accepted #E7EDE3 Light / #10354F Dark mounted palette.
  Selected tabs use #D6E1D2 / #2A4C62 for directional contrast.
  The GitHub rows read `lune-browser` and `ungoogled-chromium`.
- The illustrative shell mirrors the native edge-to-edge frame and sidebar-footer
  revisions reviewed on 2026-11-07: 16px outer corners, no content gutter, inner
  radius, outline or shadow. Only the outer window clips the page. A physical-pixel
  semantic hairline separates the pinned sidebar from content.
- Pinned and floating sidebars have identical 216px widths, flush top/bottom/left
  edges and square inner corners. Pinned mode shares the window material;
  floating mode approximates the accepted themed glass: a lighter Light tone and darker Dark tone, with theme selection and hover colors.
  Its right edge has a physical-pixel glass rim: white at 60% in Light and
  black at 20% in Dark, approximating the native material's contrasting edge.
  The edge overlays the pane without changing its width or catching pointer input.
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
  Two filled pinned tiles use 6px spacing and
  a 6px gap before New Tab. New Tab stays above the independently scrolling tabs,
  with the same colors and spacing as a regular row and no tooltip.
- Sample tab close marks appear only on hover, including the selected tab. The
  32px close region stays inside the row and holds an 11px glyph centered 16px
  from its trailing edge. The tab list scrolls vertically only.
  Hovering the close button adds an immediate 20px square contrast fill with
  4px corners and 16% opacity (14% while pressed), matching the app; the glyph
  retains the tab's foreground color. Keyboard focus also reveals the close
  control; touch layouts keep it hidden unless the row is hovered.
  Labels yield space and fade before the close mark without changing row height.
  The illustration omits default-browser and update prompts.
- Tab rows use the regular arrow cursor. Clicking the current Lune tab does
  nothing. Each regular tab has a separate accessible close button; other tab
  titles remain links. Closing Lune instantly returns to the desktop at scroll
  position zero and keeps its row in place. Other closed rows stay removed until
  reload. Close controls never follow the tab's link.
- During the toolbar sentence, the scroll-driven cursor enters from the left,
  pauses at the top edge one-third of the way across the window, and exposes
  the header. It holds steady, then moves to the sidebar toggle and clicks as
  the vertical-tab sentence reaches the same reading height (58% of the pane).
  The page fills the window on click; the floating sidebar and header remain
  until the cursor tip crosses the window edge, then begin retracting together
  without a distance buffer. The sidebar slides left over 260ms and the header
  fades over 180ms. Scrolling backward reverses the demonstration.
  Numeric JavaScript transforms position the cursor and click ring on every screen size; CSS scroll timelines drive layout where available, with a JavaScript fallback.
  Its black arrow, white outline and compact shadow approximate the macOS pointer;
  its existing tip/hotspot coordinates remain fixed for the toggle click.
  On mobile the pointer and click ring are visible at the browser’s half scale.
  Scroll-positioned transforms move the pointer continuously, pause on the
  header and toggle and show the click. Both panels retract when the simulated
  pointer leaves the window. Actual mouse interactions retain the established
  48px dismissal boundary. Reduced Motion hides the demonstration.
- Windowed reveal bands are 8px at the top and left edges and consume no layout
  space. The sidebar’s full 52px header also reveals the toolbar. Revealed glass
  stays until the pointer is 48px away; the header retains the full window-width
  top strip. An input shield prevents clicks through visible header gaps. Wheel input over
  the header scrolls the story, matching the accepted native forwarding behavior. Keyboard focus retains controls; Escape dismisses.
- All header groups fade over 180ms without vertical movement. The fixed window
  controls remain while either sidebar or toolbar is visible, following the last
  surface to leave. Hovering their group reveals the sidebar and header. The
  address remains read-only and navigation glyphs remain illustrative; the two
  extension icons link to their sites.
  CSS glass follows system appearance; it does not reproduce AppKit’s content-aware compositor.
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
- The emulated browser is the visual demonstration; there is no screenshot
  placeholder or separate feature illustration. Both Download buttons
  select the matching build when macOS User-Agent Client Hints report `arm` or
  `x86`. Windows, iOS/iPadOS, Android, Linux and ChromeOS identities disable and
  dim both buttons, including iPads using a desktop Mac identity. Unknown
  platforms and unsupported, denied or unknown architecture hints retain a
  native popover with explicit Apple silicon and Intel choices. Legacy
  `MacIntel`/user-agent strings are not used to infer chip architecture.
  The download buttons and explicit choices use permanent GitHub
  `releases/latest/download/Lune-macos-ARCH.dmg` URLs. Both aliases resolve to the
  accepted production release; feeds are served from the canonical repository.

## Assets and attribution

Original website code and assets are licensed under [GNU GPLv3 or later](../LICENSE)
(`GPL-3.0-or-later`), except where otherwise noted. See [NOTICE](../NOTICE) for scope.
The website serves the full license at [`/licenses/gpl-3.0.txt`](public/licenses/gpl-3.0.txt)
for direct access. Keep that copy identical to the root
`LICENSE`. The third-party assets below retain their existing licenses and notices.

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
- `public/assets/favicons/`: official Lee Byron, Helium and GitHub icons, served
  locally. The earlier Fastmail favicon remains unused.
  Legacy design-source icons remain unused. Icons belong to their respective
  sites and illustrate the preview tabs.
- `public/assets/fastmail-mail.svg` and `fastmail-calendar.svg`: the simplified
  `i-app-mail` and `i-app-calendar` path geometry from the app switcher on
  <https://www.fastmail.com/>, using its inactive primary/secondary gray fills
  (`#848B91` / `#ADB1B5`) with CSS grayscale. Fastmail retains ownership; these
  are not Lune artwork or relicensed by this repository. Both pins link to the
  public Fastmail homepage, rather than private app routes.
- Finder and Trash images: macOS system artwork, used in the illustrative Dock.
  Apple retains ownership; these are not Lune artwork or relicensed by this repo.
- Syne 800 and Inter 400/500: Latin WOFF2 subsets from Google Fonts, Syne v24 and
  Inter v20. SIL Open Font License notices are in `public/licenses/`.
- Rock Salt 400: Google Fonts v24 TrueType, served locally as
  `public/assets/fonts/rock-salt.ttf`; Apache 2.0 license in
  `public/licenses/rock-salt.txt`.
- `public/assets/ublock-origin.png`: unchanged 32px uBlock Origin toolbar artwork
  from the prepared browser’s `third_party/ublock/img/icon_32.png`. Copyright
  Raymond Hill and contributors; GPLv3 notice in `public/licenses/ublock-origin.txt`.
- `public/assets/onepassword.svg`: official 1Password favicon from
  <https://1password.com/favicon/icon-v2.svg>, used as illustrative extension
  artwork; the brand belongs to 1Password.
- `public/assets/browser-symbols.svg`: Apple SF Symbols Medium vector outlines
  from SF Symbols 7's installed `SFSymbolsFallback.otf`, matched to the app's
  named symbols and AppKit image proportions. The sprite contains `sidebar.left`,
  `chevron.backward` (mirrored for Forward), `slider.horizontal.below.rectangle`,
  `arrow.clockwise`, `puzzlepiece.extension`, `plus`, and `xmark`.
  Browser controls use the app's 16pt configuration, Site Information and Reload
  use 14pt, and tab closes use 11pt. Square Views icon slots retain the app's
  proportional fit, including the 20px Extensions icon slot; native header
  symbols retain their wider intrinsic sizes.
  Apple retains ownership; this artwork depicts Lune's macOS interface and is
  not Lune artwork or relicensed by this repository.
- Remaining inline interface icons: Lucide (download, arrow-up-right,
  chevron-down). Its ISC/MIT notices are in `public/licenses/lucide.txt`.
- Window glyph proportions were checked against [Apple's macOS reference](https://support.apple.com/guide/macbook-pro/are-you-new-to-mac-apd7ae4404d0/mac).
  They are CSS approximations, not native AppKit controls.

The final page thanks and links Helium and ungoogled-chromium in regular Inter
14px/22px. The Lune mark and download actions form a group centered in the
final viewport; the credit to both projects’ authors and contributors is centered
in the gap between the actions and the author byline. The Lode author credit, “Made with [coffee] in SF
by Lee Byron,” uses the original inline cup paths from
<https://leebyron.com/lode/> and sits 18px above the final browser-content edge,
with at least 72px separating it from the coda. Preserve this credit when
changing the story length.

## Respect story

The tagline is “A respectful browser for the Mac”. Ten short sentences cover
Chromium, removed Google services, extension proxying, blocking, Mac details,
Cmd-T, Helium's !bangs, the toolbar, vertical tabs and shared source.
The opening reuses setup’s paired-circle logo reveal, driven by scroll
rather than a timer. The mark starts at the content viewport’s vertical center
and moves upward with the page. Two personal-note paragraphs sit below it in
Rock Salt 16px/32px, matching the botanical copy. A 1.08-viewport prelude and
128px section gap keep the first flower offscreen when the browser opens.
The opening point has only a flower, enlarged 50%; nine generated leaves mark
later points. A branching cyanotype vine joins them with small shoots and
curled tendrils. Prose shares one foreground color. At 700px or less, the complete
browser and its content share the same 50% transform: handwritten prose renders
at 8px/16px.
There is no mobile-only enlargement of the text, coda, buttons or author credit.
The window fixes text-size adjustment at 100% so mobile text autosizing does not
diverge from the chrome. This does not assert physical Safari-device validation.
Syne remains confined to the Lune wordmarks.

Each row retains its overall maximum measure and an 80px specimen box. Its
text gap now follows the seeded specimen's ink bounds, targeting 44px of optical
clearance instead of spacing from the transparent SVG box. The opening flower
uses a 40px layout gap because it is still unfolding at its reading position.
The copy is vertically centered beside the leaf or
leaf body, 10px above the row center; the first sentence rises 22px to align
with its larger flower. The complete row starts horizontally
centered, then follows x = column center + A sin(2πi / (n − 1)). A is at most
48px and shrinks to the available room; 32px is reserved so even narrow layouts
retain a small wave. The browser cursor unpins the sidebar during the vertical-tab
sentence. The coda thanks the authors and contributors behind Helium and
ungoogled-chromium. Its preceding gap is 24px, keeping the ground close to the
last point. See the [copy rationale and evidence](../agent-docs/project/website-respect-story.md).

The sidebar pins Fastmail and its Calendar, both linking to the Fastmail homepage.
Regular tabs show Lune, its GitHub project, Helium, ungoogled-chromium and Lee Byron,
with the author’s website last. The current Lune row is a selection button without a click action;
other titles and New tab open their destinations in separate tabs with
`noopener noreferrer`. Each regular row has an independent close button.
No iframe, proxy, external
page fetch or private-mail content is loaded in the illustration. The top-right
trailing group shows only Extensions, uBlock Origin and 1Password. The uBlock
Origin and 1Password icons are accessible links to their project/site, opening
separate tabs with the same safe anchor attributes.

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

The current story’s claim-by-claim evidence and limits are documented in the
[respect-story notes](../agent-docs/project/website-respect-story.md). The frozen
release and development lock establish inclusion; this is not a new runtime
security audit. No anonymity or infallible-protection claim is made. Optional
Helium services retain their independent consent in the real browser.

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

Website prose uses the simplified respect-story typography described above.
Calls to action retain regular Inter 16px/20px pill buttons, teal/cyan primary
fill and the outlined ghost secondary action. Native browser-demo controls
retain their existing typography.

The Dock uses light/dark PNG exports from the same Apple-compiled app icons as
the browser, including the enlarged mark and native tile edge. These are copied
by `render-app-icons.py`; no extra CSS glass frame is painted over the Lune icon.

## Release download links

The download chooser uses GitHub latest-release aliases Lune-macos-arm64.dmg
and Lune-macos-x86_64.dmg. Explicit macOS architecture hints select the matching link;
otherwise both remain available unless the device is known to use an unsupported platform. Keep these names identical across stable
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

## November 10 browser-polish audit

Compared the existing illustration with the current development lock and frozen
26.1110.1 source, using the feature records below. These are website changes;
they do not change browser patches or constitute native runtime validation.

The subsequent icon alignment uses actual SF Symbol SVG outlines in place of
the hand-drawn substitutes. Local Light/Dark desktop and 390×844 phone previews,
sidebar pin/unpin, hover-close rendering, SVG references, cache keys, JavaScript
syntax, deployment dry run and whitespace checks pass. Browser inspection reports
no console warnings or errors. This revision remains local; native Safari and
physical iPhone rendering have not been independently checked.

| Recent browser work | Website treatment |
| --- | --- |
| [Themed sidebar](../agent-docs/project/features/themed-unpinned-sidebar.md) | 216px width; mounted palette; lighter Light / darker Dark detached tint; strong #D6E1D2 / #2A4C62 selection and themed hover fills. CSS blur remains an approximation. |
| [Toolbar polish](../agent-docs/project/features/trailing-toolbar-controls.md) | 72px navigation pill with 16px separator; Medium SF Symbol SVGs with native proportions; 14pt site-info/reload symbols in 32px slots; 4px site-info and 2px reload insets; neutral AppKit secondary-label, rollover and disabled colors; address cap at half the available header; 4px trailing padding and 2px gaps; no gap between Extensions and first extension; real uBlock and 1Password artwork. The latest owner revision limits this illustrative group to those three controls, omitting Profile, Downloads and More. |
| [Glass appearance](../agent-docs/project/features/chrome-appearance.md) | Diffuse 5% black / 10px / 3px header shadows, no extra sidebar shadow. CSS tint and foregrounds follow appearance; AppKit content adaptation is not emulated. |
| [Header scrolling](../agent-docs/project/features/header-scroll-through.md) | Removed the previous wheel-event blocker; native click shielding remains represented. |
| [Sidebar pin](../agent-docs/project/features/sidebar-pin-activation.md), [edge frame](../agent-docs/project/features/edge-to-edge-frame.md), [New Tab](../agent-docs/project/features/sidebar-new-tab.md), [footer](../agent-docs/project/features/sidebar-footer.md) | Retain accepted flush geometry, pin/reveal choreography, fixed New Tab and hover-only tab closes. The illustration continues to omit installation/update prompts. Native activation colors and OS window menus are not simulated. |
| [Menu retention](../agent-docs/project/features/menu-reveal-retention.md), [downloads](../agent-docs/project/features/downloads.md), [media](../agent-docs/project/features/media-toolbar-controls.md) | The trailing group shows idle artwork. Native menus, download progress/status and media sessions remain outside this illustration. The website’s real download chooser retains its own popover behavior. |
| [Command-T/results](../agent-docs/project/features/command-bar-corners.md), [suggestion selection](../agent-docs/project/features/address-suggestion-selection.md), [toolbar modes](../agent-docs/project/features/header-inset-prototype.md), [older macOS](../agent-docs/project/features/older-macos-appearance.md), [window close](../agent-docs/project/features/native-window-close.md) | The passive Cmd-T illustration opens empty, types !wiki without autocomplete results, applies the provider pill with a search placeholder, and dismisses at a later scroll point. Native geometry and supplemental shadow guide the CSS approximation. Settings, OS fallback and multi-window behavior remain outside the illustration. Website close/minimize return to its desktop; fullscreen uses the web API. |
| [Setup, fonts and icons](../agent-docs/project/features/onboarding-visual-refinements.md) | Accepted wallpaper JPEGs, Inter interface text/buttons and compiled Dock artwork are retained; story prose now uses Rock Salt. |

The emulated browser itself supplies the visual demonstration; screenshot placeholders are removed. Open default-browser and
resize-cursor issues are not represented as fixed. This audit tracks the scope of
the marketing illustration rather than adding every native feature to it.

Local validation on November 10: JavaScript syntax, Wrangler deployment dry run,
asset/cache-key checks, upstream-icon byte parity, documentation links and
whitespace checks pass. Browser inspection covers desktop Dark, a preview-only
Light appearance override, and a 390×844 narrow viewport. Header wheel scrolling,
sidebar pin/unpin, point bounds, plain Inter thanks, the 80px CTA gap and final
bottom-edge credit were checked. No browser console warnings or errors were
observed. The appearance override is a local preview-server fixture, not shipped
code. The latest revision replaces that attribution with one complete sentence and
unifies the story typography; it removes the screenshot and feature diagrams.
Tab anchors and official icon sources were checked against their intended destinations. Deployment and public readback follow the website runbook.

The simplified story and linked-tab refinement pass the same source/deployment
checks, plus desktop Dark and preview-only Light inspection and a 390×844 layout
check. All four story points share one computed font and color. The footer fits
without overflow, its mobile buttons render at their normal readable size, and
the author credit remains at the lower edge. Clicking Lee Byron opens the real
site in a separate browser tab; all seven sidebar links use the same native
anchor behavior. The two extension links use matching new-tab anchors. 1Password and GitHub artwork is used as a foreground-colored
mask for appearance contrast. No iframe or private Fastmail content is loaded.

## Cyanotype botanical illustration

The initial Rock Salt revision passes local desktop Light, a preview-only Dark fixture,
and 390×844 layout checks without horizontal text overflow. A forced fallback
sample records the first line at 60.7% wipe with the second still hidden; both
finish at 116% with full opacity while scrolling is stationary. Reversal resets
both lines. A forced Reduced Motion fixture shows all twelve text elements at
full opacity with no mask or transition. No console warnings or errors were
observed. Syntax, deployment dry run, asset/cache keys, documentation links and
whitespace checks pass. This revision remains local; physical Safari/iPhone
rendering has not been independently retested.

The subsequent timing refinement reduces the lift from 18px to 6px and slows
the wipe from 600ms to 800ms with ease-in-out timing. Local computed-style
inspection confirms 600ms fade/lift, 800ms wipe, and an 860ms second-line delay.

The following copy revision preserves all ten owner-supplied lines, with Cmd-T
spelled out, and reduces Rock Salt by 20% to 16px/32px. Its original local pen-underline
SVG used a shallow arc with changing ink thickness and a pointed right finish
at 50% opacity; the subsequent refinement below supersedes that treatment. Desktop and 390×844 checks find no horizontal text overflow;
project links use the sketch asset and retain their destinations. The sidebar
demonstration targets the vertical-tab line. Exact-copy, SVG, cache-key,
JavaScript syntax, whitespace and deployment dry-run checks pass, with no
preview console warnings or errors. This revision remains local.

Original vector artwork is generated from fixed seeds. Every main leaf and
small offshoot has its own length, width, lean, edge variation and vein pattern.
Leaves have narrow, pointed silhouettes with restrained edge variation. Each
petiole shares its leaf’s silhouette but uses the same flat ink as the main vine; the brighter gradient is confined to the blade. Small shoots
use measured branch tangents to align their leaves at the junction.
The petiole starts at the same exact stem junction regardless of shape; mirrored
leaves keep mirrored pivots. The vine reads each outer SVG’s rendered box relative
to the page, normalized by the actual scale, rather than assuming an offsetParent
chain. The outer SVG never transforms. An inner SVG group uses explicit numeric
rotation pivots, updated on scroll in both timeline modes, avoiding percentage
CSS transform origins on mobile SVG roots. A fixed small-area grain filter and shared cyanotype
ink colors keep the family coherent. Resize does not regenerate random designs.

The ground begins a slightly darker underground fill that continues through
the footer in both appearances, with no separate contour stroke. Its shape uses four octaves of one-dimensional Perlin gradient noise with
quintic interpolation, independently implemented after consulting [Ken Perlin’s
reference](https://cs.nyu.edu/~perlin/noise/). Broad rises, smaller bumps and fine
grading replace the repeating sine contour. The root junction remains 15% down
the final viewport. A taproot carries two uneven laterals below the crown,
with varying side branches and fine rootlets. A further order of short, tapered
rootlets fans from the fine branches: 135 total paths, including 89 terminal
rootlets, in the checked desktop and phone layouts. Noise steers their headings;
filled silhouettes taper all the way to a point. The spread is capped at 420px
and depth at 25% of the viewport (at most 180px). Two shared radial masks reveal the cached silhouettes: the base starts at 70% of the final radius and the light starts at zero, both expanding to full coverage.

The flower is 50% larger, faces upwards, and has 19 seeded, curved filaments
with varied anther positions and brightness. Stamens spread from a narrow bundle to a wide fan as the petals open. The
opaque front petal is painted after the stamens and covers their bases; only those tips use a small-area light blur. There
is no idle pulse or time-driven growth. Artwork is hidden from accessibility
APIs, takes no input, and adds no raster/network assets or dependencies.

Native scroll timelines own the logo, petal and root animations. Inner SVG
groups use numeric rotation attributes for leaf motion in both modes; the
existing scroll update also provides equivalent logo, flower and root progress
in the JavaScript fallback.
Reduced Motion shows the completed logo, open flower and grown roots without
motion. Layout measurements update the plant, terrain and footer credit on font
loading and resize. The credit’s center is halfway between the action group’s
bottom and the byline’s top, accounting for its own wrapped height.

The November 10 refinement passes desktop Dark, preview-only Light and a
390×844 mobile layout check. Computed mobile prose remains 20px/32px inside the
shared 50% browser transform; all eight rows fit, the first row center equals
the content center, and the mobile footer fits with its credit at the lower
edge. Native timelines and a forced JavaScript fallback advance the artwork;
a forced Reduced Motion fixture keeps leaf, flower and stem values unchanged
across scrolling. Font loading and sidebar width changes still remeasure the
plant. Syntax, Wrangler dry run, assets/cache keys, local documentation links
and whitespace checks pass. Preview fixtures are not deployed.

The rooted-flower revision also passes desktop Dark, preview-only Light,
390×844 bounds and footer inspection. Each main stem junction exactly matches
its leaf’s resting pivot, including mirrored right leaves. Native and forced
fallback scroll paths open the petals and reveal stamens; the forced Reduced
Motion fixture retains identical fully open petal transforms and stamen opacity
across scrolling. The final download group center is at 50% of the viewport;
the root meets the bumpy horizon at 15%, and the author credit remains 18px from
the lower edge. These are browser-preview checks, not physical Safari tests.

The generated-plant revision passes desktop Dark, preview-only Light and a
390×844 mobile viewport. The logo circles advance through intermediate scroll
positions before the first point enters. Seven distinct main silhouettes remain
byte-identical across desktop and mobile; all generated path coordinates are
finite. Native and forced-fallback roots grow through intermediate parent/child
stages and finish all 75 paths. The forced Reduced Motion fixture leaves logo,
petal and root values unchanged. The 19 anthers render in both schemes. The
final gap measures 24px, and the upstream credit center matches the midpoint
between the action bottom and byline top within 0.1px before/after mobile scaling.
Syntax, deployment dry run, asset/cache keys, local links and whitespace pass.

The subtle-growth revision keeps roots at 80% before their range and finishes
only the tips. Native and forced-fallback checks cover narrow-to-wide stamens,
the moving logo-only opening, and completed roots; a forced Reduced Motion
fixture leaves the completed artwork unchanged. Dark, preview-only Light and
390×844 layouts include the continuous darker underground fill. Mobile uses a
pointer-free sidebar collapse with a 260ms content-boundary transition.

The mobile-attachment revision replaces offset-based joins and outer-SVG CSS
rotation with measured SVG boxes and inner numeric pivots. All nine phone-preview
junctions match their vine nodes within 0.001px, including while swaying. The
opening mark starts at the viewport center, above the personal note. The ground
has no stroke, the final mark/button gap is 28px (14px at mobile scale), and the
credit stays at the actions/byline midpoint. These are desktop/phone-size browser
preview checks; the owner’s physical iPhone rendering was not independently
retested.

The growing vine stroke is 2.6px at 68% opacity over a 30% guide. It starts
once the flower is at least 35% open, then reaches
the root crown when that junction is 60% down the viewport. The established
root silhouettes are precomputed during layout and cached until their geometry changes. Two shared radial-gradient masks expand from the crown: the faint base starts at 70% of the final radius and the lighter overlay starts at zero. Both finish over 27% of the viewport’s scroll distance, with 18% of a viewport left to scroll. This replaces the earlier per-junction path timing with a soft radial front and reduces 270 animated centerline masks to two animated transforms. The overlay uses the stem ink in Light and the brighter cyan/mint mix in Dark. Base silhouettes use 50% opacity and the overlay 90%, under an 85% root layer, keeping the fine roots close to the stem’s visual weight. Native scroll timelines and the fallback use the same linear radial progress; Reduced Motion shows both complete layers without motion. Each leaf opens outward by 6 degrees as the stem light reaches its attachment; small shoots and tendrils open by 7 degrees around their own stem junctions. Numeric SVG pivots keep all joins attached. No timer, idle pulse or dependency is added.

The earlier root-light revision verified 135 static base silhouettes and 135 matching
light silhouettes. Before arrival all light masks are empty; during the burst
parents advance before their children, and all complete by the last scroll
position. Base path data, fills, opacity and lack of masks stay unchanged through
scrolling. The forced Reduced Motion fixture keeps every light mask complete.

The leaf-opening revision keeps 135 matching base/light silhouettes, with base
centerline masks starting at 70% of the network’s maximum travel distance. The
base growth front advances to 100% during the existing light burst; the light
still reveals from 0% to 100%. Shared travel distances keep child attachments
behind the parent’s growth front. Main leaves rotate 6 degrees outward and 21
small shoots/tendrils rotate 7 degrees around fixed junctions as the stem light
passes. Reduced Motion retains the complete, open plant.

The stem-polish revision removes the flower’s bent connector, keeps its neck
steady above a vertically tangent first vine segment, and uses one flat stem
ink across the vine, petioles and offshoots. The root base uses 32% of its former
opacity while the independent light overlay retains its full reveal. The
prelude spans 1.08 viewports; the logo stays centered at half a viewport, the
personal note starts 128px below that center, and 128px separates the prelude
from the flower section. The flower starts below the initial viewport on
desktop and at phone size. Nine shorter sentences cover blocking, consent,
extensions, navigation, page focus, search choice and open-source foundations.

The personal note fades from 18px below its resting position after the logo’s
scroll range ends, over the next 18% of a viewport. Each point fades up by the
same amount as its resting text center moves from 75% to 55% down the browser
viewport. These ranges reverse with scrolling and retain the settled text
above that band. Native scroll timelines and the JavaScript fallback share
setup’s cubic-bezier(.2,.8,.2,1) easing. Reduced Motion shows all text in place.

The first point now leads with current Chromium, followed by uBlock Origin.
The extension point explains the privacy benefit of proxying downloads and
updates, following [Helium’s published explanation](https://helium.computer/).
There are ten points in the same flowing sequence and type style.

The restored phone cursor uses numeric translate3d positions from the measured
path in the existing scroll animation frame, instead of native motion-path
interpolation. Its tip stays anchored at the half-scale sidebar toggle during
the click pause. Opacity, press scale and click ring share the desktop progress
windows. The later Safari cursor fix extends this numeric positioning to desktop and recomputes it when crossing the mobile breakpoint.

The underline refinement confines the effect to handwritten links and restores
regular text underlines in the footer. Its upward arc thickens on the right,
ending in a small ink dot. The stroke uses currentColor without extra opacity,
and a 600ms clip animation wipes it from left to right on hover or keyboard
focus. Reduced Motion disables that animation. Lune is plain text in the final
line; only Helium and ungoogled-chromium are linked there.
Local inspection confirms currentColor at opacity 1 for handwritten strokes,
regular CSS underlines with no sketch pseudo-element on footer links, and no
horizontal text overflow at desktop or 390px width. Keyboard focus samples the
same 600ms wipe from a 99.4% right inset to 0%. Asset hashes, scope, final-line
links, syntax and whitespace checks pass.

The radial-root revision was checked locally at desktop and 390×844 phone size, including dark appearance, reverse scrolling, the forced timeline fallback and Reduced Motion. A three-second desktop scroll comparison recorded median frame intervals of 66.1ms with the previous 270 masks and 16.7ms with the two radial masks (55 versus 180 frames). These are local browser preview measurements, not physical iPhone results or production readback. The existing website deployment dry run and JavaScript syntax check pass.

The root contrast refinement strengthens both appearances: Light uses the stem’s exact ink color for the reveal, while Dark retains the lighter cyan/mint mix. The base/overlay opacity multipliers increase from 32%/65% to 50%/90%, and the shared layer from 68% to 85%. Radial reveal geometry and timing are unchanged.

The spacing/header-hold revision checks all ten desktop reading positions and
390px text bounds without overflow. Native and forced-fallback paths hold the
cursor at an identical header point through 18–42% of the journey, then click
the toggle at 68%. Their respective sentences meet the 58% reading height.
The desktop hover x is 404px in a 1212px window; the phone hover x is 244px in
a 732px logical window (half-scale). Both panels are visible with the cursor
tip still 16px inside the top edge and retract when it is about 3px outside;
reverse scrolling restores them. Phone behavior agrees, and a forced Reduced
Motion fixture hides the cursor and leaves the header closed. Syntax, asset
cache keys, local links, whitespace and deployment dry run pass. These are local
preview checks; this revision has not been deployed.


The earlier Cmd-T sequence passed local empty/typing/scoped/dismissal checks: all five
characters appear without a result row, then the Wikipedia pill and its row
appear together. Stationary scrolling completes typing and holds the pill;
reverse scrolling restores or resets the appropriate state. Later entrance,
bang-typing and dismissal thresholds remain separate. Native and fallback
previews agree on 600×111px scoped geometry, 18px corners and the 5% black /
10px / 3px shadow. A 390×844 preview remains within the window, and Reduced
Motion hides the illustration. Focused state-transition checks cover reversal,
leaving the story and cancellation. The source consolidation checks JavaScript
syntax, local assets, SVG symbols and matching cache keys at each intermediate
commit; the final Wrangler deployment dry run and whitespace checks pass.
These are local checks, not a new production deployment.

The updated illustration follows the [accepted native provider-pill design](../agent-docs/project/features/command-bar-bangs.md), with the owner-requested website simplification: no autocomplete results appear at any point. It types `!wiki`, then shows the Wikipedia pill and “Search Wikipedia” placeholder in the same 52px pane. Local browser checks cover Light/Dark desktop, 390×844 phone size, a forced timeline fallback, Reduced Motion, stationary typing, dismissal and reverse-scroll reset. JavaScript syntax, asset/cache-key checks, deployment dry run, documentation links and whitespace pass. Preview fixture hooks are served only by the local test server and are absent from shipped sources. This source refinement has not been deployed.

The Safari cursor fix (November 11, 2026) replaces desktop SVG motion-path positioning with the same measured numeric transforms used on phones. Desktop Safari reproduced the old cursor stuck at the window origin; the fixed local preview moves to the header hold and sidebar click, reverses on backward scrolling and retracts both panels on exit. Cursor opacity, press scale and click ring use the existing scroll-frame update. Reduced Motion continues hiding the demonstration.

Focused Chromium checks pass at 1440×1000 and 390×844, with native and forced-fallback layout timelines, Reduced Motion, phone-to-desktop resizing, reverse scrolling, click-ring visibility and panel exit. The cursor hotspot stays within 0.6px of the toggle during the click hold; no JavaScript errors were observed. JavaScript syntax, asset cache keys, documentation links, whitespace and the pinned Wrangler 4.158.0 deployment dry run pass. No specific GitHub issue tracks this website defect. Physical iPhone Safari was not retested.
