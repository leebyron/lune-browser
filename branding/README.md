# Lune / Day and night

The approved paired lunes are 30% wider at their horizontal midpoint: 36.4
instead of 28 source units. Their outside silhouette and pointed endpoints
stay fixed. The geometry and sRGB palettes live in [`palettes.json`](palettes.json).
`lune.svg` follows appearance; `lune-light.svg` and `lune-dark.svg` are fixed variants.

The dark palette comes from **Lune / Color Atlas**, version 3,
[Pelagic Signal](https://lune-color-atlas-lee.leebyron.chatgpt.site).
The approved light palette, **Chlorophyll Daylight**, carries its cool teal into
pale green paper and leaf green. No glow is added.

| Role | Light | Dark |
| --- | --- | --- |
| Ground | `#E7EDE3` | `#10354F` |
| Left lune | `#258D91` | `#00A7BE` |
| Right lune | `#789751` | `#5386BF` |
| Signal | `#C4D95A` | `#00D5C6` |
| Text | `#234550` | `#DDE7EA` |
| Action | `#276C69` | `#00D5C6` |

Use the darker teal action color for readable light-mode buttons; the yellow-green
signal is a decorative accent. Raster and vector outputs share the sRGB values.
The website retains its Syne wordmark and Inter text.

Run from the repository root on macOS:

```sh
python3 scripts/branding/render-assets.py
python3 scripts/branding/generate-assets.py --check
```

The renderer produces both iconsets and `.icns` files in `out/branding/`, all
internal PNG sizes, wordmarks, monochrome artwork, and Chromium `.icon` vectors
in `out/branding/internal/`. It also updates website SVGs and raster favicons.
Copy internal files into the macOS component's `resources/lune/`, copy both
`.icns` files into `resources/assets/`, and use `app-dark.icns` as `app.icns`.
These reviewed assets are pinned build inputs; browser builds do not regenerate them.

The running Dock icon follows macOS appearance. Finder and legacy raster icon
surfaces use the dark tile. Web SVGs, onboarding and default browser colors
follow light/dark mode. Custom themes, chosen accent colors and accessibility
palettes retain precedence. See [implementation and validation](../agent-docs/project/features/day-night-branding.md).

`resources/lune_resources.txt` runs after upstream resource replacement. The
Chromium 158 integration candidate overrides all 34 upstream browser-logo
destinations plus onboarding's favicon and SVG. Its `lune/internal-icons.patch`
uses that SVG in welcome, services, import, and finish screens. The main app and
notification helpers use Lune's `.icns`; the unused Helium asset catalog is not
bundled. The Helium partner badge keeps its upstream attribution as text, without
claiming those partnerships support Lune.
`lune/webui-logo.patch` also replaces both shared `cr:chrome-product` inline icons
with the generated monochrome SVG path, covering Settings and other WebUI users.

Check coverage against the selected upstream manifest and prepared sources:

```sh
python3 scripts/branding/verify-resources.py PLATFORM_CHECKOUT CHROMIUM_SOURCE
```

After compiling the candidate, add `--ui --internal-icons` to
`scripts/smoke-browser.py`. This checks helper bundle icons, rejects leftover
asset catalogs, and compares the loaded About, welcome, and services assets
against the exact component inputs. PNG EXIF removal is permitted; image and
color data must match. This avoids fingerprinting noise from canvas readback.
For an integration candidate, supply `--platform-commit` with its full macOS
component SHA. Source coverage, both Chromium 158 builds, arm64 headless/headed,
and Intel-under-Rosetta runtime checks have passed. The older 157 diagnostic app
does not contain this fix.


Name substitution must preserve upstream credits in translated strings as well
as English messages. After source preparation, check the component helper and
its actual XTB output:

```sh
python3 scripts/branding/check-names.py PLATFORM_CHECKOUT CHROMIUM_SOURCE --prepared
```

This also runs a synthetic regression through the multiprocessing entry point
and verifies ordinary localized branding still changes to Lune.

After compilation, compare packaged French and German partner strings with the
prepared translation catalogs:

```sh
python3 scripts/branding/check-runtime-credits.py BUILD_OUTPUT --source CHROMIUM_SOURCE \
  --locale fr --report out/validation/credits-fr.json
python3 scripts/branding/check-runtime-credits.py BUILD_OUTPUT --source CHROMIUM_SOURCE \
  --locale de --report out/validation/credits-de.json
```

The check uses a disposable profile and process-local macOS language override,
blocks external DNS, and uses a mock Keychain. It verifies the actual selected UI
language, exact partner translations, rendered Helium credit, Lune greeting, and
browser/source version match. These two runtime locales complement the full
source-catalog audit; they do not establish runtime coverage of every locale.
