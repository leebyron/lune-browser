# Website specification

Agent-owned requirements for [lune.computer](https://lune.computer/). These files describe the intended behavior of the current implementation, checked against repository source on November 17, 2026.

| File | Scope |
| --- | --- |
| [Experience](experience.md) | Desktop, story, browser illustration, motion, and downloads |
| [Assets and credits](assets.md) | Appearance, asset sources, licenses, and attribution |
| [Build and delivery](delivery.md) | Legal pages, local checks, production deployment, and readback |

## Maintaining this specification

Update the relevant file when an accepted change alters behavior. Keep each requirement in one place; link to code for implementation details rather than copying algorithms or tuning histories. Keep the human-facing [README](../README.md) limited to an introduction and local setup.

The homepage sources are [index.html](../public/index.html), [styles.css](../public/styles.css), and [main.js](../public/main.js). Legal text is canonical in [legal/](../../legal/); deployment configuration is canonical in [wrangler.jsonc](../wrangler.jsonc) and the [Website workflow](../../.github/workflows/website.yml).

Browser claims must match the promoted release and its [frozen inputs](../../manifests/releases/), with [feature records](../../agent-docs/project/features/README.md) as supporting evidence. The [development lock](../../manifests/browser.lock.json) describes future builds, not proof that a change is published. The website is an illustration, not native-browser validation.

Keep exact source identities, test results, device limitations, and public byte readback in dated [build records](../../agent-docs/project/builds/). Older reports and Git history explain past revisions; they do not override this specification. No live deployment or physical-device verification is implied by this source review.
