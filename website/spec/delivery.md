# Build and delivery

## Sources and generated pages

The site uses plain HTML, CSS, and JavaScript with Cloudflare Workers Static Assets. There is no application Worker script or service backend. The homepage is edited directly in [public/](../public/); a build copies those assets into ignored `website/dist/` and generates legal pages.

| Route | Canonical source |
| --- | --- |
| `/` | [public/index.html](../public/index.html) |
| `/privacy`, `/privacy.md` | [legal/privacy.md](../../legal/privacy.md) |
| `/terms`, `/terms.md` | [legal/terms.md](../../legal/terms.md) |

[build.mjs](../scripts/build.mjs) validates both legal documents before replacing the previous build. [legal.mjs](../scripts/legal.mjs) lists page identities and renders Markdown through [templates/legal.html](../templates/legal.html), styled by [legal.css](../public/legal.css). Do not edit generated HTML. Markdown downloads are exact source copies, including metadata.

Each document requires ordered front matter: `status: draft|published`, `revised: YYYY-MM-DD`, and an optional `effective: YYYY-MM-DD`. Dates must be valid; each document must have exactly one H1. Published documents require an effective date and no unresolved “draft” or “placeholder” markers. Drafts receive `noindex, nofollow` without a visible status badge.

Legal pages provide a section navigation, skip link, homepage link, revision/effective dates, Markdown download, and GitHub edit history. Escape raw HTML in Markdown. Serve the Markdown downloads as plain text with `nosniff` through [public/_headers](../public/_headers).

Production builds require both documents to be published. This validates readiness markers, not legal or factual correctness. Do not bypass the guard with a direct Wrangler deployment. The policy describes Cloudflare hosting and analytics; locally hosted fonts and artwork do not imply the absence of production analytics.

## Local work and checks

From `website/`:

```sh
npm ci
npm run dev
```

`dev` builds once, then starts Wrangler. Rebuild with `npm run build` after source edits; Wrangler serves/watches `dist/`, not the canonical sources. Dependencies are locked in [package-lock.json](../package-lock.json); commit it with dependency changes.

`npm run check` builds, runs the legal-renderer tests, and performs a Wrangler deployment dry run. For documentation-only edits, check links, source consistency, and whitespace; no browser build or deployment is needed.

For behavior changes, also inspect Light/Dark desktop and narrow layouts, forward/reverse scrolling, stationary text/typing completion, native timelines and forced fallback, Reduced Motion, keyboard focus, New tab, panel dismissal, and download-platform states as affected. Check console errors, local asset/SVG references, and hash query keys when changing cache-keyed assets. Phone-size emulation does not establish physical iPhone behavior; record Safari/device coverage accurately.

## Production configuration

[wrangler.jsonc](../wrangler.jsonc) owns Worker `lune-website`, its account/zone IDs, the `lune.computer` Custom Domain, `dist/` asset directory, and 404 handling. It enables workers.dev and disables preview URLs; workers.dev is not a staging release channel. Treat the custom-domain/DNS setup as existing infrastructure, not an activation task to repeat.

[Website workflow](../../.github/workflows/website.yml) deploys owner pushes to `main` affecting `website/**`, `legal/*.md`, or the workflow itself. Owner manual dispatch on canonical `leebyron/lune-browser` and `main` is also supported. This broad filter includes website documentation. For documentation-only pushes with local checks complete, include `[skip ci]` in the commit message to avoid deploying unchanged assets; GitHub documents this [push-workflow skip instruction](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs).

Use the existing `[self-hosted, macOS, ARM64, lune-build]` runner. Website, setup, and browser work share `lune-browser-local` concurrency. The workflow pins actions, uses Node 24 and read-only repository permissions, then runs `npm ci`, `npm run check`, and `npm run deploy`. Never run untrusted PR/fork code on this persistent signing host.

`deploy` runs the production build guard before Wrangler. Cloudflare authentication uses repository secret `CLOUDFLARE_API_TOKEN`; keep tokens outside source and logs. Account/zone IDs are public configuration. Browser signing and publication remain separate from website deployment.

## Publication and readback

For an authorized deployment:

1. Validate the settled source and inspect the commits being pushed. Website changes and deployments do not require Chromium version or freshness checks.
2. Run the guarded Website workflow, or `npm run deploy` with the same production guard and appropriate authentication. A queued, cancelled, or merely pushed revision is not a deployment.
3. Verify workflow success, public HTTPS, and byte parity against the exact deployed build. Read back changed homepage assets and any generated legal HTML/Markdown; `_headers` is configuration, not a served file. Do not claim Cloudflare-injected analytics markup is a source change; distinguish it from the generated page when checking responses.
4. Retain the source commit, hashes, workflow URL, readback result, and material test limits in a dated [build record](../../agent-docs/project/builds/). Follow the [completion process](../../agent-docs/project/committing.md) and stop task-owned previews/servers.

Downloads use the fixed GitHub latest-asset URLs in [experience.md](experience.md#downloads). Keep architecture asset names stable so a browser release does not require website redeployment. Sparkle feeds live in the browser repository, not on this site. Publish immutable browser assets and verify both latest downloads and stable feeds before enabling or changing download links; use [release delivery](../../agent-docs/project/release-delivery.md) for promotion ordering.

Historical deployment evidence includes the [privacy publication](../../agent-docs/project/builds/2026-11-14-privacy-publication.json) and [terms publication](../../agent-docs/project/builds/2026-11-15-terms-publication.json). These are dated observations, not proof of the current live bytes.
