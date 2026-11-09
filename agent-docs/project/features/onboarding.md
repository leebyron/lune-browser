# Onboarding refresh

Status: rebased local candidate on the reviewed stack now pinned by main.
Latest arm64 build, packaged flow, native palette comparisons, migration and
restart persistence, and browser smoke checks pass on both architectures
(Intel under Rosetta).
The November 9 import-edge, navigation, sidebar theme choices, normal-launch
floating-toolbar behavior, search ordering, and intro refinements pass the arm64
build and packaged flow. Final Intel validation is running.
Owner visual acceptance remains pending.
No onboarding commit, release, development-lock update, or push.

The candidate is developed in the existing prepared Chromium 158 tree at
`.work/chromium-158/macos/build/src`, with refreshed platform patches on
`onboarding-refresh` in `.work/menu-retention/platform`, based on accepted
`01905fc411a170d7498ea04b3e315111bb806925`. The distribution patches are
`lune/onboarding-refresh.patch` and `lune/internal-url-scheme.patch`. The separate
`lune/opposite-side-panels.patch` hides independent panel position controls;
the reviewed base supplies opposite-side placement. `lune/theme-choices.patch`
adds native macOS System colors and keeps the Lune brand palette distinct.
`lune/sidebar-theme-choices.patch` exposes System/Lune first in the Appearance
color picker, using native palette samples for their swatches.
`lune/pinned-floating-header.patch` retains floating controls when pinned, without
requiring the experimental content-inset flag.
`lune/system-tab-selection.patch` corrects System theme pinned-tab selection to
AppKit selected content background/text, with unemphasized variants for inactive
windows; other theme palettes are unchanged. Both architecture builds pass;
active-window selection was inspected on arm64. Inactive-window acceptance remains pending.

## Behavior

- Internal-page alias, formatted addresses, built-in suggestions, and tab-search
  protocol labels use `lune://`. Chromium's underlying `chrome://` WebUI URLs
  remain available for internal callers.
- Welcome uses the website's light/dark colors, locally bundled Inter/Syne fonts,
  and a larger transparent double-lune mark. Its circles open from coincident
  centers over 1.4 seconds. The background starts at 1.3 seconds and fades over 1.6 seconds; all content
  below the logo reveals together at 2 seconds over 1.5 seconds. The fades overlap.
  The logo starts 50 px above center at 120% size. After 200 ms, the welcome
  group rises and the logo eases to 100% over 3300 ms, ending with the text fade.
  A smaller 16 px wallpaper drift supplies parallax over 3500 ms.
  Wallpaper grows from full cover to 105%, with clipped overflow and no empty
  edges. Light mode uses the website's #E7EDE3 ground and 10% wallpaper strength,
  with the owner-requested screen blend so the image lightens the ground; dark uses
  45% strength with 70% image brightness. The complete tinted wallpaper fades
  over its sampled 64x64 center average (#E7EDE4 light, #0A2B44 dark), preserving
  the center brightness throughout. Reduced motion shows the final state
  immediately. Content remains scrollable on short windows.
- Heading is “setup lune”. Description is “Make Lune your own, import from another
  browser, or start with the defaults.” Both intro buttons use regular 16 px text, matching navigation size. Setup uses an accent-color button with its arrow on the right;
  Use defaults uses the website's outline button without an icon.
- Automatic browser updates use the existing persistent preference, defaulting
  on for fresh profiles and preserving saved opt-outs, without explanatory text.
  Browser update permission is independent of optional
  Helium services; the corresponding Settings control remains visible when
  services are off, with corrected disclosure text.
- Attribution reads “Built on Helium browser, with thanks to its authors and
  contributors.” The privacy/terms and defaults disclosure use Helium's compact 1.2 line
  height, without a gap between them.
  Existing Helium privacy/terms links and default-services
  disclosure remain below it.
- Services uses Helium's logo and omits browser-update controls and discussion.
  Custom Setup starts with services disabled; Use defaults enables them.
- Import retains the square Lune app artwork with a lighter top and darker bottom
  edge directly on the icon, with no surrounding padded outline. The in-page
  action says “Import” without an icon; bottom navigation says “Next” with an arrow.
- Startpage is the native fallback search provider when there is no saved choice.
  Saved, imported, and managed choices retain their existing precedence. The
  frontend also handles a missing selected engine using an eligible Startpage entry.
  Choices start with Startpage, Kagi, and DuckDuckGo.
- The default-browser setup step is removed. The existing sidebar prompt remains
  responsible for offering to make Lune the default browser.
- Finish becomes “Customize Lune”, with an adjustments icon and the shared
  configuration header spacing/wrapping. Four dropdowns expose Appearance
  (Auto/Light/Dark), Theme (System/Lune/Grayscale and all 13 standard colors),
  Tab sidebar (Left/Right), and Show toolbar (On hover/Always/Always cover).
  Native ThemeService observation keeps the theme choices synchronized with
  changes made in the Appearance panel. A custom installed theme remains visible
  as Custom rather than being mislabeled as Lune.
- System enables the existing device-theme preference on macOS. The native color
  mixer resolves AppKit semantic window, control, label and accent colors under
  the selected light/dark appearance, and floating glass has no added theme tint.
  Lune selects the baseline palette: Chlorophyll Daylight/Pelagic Signal. Explicit
  grayscale and accent choices are excluded from brand overrides. New macOS
  profiles use Lune's baseline instead of upstream's implicit grayscale default.
  A one-time migration preserves the brand appearance of older implicit-grayscale
  profiles. Subsequent explicit grayscale choices persist across restarts; macOS
  baseline restoration no longer runs through the theme-reset path.
- Show toolbar uses the existing pin and overlay preferences, matching Settings
  and the native menu. Always retains the floating glass toolbar and reserves
  52 pt above page layout. Always cover permits viewport-fit=cover pages to draw
  underneath it and supplies the corresponding safe-area inset. On hover restores
  the full page viewport. No feature launch flag is required.
- The final page opens Appearance and uses the shared Back/Done controls, with
  a checkmark on Done. Back closes the panel; Done records completion and opens
  the new-tab page. Top-level navigation away also closes the panel.
- The reviewed base keeps default auxiliary-panel placement opposite the tab
  sidebar. Its existing per-panel overrides are retained. Onboarding hides the
  independent panel-position section in Settings and does not replace the newer
  native placement logic.

## Assets and validation

Website assets are copied into platform `resources/lune/onboarding/` and mapped
through `resources/lune_resources.txt`; nothing loads fonts or wallpaper from the
network. The upstream OFL licenses accompany both fonts.

Evidence lives in `.work/onboarding/`. The frontend passes Svelte checks with zero
errors or warnings. Development-preview checks cover light/dark colors, 360/480 px
widths, short-window scrolling, reduced motion, selected Kagi, services-off flow,
and appearance open/close messages. These mocks do not establish native panel
behavior. Strict zero-fuzz replay of the new patches against their recorded
prepared-source baselines matches the changed source files; this is not a fresh
full Chromium preparation.

The arm64 build and page-loading/profile-persistence smoke test pass. Packaged
flow checks verify the exact welcome copy, default-on update switch, saved update
opt-out, services-off flow, selected Kagi, a subsequently selected DuckDuckGo
remaining selected on reopening setup, completion persistence, and both Setup /
Done and Use defaults reaching the new-tab page. The real appearance panel reduces
the content width and Back restores it.

Live arm64 checks in **Lune Setup Test** confirm typed `lune://settings/` and
`lune://setup/` navigation, Lune scheme in the address field and suggestions,
selected Kagi, color application, and panel dismissal on navigation. The fresh
review profile also shows the existing Make default browser sidebar button.
Automation navigates using underlying `chrome://` URLs: direct ChromeDriver
navigation bypasses the inherited alias rewrite in the normal browser navigator.
The native address-field route is verified separately.

The eight patches pass platform patch lint and strict replay of all 55 affected
files. The new native theme and onboarding implementation units compile, and
frontend checks report zero errors or warnings. Vite clears its own generated
output directory on rebuilding, avoiding stale hashed chunks exhausting the
existing WebUI resource-ID allocation.

The final arm64 build passes the full packaged flow: exact dropdown choices,
all standard colors, appearance modes, header visibility, left/right tabs,
panel cleanup, intro timings, compact policy line height, and local-only assets.
Native System colors match independently sampled AppKit window/control/label/
accent colors in light and dark modes. Lune matches the brand palette values;
Grayscale remains neutral. Legacy implicit-grayscale migration and explicit
Grayscale persistence pass. System/Dark/right/Always survive restarting the
profile. General page-loading and profile-persistence smoke checks also pass.
Evidence: `.work/onboarding/runtime-Default/report.json`,
`.work/onboarding/theme-Default/report.json`, and
`.work/onboarding/smoke-Default-final.json`.

The latest Intel build and identical packaged flow, native palette, migration,
restart-persistence, and smoke checks pass under Rosetta. Results are recorded in
`.work/onboarding/final-Intel.json` and the corresponding Intel reports.

On November 9, 2026, live arm64 inspection in **Lune Setup Test 2** verified the
welcome layout and tight policy text, selected Kagi, services off, glass-edged
import icon, four dropdowns, System light and Lune light/dark colors, opposite
Appearance panel placement when moving tabs right, Back closing Appearance,
Done opening the new-tab page, and typed `lune://setup` navigation. The preview
is left on Welcome for owner review. This inspection is not owner acceptance.
Native Intel hardware acceptance and older macOS behavior remain unverified.

Latest requested refinement: Startpage is first and the new-profile/missing-choice default, followed by Kagi and DuckDuckGo. Saved choices remain intact. The welcome group starts with its logo 50 px above screen center, pauses 200 ms, then rises and shrinks the logo from 120% to 100% over 3300 ms with ease-in/out, finishing with the single content fade. The wallpaper drifts upward 16 px over 3500 ms with overscan to cover all edges. Final arm64 packaged validation passes, as do native System/Lune swatch comparisons in both schemes and responsive motion/scale, typography, and reduced-motion checks. Lune Setup Test 3 is refreshed with the final source. Intel validation is running.

The live website CSS was fetched November 9 and confirmed the light-mode 10%
wallpaper/luminosity override. The owner then requested a lighter mix: setup uses screen blending instead of
luminosity, retaining the local wallpaper and 10% strength. Its recomputed
64x64 center average is #E7EDE4. Both final architecture builds pass.

The owner requested production behavior on November 9: `helium/ui/toolbar-inset.patch`
removes the runtime prototype switch and its renderer forwarding. macOS browser
preferences now drive the existing 52 pt inset and cover handling directly;
other platforms retain their prior viewport-fit parsing. Onboarding, Settings,
and native menus offer On hover / Always / Always cover with matching saved
preferences. Both architecture builds pass; the candidate is not yet release-validated. A source audit
of chrome/content/Blink and platform/core patch/configuration inputs found no
other Lune-specific feature switches or custom GN feature toggles.

## November 9 production-mode validation

The final arm64 build passes. Packaged onboarding checks pass with Startpage
first/default, Kagi second, DuckDuckGo third, saved-choice retention, regular
16 px intro buttons, the delayed 50 px-above-center / 120%-to-100% logo motion,
and all three toolbar modes. The restored issue #11 renderer fixture passes
without a prototype flag: 52 pt inset, cover/contain transitions, safe-area values,
scroll-under pixels, nested scroll, click alignment, live changes, defaults, and
restart persistence. Settings mode/side selection, backend synchronization,
opposite-panel invariant, and restart checks pass. The inherited limitation
that ordinary-page root background images do not extend into the reserved band
remains; cover-mode images do extend when opted in.

Lune Setup Test 3 was refreshed and launched without the former feature flag.
Live arm64 inspection verifies the lighter locally bundled background, Startpage
selection, System-first swatches, System selected-tab fill/text, and the visible
Always toolbar reservation. It is left on Customize Lune with System and Always
selected. Native inactive-window selection acceptance remains unverified.
The final Intel build passes; final no-flag runtime checks under Rosetta are in progress. No onboarding commit,
push, development-lock change, release, or deployment has been made.

The option audit also identified inherited runtime controls for bookmark-bar
visibility, the Extensions menu, and visual tab-switcher capacity. Lune disables
Chromium's AsyncLiveResize feature by default to keep native child windows and
content in the same resize transaction. None requires an extra flag to enable
the toolbar inset or cover behavior. These runtime controls are distinct from
standard Chromium GN build configuration.

## Local cyanotype asset refinement (November 9)

The owner selected blue cyanotype specimens on pale paper for light mode and
requested finished assets shared with the website, without runtime blending.
The local candidate adds wallpaper-light.jpg and wallpaper-dark.jpg, removes
setup and website wash/blend layers, and keeps the existing reveal animation.
Root/body/main colors match the 64x64 image-center averages #F1F6F2 / #012034.
Both surfaces use identical local JPEG bytes. Original reference artwork remains
retained. Website and packaged setup light/dark screenshots, frontend checks,
patch lint, both architecture builds and the arm64 packaged flow pass. Intel
packaged-flow startup failed twice before assertions (DevToolsActivePort missing);
no final Intel runtime pass is claimed. Evidence is under
.work/onboarding/cyanotype/. This candidate
is not yet committed or deployed.

The light variant uses the owner-requested softer blue specimens, approximately
half the initial contrast against the pale paper, baked into the JPEG.

Latest owner-approved light refinement: near-white paper with a small contrast
increase from the palest draft (requested +20%). The final sampled center is
#F1F6F2. Dark remains #012034. Website root/body/stage and setup root/body/main
all match their respective asset center. Built-in image generation prompt: keep
the near-white background unchanged and gently deepen only the pale blue
cyanotype specimens by approximately 20%, preserving all composition and detail.
