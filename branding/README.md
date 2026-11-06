# Lune / Pelagic Signal

The paired lunes preserve the geometry from **Lune / Color Atlas**, version 3,
[Pelagic Signal](https://lune-color-atlas-lee.leebyron.chatgpt.site), created for
Lee Byron. The macOS tile uses the palette's night background, without glow.

| Role | sRGB fallback | Display P3 source |
| --- | --- | --- |
| Night | `#10354F` | — |
| Left lune | `#00A7BE` | `0.06 0.66 0.78` |
| Right lune | `#5386BF` | `0.37 0.52 0.73` |
| Signal accent | `#00D5C6` | `0.04 0.85 0.79` |

The icon uses the Atlas's gamut-mapped sRGB fallbacks (OKLab chroma reduction,
preserving lightness and hue), so its PNG and SVG versions agree on ordinary
screens. The brighter signal accent is reserved for future UI use.

`lune.svg` is the editable master. `scripts/branding/render-icon.swift` renders
the same circle geometry with AppKit, including transparent macOS icon margins.
Run from the repository root:

```sh
swift scripts/branding/render-icon.swift
iconutil -c icns out/branding/Lune.iconset -o out/branding/app.icns
```

The generated `.icns` is an input in the macOS component's resources; it is not
regenerated during a browser build. Source and renderer changes must be reviewed
and the component asset updated together.

The renderer also produces `out/branding/internal/`: all internal PNG sizes,
light/dark wordmarks, a monochrome mark, and Chromium `.icon` vectors. Copy these
files into the platform component's `resources/lune/`, together with `lune.svg`
as `product_logo.svg`. The color vector uses the same circle intersections and
tile geometry as the master; monochrome vectors inherit the UI foreground color.

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
component SHA. Source coverage, the full Chromium 158 arm64 build, and headless
runtime checks have passed. The older 157 diagnostic app does not contain this fix.


Name substitution must preserve upstream credits in translated strings as well
as English messages. After source preparation, check the component helper and
its actual XTB output:

```sh
python3 scripts/branding/check-names.py PLATFORM_CHECKOUT CHROMIUM_SOURCE --prepared
```

This also runs a synthetic regression through the multiprocessing entry point
and verifies ordinary localized branding still changes to Lune.
