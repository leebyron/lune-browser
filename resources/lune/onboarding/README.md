# Onboarding assets

Copied from Lune website/public/assets: lune-mark.svg, wallpaper.jpg,
fonts/inter-latin.woff2, and fonts/syne-latin.woff2. The mark remains untiled.

Font licenses are the upstream Google Fonts OFL files:
- https://github.com/google/fonts/blob/main/ofl/inter/OFL.txt
- https://github.com/google/fonts/blob/main/ofl/syne/OFL.txt

Both licenses are also bundled as onboarding WebUI resources.

The import graphic separately maps the existing square `lune/product_logo.svg`
to `lune-app.svg`; the welcome mark stays transparent. Wallpaper and fonts are
served entirely from the packaged WebUI resources, including offline.

## Finished wallpaper variants (November 9, 2026)

`wallpaper-light.jpg` and `wallpaper-dark.jpg` are baked color treatments derived
from the original website cyanotype with the built-in image generation tool.
The owner selected blue botanical silhouettes on pale paper for light mode; dark
retains light specimens against deep blue. Both preserve an open center for text.
The website uses identical JPEG bytes. No runtime blending or color wash is needed.
The 64x64 center averages are #F1F6F2 and #012034; setup's root/body/main use these
colors so its fade and reserved toolbar band match the artwork.

Prompt summary: preserve cyanotype botanical framing and quiet center; light uses
muted Prussian-blue impressions on pale sage paper; dark uses visible muted cyan
specimens on deep Prussian blue. No text, UI, borders, or extra objects.

The light variant uses the owner-requested softer blue specimens, approximately
half the initial contrast against the pale paper, baked into the JPEG.

Latest owner-approved light refinement: near-white paper with a small contrast
increase from the palest draft (requested +20%). The final sampled center is
#F1F6F2. Dark remains #012034. Website root/body/stage and setup root/body/main
all match their respective asset center. Built-in image generation prompt: keep
the near-white background unchanged and gently deepen only the pale blue
cyanotype specimens by approximately 20%, preserving all composition and detail.
