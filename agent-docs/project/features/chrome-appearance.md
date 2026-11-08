# Native chrome appearance

Work for [issue #7](https://github.com/leebyron/lune-browser/issues/7), based on
the accepted media-toolbar platform head
`41312cdfc8fa0ec20a49396fb3355c9a01024a8c`. The local candidate is on
`stable-chrome-appearance`, imported as `topic/stable-chrome-appearance`.
The current signed platform head is
`86aba2f195484f47b86093e9ab71d3d22205f4b0`. It is not in the development lock or
published builds.

## Reproduction

A local white/black page reproduced the reported failure in the media-toolbar
preview: regular glass became dark over black content while the address text and
native/Views toolbar icons remained dark. Native inspection reported Aqua for
the surface, glass, and explicitly overridden content view. It is therefore not
safe to infer the composited glass treatment from the glass view's explicit
appearance alone.

An AppKit comparison reproduced both directions: Aqua glass with dark text over
black content, and Dark Aqua glass with light text over white content. Removing
the explicit content-view appearance let native text follow the actual glass
treatment. Apple's [AppKit guidance](https://developer.apple.com/videos/play/wwdc2025/310/)
requires foreground content inside `NSGlassEffectView.contentView` to receive
its legibility treatment. Lune's Views toolbar and detached sidebar are hosted
in separate transparent windows, so they also need an appearance bridge.

## Behavior

On macOS 26+, the address, navigation, trailing actions, floating sidebar,
Customize close button, and Command-T all retain native regular Liquid Glass.
The browser's Light/Dark/Device choice supplies a neutral 80%-opacity layer
behind the glass in fixed mode. This bounds the sampled background luminance
while retaining some page color and the native glass effect. The public tint
property alone did not keep both Light and Dark stable in the native comparison.
This is a composition policy, not an undocumented glass adaptation override.
Older systems retain the native visual-effect fallback.

At the owner's request, Customize's Appearance section has a **Content aware**
toggle. It stores the independent profile preference
`helium.browser.content_aware_chrome` (default true; explicit saved false remains off), without replacing the
Light/Dark/Device choice. Enabling it hides the neutral backing so the same glass
samples the page directly. Older systems do not expose the toggle.

Native foreground controls inherit the glass content appearance in both modes.
A content-view callback supplies each trailing-action/sidebar widget with its
own effective appearance. Semantic foreground resolution uses that appearance
ahead of the profile fallback and invalidates the widget's concrete color/image
caches on changes. This does not change the browser theme. Weak widget references,
per-native-host storage, and clearing callbacks during teardown keep state local
to its owning surface. Extension-provided colored artwork stays intact.

The same material, content view, and controls stay attached across toggles.
This preserves address editor focus, selection, dimensions, reveal state, and
clipping. The floating sidebar uses the same glass/backing policy and bridges
its actual appearance to its tabs and native pin control. Command-T applies the
same policy when opened.

The first preview substituted popover material in fixed mode and reparented the
content view when toggled. The owner confirmed adaptive icon colors worked, but
reported disappearing address controls when disabling the option and rejected
the material change. Native inspection confirmed that reparenting collapsed the
address content view to zero height and Customize close content to zero width.
The persistent glass revision removes both the substitution and reparenting.

## Theme tint

At the owner's request, the floating sidebar, address, navigation, trailing
controls, and Customize close glass use AppKit's public `tintColor` property.
The tint uses the HSL midpoint of the owning browser theme's light and dark
`ui::kColorSysPrimary` accents at 7% alpha. Hue follows the shorter circular
arc; achromatic endpoints retain the chromatic endpoint's hue. Both variants
come from cached Chromium color providers using the same owning browser key,
changing only the scheme. Custom themes, user colors, and incognito palette
settings remain in that key. No palette values are duplicated in the feature.
The tint is identical in Light/Dark/Device; AppKit supplies the material tone,
and foreground controls continue to follow the actual glass appearance.

Existing surfaces update immediately on theme changes, even with the header
hidden. New surfaces receive the same tint when created. Unchanged colors do not
reapply the material property. This adds no overlays, timers, capture or pixel
sampling. Native material identity, attached controls, fixed/adaptive mode, and
reveal behavior remain intact. Earlier macOS visual-effect fallback and Command-T
are unchanged. A startup smoke run caught an early theme notification before
BrowserView widget attachment; tint lookup now tolerates the absent provider and
applies during surface setup. The native harness covers this initialization
case as well as theme tint changes with a live editor. The balanced tint passes
native checks on both architectures, including scheme
independence, custom-theme changes, hue wraparound, and achromatic endpoints.
The midpoint implementation passed full builds and browser smoke checks on both
architectures at 10%. Live inspection confirmed all five glass surfaces retained
identical sRGB tint components across Light/Dark with the selected Green theme,
while foregrounds continued to follow the native material. The final 7% strength
refinement passes both browser builds and native checks. Live arm64 inspection
confirms 7% alpha on all five surfaces with the same midpoint color. The full
settings smoke matrix was not repeated for the alpha-only refinement.

The first tint candidate used the near-neutral toolbar surface at 12% alpha.
Native inspection confirmed it reached every target surface, but the owner
reported that the sidebar change was imperceptible and header tint too faint.
The next candidate used the selected scheme's accent at 30% alpha. Both builds
and smoke checks passed, and live inspection confirmed tint on every surface.
The owner found it too intense and requested one shared tint across schemes,
using their HSL midpoint at one third of the strength. The current candidate
implemented that refinement. After reviewing the 10% preview, the owner asked
for 7%; the midpoint computation remains unchanged. The owner accepted the 7%
tint on November 8, 2026, then requested stronger header shadows and asked why
tint appears to disappear when the window loses focus.

## Header shadows and inactive windows

The next candidate adds AppKit `NSShadow` to the existing header material views:
24% black, 8 pt blur, and a 3 pt downward offset. Navigation, address, trailing
controls, and Customize close receive it; the sidebar and its toggle do not.
The shadow shares the material's existing fade and does not enlarge hit regions.
An explicit rounded Core Animation shadow path updates only when bounds change,
including the address suggestions expanding vertically. Native `NSShadow`
ownership is necessary: direct layer shadow settings were reset by AppKit during
appearance changes. No new window, timer, polling, or page sampling is added.

Native checks cover the shadow silhouette, width/height changes, appearance
changes, reveal interruption, and absence of an added sidebar shadow on arm64
and x86_64 under Rosetta. Full browser builds pass on both architectures, along
with strict replay, patch lint, root validation, and changed documentation links.
The prior tint settings smoke matrix was not repeated for the shadow-only change.
The stronger-shadow binaries are built but the running preview still contains
the accepted 7% tint candidate without these shadows. Refreshing and visually
checking that preview awaits the Mac unlock; shadow visual acceptance is pending.

The tint code has no activation-dependent clearing or alternate color. Live
inspection confirmed the selected Green midpoint remains assigned at 7% while
the preview is active. The attempted deactivation did not change the app's active
flag, so it is not evidence of an active/inactive comparison. The Mac then locked,
blocking further visual inspection. Native inactive rendering is the likely
explanation for the owner's observation, but the exact transition remains to be
verified. The public macOS 27.2 SDK exposes no activity-state override on
[`NSGlassEffectView`](https://developer.apple.com/documentation/appkit/nsglasseffectview).
No workaround or inactive tint override was implemented.

## Validation

The final 7% midpoint candidate passes full arm64 and x86_64 browser builds and
native regression checks. The same implementation at 10% passed both
architectures' UI/settings/appearance/persistence smoke checks, including a
fresh-profile Content aware value of true and an explicit saved false after
restart. Intel checks run under Rosetta, not native Intel hardware.

Strict replay passes across 146 relevant patches and 17 changed source files,
including the production GRIT-aware name transform. Patch lint, root validation,
and GN header dependency checks pass. The repository's 44 unit tests pass. The focused native harness covers the
material implementations and appearance bridge.

Native regression checks pass on both architectures. They compile the actual
surface implementation, Command-T material construction, and appearance bridge.
They check profile/high-contrast appearances, owner isolation, editor focus and
selection, interrupted reveal/hide, sizing, sidebar hit behavior, callbacks,
cache invalidation, and clearing per-widget colors. The persistent-glass fixture
also starts at zero size, resizes, and toggles repeatedly while checking material
identity, content dimensions, editor and selection. These tests do not establish
compositor-level contrast or native Intel hardware acceptance.

Live arm64 inspection confirms that disabling Content aware preserves the center
pill's text/icons and regular glass; the owner confirmed this fix. The owner also
confirmed the preceding adaptive foreground implementation works for toolbar
icons. The floating sidebar remains under review: it looks more opaque and does
not invert light/dark with the page like the toolbar pills.

A standalone AppKit comparison reproduces this behavior for sidebar-sized regular
glass, with both square and rounded corners and with or without text content.
Apple documents that larger glass is more opaque, while smaller glass switches
between light and dark automatically in its
[glass sizing guidance](https://developer.apple.com/videos/play/wwdc2025/284/?time=188).
The clear-style comparison is more transparent but leaves native dark text on a
dark backdrop, so it is not a safe direct substitution. The owner requested
retaining the more opaque native material while adapting its color to the page.
A candidate followed the adjacent header glass, but the owner rejected it:
sidebar changes lagged the header transition and stopped when the header hid.
That coupling is removed. The owner then required native UI primitives and
rejected a proposed compositor-frame sampling approach because of CPU/power
concerns. No page capture, sampling loop, or hidden glass probe was implemented.

The final sidebar retains regular AppKit glass and its native large-surface
behavior. Its foreground still follows its own material. It is independent of
header visibility, but does **not** promise the toolbar's automatic light/dark
inversion. The public SDK exposes regular/clear styles, tint, geometry, content,
and interactivity; it does not expose a large-surface adaptation override.
The request for stronger sidebar adaptation remains a known native limitation,
not a verified fix. Fullscreen, system accessibility settings, and the complete
active/inactive browser matrix have not been rerun for this candidate.

```sh
python3 scripts/check-native-chrome-appearance.py .work/chromium-158/macos/build/src --arch arm64
python3 scripts/check-native-chrome-appearance.py .work/chromium-158/macos/build/src --arch x86_64
```

Local evidence and native comparison images are under `.work/glass-appearance/`.
The new label is an English source string; translations remain subject to the
existing [string review](string-review.md).
