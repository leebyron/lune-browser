# Website deployment

The website is a static HTML/CSS page with a small interaction script, deployed
independently of the browser. No framework, Worker script, server, or paid plan
is required. Assets and fonts are served locally. See the
[website source notes](../../website/README.md) for interaction timing and asset
provenance.

## Resources

| Resource | Value |
| --- | --- |
| Repository | `leebyron/lune-browser` |
| Production branch | `main` |
| Site source | `website/public/` |
| Wrangler config | `website/wrangler.jsonc` |
| GitHub workflow | `.github/workflows/website.yml` |
| Cloudflare account | `57a79916090fa9c99c899a708e9ba22c` |
| Worker | `lune-website` |
| Temporary URL | <https://lune-website.lee-57a.workers.dev> |
| Production URL | <https://lune.computer> |
| Registrar | DNSimple |
| Cloudflare zone | `2850307453708b5b5a13dff6cb0077d3` |
| Authoritative nameservers | `gabriel.ns.cloudflare.com`, `tia.ns.cloudflare.com` |

## Current status

The deployed source uses Rock Salt 400 at 16px/32px for the personal note
and ten botanical paragraphs. The note uses two separate paragraphs with the
owner's requested wording, staggering their entrances by 860ms. All story
copy uses a soft 800ms left-to-right wipe with ease-in-out timing, alongside
a 600ms fade and subtle 6px lift. Reduced Motion
shows fully visible text without masks or delays. The font and its Apache 2.0
license are served locally. The current production record below covers this
revision; subsequent local-check descriptions preserve their original scope.

The pollen refinement gives two of the seventeen mote groups a close companion with its own slightly smaller float path, reverse traversal, shifted phase, different speed and origin offset by about 23px, sharing only the scroll anchor. Three additional singles sit 48px, 72px and 96px up the stem from the root crown, above the ground. Light-mode stamen tips, halos and motes use `color(display-p3 .929206 .81535 0)`, preserving the original yellow's OKLCH hue and lightness while increasing chroma to the P3 boundary; `#EBD039` remains the sRGB fallback. Dark retains its existing teal.

The botanical copy follows the owner's ten-line sequence from Chromium
through removed Google services, extension proxying, blocking, Mac details,
the command menu, !bangs, toolbar, vertical tabs and open-source foundations.
Project names link to their sites/repositories, with Helium's !bangs linked to
the directory. Only handwritten links use the hand-drawn underline: an upward
arc in the text's ink color thickens to a dot on the right. Hover or keyboard
focus triggers a 600ms left-to-right clip wipe, disabled for Reduced Motion.
Normal-text links retain regular underlines. Lune is plain text in the final
line; Helium and ungoogled-chromium remain linked. The command menu is labeled
Cmd-T. The cursor pauses at the top edge one-third of the window width during
the toolbar line, exposing the header, then moves to the sidebar toggle during
the vertical-tab line. Both panels retract when its tip crosses the window
edge. Numeric transforms position the cursor on desktop and phones, avoiding Safari SVG motion-path failures. Native and fallback layouts share the two holds; the phone path uses the
same logical coordinates at half scale. Reduced Motion hides the demonstration.
Copy gaps now follow each seeded specimen's ink bounds, targeting 44px optical
clearance; the still-opening flower uses a 40px layout gap.

The recorded production Cmd-T demonstration opens empty as the command-menu sentence
reaches 70% of the pane. The next sentence triggers !wiki typing at the same
70% reading position, followed by the Wikipedia provider pill; the completion
result appears only with the pill.
The pill remains when scrolling is stationary and dismisses at a distinct later
scroll threshold, before the cursor's header hold. The illustration is passive,
has no open-tab options or network requests, and is hidden for Reduced Motion.
Live inspection of the installed app supplied its glass-menu reference; native
source supplies input, provider-pill and row metrics. That recorded revision uses a 600px
maximum width, 18px corners, 52px empty height and 111px scoped height. The
supplemental shadow matches 5% black, 10px blur and a 3px downward offset;
the glass itself remains a web approximation.

The deployed source uses the accepted native provider-pill design, with the owner-requested website simplification: no autocomplete row appears while typing or after scope application. The illustration types `!wiki`, then shows the Wikipedia pill and “Search Wikipedia” placeholder. Its pane remains 52px tall. Light/Dark desktop, 390×844, forced-fallback and Reduced Motion checks pass, including dismissal and reverse-scroll reset. Syntax, assets/cache keys, deployment dry run, documentation links and whitespace pass. This refinement is included in the November 11 Safari cursor deployment below; earlier production records retain their original scope.

[Deployment 43113788646](https://github.com/leebyron/lune-browser/actions/runs/43113788646) successfully deployed website source commit `5f2313568b22ed2f8f9377ec441d9c1e0d323a18` on November 11, 2026. The cursor uses measured numeric transforms on desktop and phones, fixing the SVG motion-path failure reproduced in desktop Safari. Local Safari verifies the header hold, sidebar click, reversal and panel exit. Focused Chromium checks pass for desktop, phone, forced fallback, Reduced Motion and phone-to-desktop resizing, with the click hotspot within 0.6px of the toggle and no JavaScript errors. Physical iPhone Safari was not retested.

Public HTTPS readback at 2:43:21 PM PST matches all 42 served public files byte for byte with that source commit; `_headers` remains deployment configuration. The pre-push official macOS Stable lookup returned `158.0.8127.18`, matching the published browser engine. The one-job local runner completed validation and deployment and then exited. No specific GitHub issue tracks this website defect.

Earlier production records:

[Deployment 42973009910](https://github.com/leebyron/lune-browser/actions/runs/42973009910) successfully deployed website source commit `98b8cd382da10571d4c923b2dcd308dbfd97e66d` after the eleven focused website commits were pushed to `main`. The existing local Mac runner completed validation and production deployment. This includes native-style chrome and tab-close controls, Fastmail pins, footer and download polish, handwritten copy and link wipes, cached radial roots, pollen refinements, the two-stage cursor and passive Cmd-T/Wikipedia sequence.

Public HTTPS readback on November 10, 2026 at 10:32:20 PM PST matches all 41 tracked public files byte for byte with that commit, including HTML, CSS, JavaScript, font, symbol, pen-underline and license assets. `_headers` is deployment configuration rather than a served asset. The fresh official Mac Stable lookup returned `157.0.8103.51`; the frozen published browser lock records `158.0.8127.18`, so it is not behind that observation. Local desktop/phone-size, fallback and Reduced Motion validation is recorded in the source notes; this readback does not add physical iPhone/Safari acceptance or a new browser release.

Previous production record:

[Deployment 42957488988](https://github.com/leebyron/lune-browser/actions/runs/42957488988) successfully deployed website commit `5b6d4ab6c6f2e01f195594da9fd74a5a5a40d590` using the existing local Mac runner and token. The owner accepted the paper surface, appearance-specific ink and pollen, wide shallow mote motion, timed text reveals, earlier personal note, macOS-style cursor and corrected sidebar labels. The opening wordmark retains Syne 800 at 40px after its missing size-variable fallback was repaired.

Public HTTPS readback on November 11 at 04:11 UTC matches HTML, CSS, JavaScript and the new cotton-paper JPEG byte for byte. Local desktop/phone previews verify 600ms text entrances and 200ms exits only across the bottom threshold, continued visibility past the top edge, and completion while scrolling is stationary. The note trigger is 39.6px earlier in the 720px desktop viewport. Fourteen seeded motes share the stamen glow, with wide shallow 26–42 second loops and reversible cubic outward travel. Light uses yellow-gold; Dark uses saturated Display P3 teal with an sRGB fallback. Reduced Motion settles text and artwork and stops the motes. Native and forced-fallback scroll paths pass. The cursor tip remains within 0.5px of the toggle center on desktop and phone previews. Production readback confirms the restored font, timed reveal state, renamed tabs and P3 motes without console errors. Syntax, deployment dry run, cache keys and whitespace pass. The pre-push official Mac Stable lookup returned `157.0.8103.51`; published Chromium `158.0.8127.18` is not behind that observation. Browser assets, feeds and download targets retain their existing identities. Physical iPhone rendering was not independently retested.

The live site links to `leebyron/lune-browser` for source and fixed latest-download URLs. Legacy feed redirects and staging files remain removed. See [current status](status.md) and [consolidation evidence](builds/2026-11-10-release-consolidation.md).

Subsequent browser releases update GitHub's latest pointer and paired stable feeds without a website deployment. Each release stores one DMG per architecture; the version-specific URL and fixed latest URL select the same asset. Follow [release delivery](release-delivery.md) for publication ordering and public readback.

The source now contains the
adaptive Chlorophyll Daylight / Pelagic Signal desktop and a continuous
scroll-driven browser story about respect for privacy, trust and attention,
credited to both upstream projects.
The source now uses ten short sentences in one Rock Salt style and color,
with a restrained, centered sine wave and no screenshot placeholder. The owner-accepted opening refinement starts the setup mark at 70% of the pane height and opens it over 65% of a viewport of scrolling. It moves upward with the content above the two-paragraph personal note in Rock Salt 16px/32px, with the note 128px below the logo center. A 1.28-viewport prelude and 168px section gap add space before the flower. The personal note triggers when its first line’s resting center reaches 68% of the pane, with a 1200ms stagger, leaving a 400ms pause after the first wipe. The second line reads “I wanted a browser that stayed out of my way”. The Google sentence now reads “with all Google's products & background services removed”. The owner accepted this refinement in the local preview; this paragraph records source behavior. Point copy becomes visible when its center reaches 85% of the browser viewport and stays visible through the top edge; only scrolling back below that lower threshold hides it. Scroll selects visibility while timed transitions finish independently (600ms in, 200ms out). Reduced Motion shows settled text. The softer 2.6px growing stroke waits until the flower is at least 35% open, then reaches the root crown before the final viewport, triggering an outward radial reveal through the roots over 27% of a viewport. The illumination finishes with 18% of a viewport left to scroll. The complete root silhouettes are cached until layout changes. Two shared radial-gradient masks reveal the faint base from 70% to 100% of its radius and the lighter overlay from 0% to 100%, replacing 270 animated centerline masks. Native scroll timelines and the fallback share the same radial progress; Reduced Motion shows both layers fully revealed. Its
flower is 50% larger, with 19 luminous stamens; nine generated leaves join a vine with
varied shoots, curled tendrils and subtle scroll motion that respects Reduced Motion.
Leaves alternate around their exact petiole attachments and open outward by 6 degrees as the light passes; small shoots and tendrils open by 7 degrees around their stem junctions. The vine measures stable flex-row boxes; inner numeric SVG rotations keep the attachments fixed across engines. The stem roots in a
Perlin-noise horizon 15% of a pane below the start of the coda, with cached tapered roots under a radial base mask starting at 70% of its final radius and a lighter radial reveal growing over them, and the upward-facing flower
opens its petals to reveal subtly luminous stamens.
Specimens and copy align vertically with per-specimen optical spacing. Leaves are narrow and pointed, with flat-ink petioles and tangent-aligned offshoots. The flower has a straight tapered neck above a vertically tangent first vine segment. The root base uses 50% silhouette opacity and the reveal 90%, under an 85% shared layer. Light uses the stem’s exact ink color; Dark mixes the stem ink 15% toward the soil color in both layers so roots are slightly darker than the stem. The coda adds 6⅔% of a pane of scrolling below the ground, increasing root-to-logo clearance while the brand/actions stay centered in the final pane. The terrain extends through the full coda with a slightly darker fill and no contour stroke. Fine terminal rootlets add detail, and the final mark/button gap is 36px. The faux cursor uses numeric scroll-positioned transforms on every screen size, including the half-scale mobile cursor and click ring; the floating sidebar stays visible until the faux cursor leaves the window. Reduced Motion hides the demonstration. Mobile content shares the
browser’s 50% scale without typography or coda enlargement. Two pinned links open
the Fastmail homepage with mail and calendar artwork; regular links open its `lune-browser` GitHub project, Helium,
`ungoogled-chromium` on GitHub and Lee Byron, with the author’s site last. The top-right
group is limited to Extensions, uBlock Origin and 1Password; the latter two
open their sites in new tabs.
The final point has only 24px before the coda. The points retain their reading order; the closing thanks use smaller 14px/22px Inter,
centered between the download actions and the bottom author byline, and the Lode author line sits at the bottom edge. Section heights and
the reading distance follow the content rather than a fixed page count. The
browser uses the mounted-left layout with the reviewed 216px sidebar and a reversible scroll-driven cursor
that unpins its sidebar during the minimal-UI section. The floating panel then
slides away as the cursor leaves; hovering the left rail slides it back over the
content. The pane snaps to width when pinning changes. Actual mouse interactions dismiss floating panels beyond a 48px pointer-distance
boundary; the faux cursor uses the window edge without a buffer. No cooldown timer remains.
The glass toolbar fades in from the top rail or either sidebar header, matching
the native browser. The pinned sidebar uses the window material; its floating
popover is a flush square CSS glass sheet. The window has a maximum width of 10/6 of its height, 16px outer corners and
edge-to-edge content without gutters or an inner shadow. Both sidebar modes share
header/row geometry; the pinned edge has a semantic hairline. Tab rows use native
standard-density dimensions and combined region/row insets, with hover-only close
marks. The illustration omits default-browser and update prompts. The emulated browser provides the visual demonstration. Download detects Apple silicon or Intel when the browser exposes macOS
architecture hints, otherwise offering both choices. Eligible download buttons point to permanent GitHub
latest-asset links. Known Windows, iOS/iPadOS, Android, Linux and ChromeOS devices see dimmed, disabled download buttons; unknown platforms keep the chooser. The canonical Sparkle feeds live in the same GitHub repository; legacy feed
redirects are retired during the November 10 consolidation.
For future releases, preserve [the promotion ordering](release-delivery.md)
and public byte readback before moving feeds or latest links.

## DNS activation

In DNSimple, open **lune.computer → Registration → Delegation → Edit delegation**.
Replace all four DNSimple nameservers with the two Cloudflare nameservers above,
then choose **Change name servers**. Do not edit DNSimple's locked system NS
records in the DNS record editor. DNSimple remains the registrar; Cloudflare
becomes authoritative for DNS. The initial DNS scan found no application records
to migrate. No DNSSEC DS record was present during setup.

`lune.computer` is attached as a Worker Custom Domain and recorded in Wrangler
configuration. Cloudflare creates the DNS record and certificate; public service
requires zone activation. Do not invent an A record or point the apex at
the temporary workers.dev URL. Verify public HTTPS and the page content before
marking the apex live. Reconcile DNSSEC separately after delegation if desired.

## Local development and deployment

From `website/`:

```sh
npm ci
npm run dev
npm run check
npm run deploy
```

`check` runs Wrangler's deployment dry run. `deploy` requires Cloudflare
authentication. Dependencies are locked; commit `package-lock.json` with dependency
changes. Keep OAuth and API tokens outside the repository.

## Completing a website change

After the authorized change is validated and its required public readback passes, follow the [commit and completion process](committing.md). Close specific resolved issues, stop task-owned preview/dev servers and delete disposable generated previews or build artifacts after retaining concise visual/deployment evidence.

## GitHub flow

Owner pushes to `main` affecting the website or its workflow run validation and
production deployment on the existing Mac runner. Owner manual dispatch is also
available on the canonical public repository, restricted to the owner and `main`. PR jobs are disabled on this
persistent signing host; validate proposed website changes locally. Website,
setup checks, and browser builds share one concurrency group. Actions
are pinned by commit and GitHub permissions are limited to repository read access.

The dedicated token `Lune website GitHub Actions` is stored in the GitHub Actions
repository secret `CLOUDFLARE_API_TOKEN`. The owner approved these permissions:

- Account → Workers Scripts → Edit, limited to the account listed above.
- Zone → Workers Routes → Edit, limited to `lune.computer`.
- No expiration; no IP restriction (GitHub-hosted runners have changing addresses).

Workers Scripts permission covers the entire selected account, not just this
Worker. The route includes an explicit `zone_id` so Wrangler does not need
zone-discovery read access. A deployment using these permissions was verified.
Never use the Global API Key or commit the token. Do not expose deployment secrets
to pull-request code. Rotate/revoke the token in Cloudflare and replace the GitHub
secret if compromised. Verify GitHub runs and live content after setup.

The account ID is public configuration, not a secret. The browser build and
release pipeline runs separately and does not run from this workflow.

## References

- [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/)
- [Worker Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)
- [GitHub Actions deployment](https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/)
- [DNSimple delegation](https://support.dnsimple.com/articles/setting-name-servers/)

## Production-only delivery correction (November 9, 2026)

The owner requires production/stable only. New releases stay as unpublished
GitHub drafts until acceptance, then publish final releases and paired stable
feeds. Canonical feed and latest-DMG readback precedes website deployment. The November
10 consolidation retires legacy redirects and historical staging XML; do not
restore old repository URLs. See [the current delivery procedure](release-delivery.md).
