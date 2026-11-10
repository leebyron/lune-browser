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

[Deployment 42912690521](https://github.com/leebyron/lune-browser/actions/runs/42912690521) successfully deployed website commit `578241793eefed869ed11c58226e7ec09a0807f0` using the existing local Mac runner and token. The flower now has a tapered straight neck and vertically tangent first vine segment. Flat ink unifies the main stem, petioles and offshoots; blade gradients remain separate. Unlit root opacity is 32% of its former value, while the separate light trace retains its 0%–100% reveal and the roots grow from 70% to full reach. The 1.08-viewport opening keeps the logo centered and leaves more space around the personal note; the flower starts below the initial view. Nine shorter sentences focus on blocking, consent, familiar extensions, navigation, page focus, search choice and open-source foundations.

Public HTTPS readback on November 10 at 22:15:09 UTC matches HTML, CSS and JavaScript byte for byte. Desktop and 393×740 phone previews confirm the flower starts below the opening view, by 174.5px and 89.3px respectively, and the note and points retain the same 20px type. Visual checks cover the flower neck, petiole colors and dark unlit roots; all sampled light masks remain empty before crown arrival. Generated paths remain finite. Syntax, Wrangler dry run, cache keys and whitespace pass. The 22:13:44 UTC [official Mac Stable check](https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Mac&num=1) returned `157.0.8103.51`; published Chromium `158.0.8127.18` is not behind that observed Stable version. No browser assets, feeds or download targets changed. Physical iPhone rendering was not independently retested.

The live site links to `leebyron/lune-browser` for source and fixed latest-download URLs. Legacy feed redirects and staging files remain removed. See [current status](status.md) and [consolidation evidence](builds/2026-11-10-release-consolidation.md).

Subsequent browser releases update GitHub's latest pointer and paired stable feeds without a website deployment. Each release stores one DMG per architecture; the version-specific URL and fixed latest URL select the same asset. Follow [release delivery](release-delivery.md) for publication ordering and public readback.

The source now contains the
adaptive Chlorophyll Daylight / Pelagic Signal desktop and a continuous
scroll-driven browser story about respect for privacy, trust and attention,
credited to both upstream projects.
The source now uses nine short sentences in one Inter style and color,
with a restrained, centered sine wave and no screenshot placeholder. The setup mark begins vertically centered and moves upward with the content, above a short personal note in the same Inter 20px/32px as the points; a 1.08-viewport prelude and 128px section gap keep the flower below the initial view. The softer 2.6px growing stroke waits until the flower is at least 35% open, then reaches the root crown before the final viewport, triggering a branching burst of light through the roots over 27% of a viewport. The illumination finishes with 18% of a viewport left to scroll. The unlit roots begin at 70% of their total reach and grow the remaining 30% as centerline masks draw lighter copies from 0% to 100%, timed by travel distance through each junction. Its
flower is 50% larger, with 19 luminous stamens; eight generated leaves join a vine with
varied shoots, curled tendrils and subtle scroll motion that respects Reduced Motion.
Leaves alternate around their exact petiole attachments and open outward by 6 degrees as the light passes; small shoots and tendrils open by 7 degrees around their stem junctions. The vine measures rendered SVG boxes; inner numeric SVG rotations keep the attachments fixed across engines. The stem roots in a
Perlin-noise horizon 15% down the final viewport, with connected tapered roots starting at 70% of their total reach and a lighter trace growing over them, and the upward-facing flower
opens its petals to reveal subtly luminous stamens.
Specimens and copy align vertically with a 36px gap. Leaves are narrow and pointed, with flat-ink petioles and tangent-aligned offshoots. The flower has a straight tapered neck above a vertically tangent first vine segment. The unlit root opacity is 32% of its former value; the independent light trace retains its full reveal. The terrain starts a slightly darker fill through the footer, without a contour stroke. Fine terminal rootlets add detail, and the final mark/button gap is 28px. Mobile omits the faux cursor and eases the sidebar boundary over 260ms. Mobile content shares the
browser’s 50% scale without typography or coda enlargement. Two pinned links open
Fastmail and Calendar; regular links open Lune, Helium, the Lune GitHub project
and Lee Byron, with the author’s site last. The top-right
group is limited to Extensions, uBlock Origin and 1Password; the latter two
open their sites in new tabs.
The final point has only 24px before the coda. The points retain their reading order; the closing thanks use smaller 14px/22px Inter,
centered between the download actions and the bottom author byline, and the Lode author line sits at the bottom edge. Section heights and
the reading distance follow the content rather than a fixed page count. The
browser uses the mounted-left layout with the reviewed 216px sidebar and a reversible scroll-driven cursor
that unpins its sidebar during the minimal-UI section. The floating panel then
slides away as the cursor leaves; hovering the left rail slides it back over the
content. The pane snaps to width when pinning changes. Both floating panels
dismiss beyond a 48px pointer-distance boundary; no cooldown timer remains.
The glass toolbar fades in from the top rail or either sidebar header, matching
the native browser. The pinned sidebar uses the window material; its floating
popover is a flush square CSS glass sheet. The window has 16px outer corners and
edge-to-edge content without gutters or an inner shadow. Both sidebar modes share
header/row geometry; the pinned edge has a semantic hairline. Tab rows use native
standard-density dimensions and combined region/row insets, with hover-only close
marks. The illustration omits default-browser and update prompts. The emulated browser provides the visual demonstration. Download detects Apple silicon or Intel when the browser exposes macOS
architecture hints, otherwise offering both choices. Production download buttons are enabled and point to permanent GitHub
latest-asset links. The canonical Sparkle feeds live in the same GitHub repository; legacy feed
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
