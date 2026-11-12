# Lune / Day and night

The paired lunes use adjusted inner circular arcs, preserving the outside
silhouette and pointed tips. Their midpoint thickness is 48.412 source units,
33% greater than the previous 36.4. Outer radius 111 and center offsets 14 stay
fixed. The geometry and sRGB palettes live in [`palettes.json`](palettes.json).
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

The website's `favicon.svg` is a transparent, full-width dual-lune mark on a
tightly fitted square viewBox. Its embedded `prefers-color-scheme` media query
selects the light/dark brand colors without JavaScript or separate URLs.
The PNG and multi-resolution ICO fallbacks use the same transparent framing
with the fixed dark palette. Apple touch artwork retains its opaque background.

### Native floating-glass icons (2026-11-12, accepted)

The current app mark retains the selected adjusted arcs at scale 3.3, with a
source width of 825: 10% larger than the initial glass review's 750. Each
lune occupies a separate Icon Composer group in both appearances with native glass enabled, inside
specular highlights, 40% translucency, 60% refraction strength, 30% refraction
height and 20% chromatic shadows. The reduced height and shadow keep the pieces
close to the icon plane. Light and Dark share the exact same material settings; Dark uses its native
appearance and explicit blue background. No shading, shadows, or bevels are baked
into the imported SVGs.

Both appearances render through the current Icon Composer renderer, explicitly
using design generation 27. `actool` supplies the legacy macOS icon canvas and
size-specific margins; `package-app-icon.swift` fits each native rendering
to a clean transparent canvas before `iconutil` packages all ten representations. No older-renderer rim/shadow is composited behind the new mask, avoiding
straight shadow seams at its transparent corners. The half-alpha
keyline preserves antialiased small-size edges without treating the outer
shadow as artwork. The website Dock uses the exact 256px packaged representations.
Layered `.icon` sources are retained beside the platform's `.icns` inputs.

Lune's existing runtime packages flattened `.icns` files and switches between
Light and Dark with its appearance observer. This change preserves that runtime;
it does not claim system-driven lighting or Clear/Tinted support from a bundled
layered asset catalog. Websites, favicons and internal marks retain flat artwork.
Their static and animated paths share the selected adjusted-arc geometry.

Apple's [Icon Composer workflow](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer)
and [2026 Icon Composer lab](https://developer.apple.com/videos/play/wwdc2026/8012/)
explain separate groups, Individual effects, inside/outside specular placement,
refraction, translucency and chromatic/ring shadows. The light source was opened
in Icon Composer and its actual two-group, generation-27 material verified.
See [the current feature record](../agent-docs/project/features/day-night-branding.md#thicker-adjusted-arcs-and-native-glass--november-12-2026)
for source adoption and validation limits.

### Accepted app-icon refinements (2026-11-12)

The owner requested the reviewed mark 10% larger, increasing its source width
from 750 to 825 (scale 3.0 to 3.3), then requested less shadow so the pieces sit
closer to the icon plane. The accepted version uses 20% chromatic shadows and 30%
refraction height; strength remains 60%, translucency 40%, and both appearances
share one material configuration and the generation-27 renderer. The adjusted
arcs and opening animation retain their selected geometry.

Signed input `inputs/glass-icon-relief-1/macos` identifies
`15170d0c385565cbe94cd59c282d9f89a9edd367`, following the separate 10% scale
commit. Both app bundles rebuild, all twenty icon representations decode, and
the owner-reviewed **Lune Icon Review** bundle matched the exact input. The
website Dock images use the same native representations. The owner accepted all
artwork and animation on November 12; the development lock adopts this input
for future builds. The temporary app, profile, review board and servers are
cleaned up; evidence is retained in `.work/icon-update/relief-review/` and the
[acceptance record](../agent-docs/project/builds/2026-11-12-accepted-icon-refinements.json).
Production website deployment and a browser release are separate from this acceptance.

### Native macOS icon shape candidate (2026-11-09) — historical

`scripts/branding/render-app-icons.py` now generates Icon Composer sources from
the canonical palettes and lune paths, then uses Xcode's `actool` to produce
the macOS mask, margins, edge treatment, and complete legacy `.icns` variants.
`--standalone-icon-behavior all` is required: the default emits only small
fallback sizes and places the remaining representations in `Assets.car`.
The generated catalogs are not needed by Lune's existing `.icns` packaging.
The lune layers have glass effects, translucency, and group shadows disabled;
the background receives Apple's standard treatment.
The app-only lune mark uses scale 3.3, centered at 512 × 512, retaining the
native outer shape and margins. This is 37.5% larger than the initial scale 2.4:
the first 25% enlargement followed by an owner-approved additional 10% to match
the installed Safari compass's approximate width (80% of the tile). This is an
optical comparison, not a mandatory Apple content-circle diameter.

This replaces the app icon's hand-drawn 896 px rounded rectangle with 200 px
circular corner radii. Web and internal browser artwork retains its current
geometry. Sources are generated into `out/branding/Lune-{light,dark}.icon`;
both complete iconsets and `.icns` files are regenerated alongside them.
Requires Xcode with Icon Composer support (validated with local Xcode 27.2).

See Apple's [app icon guidance](https://developer.apple.com/design/human-interface-guidelines/app-icons)
and [Icon Composer workflow](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer).
Apple specifies unmasked square artwork and applies the platform mask itself.

The owner approved the native shape and final logo scale and requested app
integration on November 9. Both variants compile and decode at all ten standard
iconset representations, from 16 to 1024 pixels. The final Safari comparison is
`out/branding/safari-content-comparison.png`.

The three `.icns` inputs are integrated into the local platform candidate at
`.work/menu-retention/platform/resources/assets/` and its prepared Chromium
source. Platform commit `7aa674dc93b2643075e119342b659221cf41613a` is retained
locally on `topic/native-app-icons`; it contains only the three app-icon files.
Both arm64 (`out/Default`) and Intel (`out/Intel`) app bundles rebuild
successfully. Byte comparisons verify the fallback and both appearance icons
in the main apps and the fallback in both alert helper bundles. The existing
native appearance observer selects the exact new assets through light/dark/light
transitions in isolated arm64 and Intel-under-Rosetta fixtures; this does not
establish native Intel hardware acceptance. Evidence lives in `.work/icon-shape/`:
`builds.json`, `packaged.json`, and `observer-{arm64,x86_64}.log`.
The arm64 browser page-loading, JavaScript, and restart-persistence smoke test
passes. Intel's first smoke attempt timed out creating a session; the retry
passed page loading, JavaScript, and storage writing, then timed out navigating
after restart. Intel restart persistence is therefore not verified by this run
(`smoke-x86_64-retry.json`). The icon-only bundle rebuild and native observer
fixture pass; no browser implementation code changed for this integration.

The transparent favicon's SVG media-query colors pass browser checks in both
schemes. All six raster fallback sizes pass transparency and full-width checks.
See `.work/icon-shape/favicon-check/report.json`. The development lock,
previously installed previews, published builds, and live website are unchanged.

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
