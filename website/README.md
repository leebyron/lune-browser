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
  a continuous background, darkening below the soil contour; there are no fixed-height slides or alternating panels. A
  ResizeObserver measures the content to set the scroll distance and reading
  indicator, including after fonts load or the viewport changes. Reduced motion
  removes the launch bounce and zoom.
- Interface surfaces are not text-selectable; headings, prose, attribution links,
  and the address field remain selectable. The sidebar has two pinned tabs and
  no divider above New tab. Chrome uses the accepted #E7EDE3 Light / #10354F Dark mounted palette.
  Selected tabs use #D6E1D2 / #2A4C62 for directional contrast.
- The illustrative shell mirrors the native edge-to-edge frame and sidebar-footer
  revisions reviewed on 2026-11-07: 16px outer corners, no content gutter, inner
  radius, outline or shadow. Only the outer window clips the page. A physical-pixel
  semantic hairline separates the pinned sidebar from content.
- Pinned and floating sidebars have identical 216px widths, flush top/bottom/left
  edges and square inner corners. Pinned mode shares the window material;
  floating mode approximates the accepted themed glass: a lighter Light tone and darker Dark tone, with theme selection and hover colors.
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
  32px close region holds an 11px glyph centered 15px from the trailing row edge.
  Labels yield space and fade before the close mark without changing row height.
  The illustration omits default-browser and update prompts.
- During the attention sentence, a scroll-driven cursor enters from the left of the
  screen, clicks the sidebar toggle and exits through the top. The page immediately
  fills the window, while the glass sidebar remains until the cursor is more than
  48px away. The sidebar then slides left over 260ms. Scrolling back reverses it.
  CSS scroll timelines own the cursor and layout state, with a JavaScript fallback.
  On mobile the pointer and click ring are omitted, and the sidebar and content
  boundary move together over 260ms; Reduced Motion removes that transition.
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
  `x86`. Unsupported, denied, or unknown hints (and other platforms) retain a
  native popover with explicit Apple silicon and Intel choices. Legacy
  `MacIntel`/user-agent strings are not used to infer chip architecture.
  The download buttons and explicit choices use permanent GitHub
  `releases/latest/download/Lune-macos-ARCH.dmg` URLs. Both aliases resolve to the
  accepted production release; feeds are served from the canonical repository.

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
- `public/assets/favicons/`: official Fastmail, Lee Byron, Helium and GitHub
  icons, served locally. The Fastmail Calendar pin uses an inline calendar glyph.
  Legacy design-source icons remain unused. Icons belong to their respective
  sites and illustrate the preview tabs.
- Finder and Trash images: macOS system artwork, used in the illustrative Dock.
  Apple retains ownership; these are not Lune artwork or relicensed by this repo.
- Syne 800 and Inter 400/500: Latin WOFF2 subsets from Google Fonts, Syne v24 and
  Inter v20. SIL Open Font License notices are in `public/licenses/`.
- `public/assets/ublock-origin.png`: unchanged 32px uBlock Origin toolbar artwork
  from the prepared browser’s `third_party/ublock/img/icon_32.png`. Copyright
  Raymond Hill and contributors; GPLv3 notice in `public/licenses/ublock-origin.txt`.
- `public/assets/onepassword.svg`: official 1Password favicon from
  <https://1password.com/favicon/icon-v2.svg>, used as illustrative extension
  artwork; the brand belongs to 1Password.
- Inline interface icons: Lucide (download, arrow-up-right, chevron-down,
  panel-left, maximize, shield). Its ISC/MIT notices are in
  `public/licenses/lucide.txt`.
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

The tagline is “A respectful browser for Mac.” Nine short sentences make the factual case through enabled ad/tracker blocking,
third-party cookie defaults, removed Google integrations, consent, extensions,
keyboard navigation, sidebar control, setup choices and shared source, with no headings, fragments, eyebrows or screenshot placeholder.
The opening reuses setup’s paired-circle logo reveal, driven by scroll
rather than a timer. The mark starts at the content viewport’s vertical center
and moves upward with the page. A short personal note sits directly below it
in the same Inter 20px/32px as the marketing points, with a 96px section gap
before the first point;
the flower is already visible when the browser opens. The opening point
has only a flower, enlarged 50%; eight uniquely generated leaves mark later points. A branching cyanotype vine joins them with small shoots and curled
tendrils, rather than a line connecting separate icons. Marketing prose uses
regular Inter 20px/32px and one foreground color. At 700px or less, the complete
browser and its content share the same 50% transform: prose renders at 10px/16px.
There is no mobile-only enlargement of the text, coda, buttons or author credit.
The window fixes text-size adjustment at 100% so mobile text autosizing does not
diverge from the chrome. This does not assert physical Safari-device validation.
Syne remains confined to the Lune wordmarks.

Each row has the same maximum text measure of 34ch and reserves an 80px
specimen plus a 36px gap (48px beside the larger flower). The copy is vertically centered beside the leaf or
leaf body, 10px above the row center; the first sentence rises 22px to align
with its larger flower. The complete row starts horizontally
centered, then follows x = column center + A sin(2πi / (n − 1)). A is at most
48px and shrinks to the available room; 32px is reserved so even narrow layouts
retain a small wave. The browser cursor unpins the sidebar while the attention
sentence is in view. The coda thanks the authors and contributors behind Helium and
ungoogled-chromium. Its preceding gap is 24px, keeping the ground close to the
last point. See the [copy rationale and evidence](../agent-docs/project/website-respect-story.md).

The sidebar pins Fastmail and its Calendar. The other tabs link to Lune, Helium, the Lune GitHub project and Lee Byron,
in that order; the author’s website is last and the Lode row is removed. Every tab, including New tab, is a real
anchor opening its destination in a new tab with `noopener noreferrer`, as the
owner requested after considering iframe navigation. No iframe, proxy, external
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

## November 10 browser-polish audit

Compared the existing illustration with the current development lock and frozen
26.1110.1 source, using the feature records below. These are website changes;
they do not change browser patches or constitute native runtime validation.

| Recent browser work | Website treatment |
| --- | --- |
| [Themed sidebar](../agent-docs/project/features/themed-unpinned-sidebar.md) | 216px width; mounted palette; lighter Light / darker Dark detached tint; strong #D6E1D2 / #2A4C62 selection and themed hover fills. CSS blur remains an approximation. |
| [Toolbar polish](../agent-docs/project/features/trailing-toolbar-controls.md) | 72px navigation pill with separator; medium-weight 16px symbol approximations; 14px site-info/reload art in 32px slots; 2px reload inset; address cap at half the available header; 4px trailing padding and 2px gaps; no gap between Extensions and first extension; real uBlock and 1Password artwork. The latest owner revision limits this illustrative group to those three controls, omitting Profile, Downloads and More. |
| [Glass appearance](../agent-docs/project/features/chrome-appearance.md) | Diffuse 5% black / 10px / 3px header shadows, no extra sidebar shadow. CSS tint and foregrounds follow appearance; AppKit content adaptation is not emulated. |
| [Header scrolling](../agent-docs/project/features/header-scroll-through.md) | Removed the previous wheel-event blocker; native click shielding remains represented. |
| [Sidebar pin](../agent-docs/project/features/sidebar-pin-activation.md), [edge frame](../agent-docs/project/features/edge-to-edge-frame.md), [New Tab](../agent-docs/project/features/sidebar-new-tab.md), [footer](../agent-docs/project/features/sidebar-footer.md) | Retain accepted flush geometry, pin/reveal choreography, fixed New Tab and hover-only tab closes. The illustration continues to omit installation/update prompts. Native activation colors and OS window menus are not simulated. |
| [Menu retention](../agent-docs/project/features/menu-reveal-retention.md), [downloads](../agent-docs/project/features/downloads.md), [media](../agent-docs/project/features/media-toolbar-controls.md) | The trailing group shows idle artwork. Native menus, download progress/status and media sessions remain outside this illustration. The website’s real download chooser retains its own popover behavior. |
| [Command-T/results](../agent-docs/project/features/command-bar-corners.md), [suggestion selection](../agent-docs/project/features/address-suggestion-selection.md), [toolbar modes](../agent-docs/project/features/header-inset-prototype.md), [older macOS](../agent-docs/project/features/older-macos-appearance.md), [window close](../agent-docs/project/features/native-window-close.md) | Keep the default hover-toolbar story and modern window shape; no fake search results, Settings, OS fallback or native multi-window behavior. Website close/minimize return to its desktop; fullscreen uses the web API. |
| [Setup, fonts and icons](../agent-docs/project/features/onboarding-visual-refinements.md) | Existing accepted wallpaper JPEGs, Inter prose/buttons and compiled Dock artwork already match and are retained. |

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

Original vector artwork is generated from fixed seeds. Every main leaf and
small offshoot has its own length, width, lean, edge variation and vein pattern.
Leaves have narrow, pointed silhouettes with restrained edge variation. Each
petiole is part of its leaf’s fill, avoiding a separate stem seam; small shoots
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
and depth at 25% of the viewport (at most 180px). The base silhouettes are always fully drawn and never animate. Identical
lighter copies use centerline masks for the light’s travel from crown to tips.

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
base roots begin at 70% of their total reach, with a shared growth front keeping every branch connected. The remaining 30% grows as the light fans through them. A lighter copy of every tapered outline
is drawn from 0% to 100% over them, with the full branching burst spanning 27%
of the viewport’s scroll distance, finishing with 18% of a viewport left to scroll.
Measured travel distance from the crown sets each branch’s range, so a child’s
light starts exactly when its parent reaches the attachment. The overlay uses
a restrained cyan/mint mix at 65% of the root’s existing opacity. Native and
fallback progress are linear along the paths; Reduced Motion shows the complete
light trace without motion. Each leaf opens outward by 6 degrees as the stem light reaches its attachment; small shoots and tendrils open by 7 degrees around their own stem junctions. Numeric SVG pivots keep all joins attached. No timer, idle pulse or dependency is added.

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
