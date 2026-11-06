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
