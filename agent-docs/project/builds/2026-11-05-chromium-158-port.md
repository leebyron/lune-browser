# Chromium 158 integration work

Status: source preparation and GN generation passed; arm64 compilation started.
This is separate from the completed Chromium 157 UI diagnostic build. No complete
build, runtime check, or release validation of 158 has passed yet. The main lock remains
unchanged until a reviewed candidate is ready.

Target: macOS stable **158.0.8127.18**, Chromium commit
`6449d9f9a6a906edff724b7b220199b3fde4615c`, confirmed against Chromium Dash and the
archive's pinned dependency metadata. Both ungoogled and Helium still target 157
at this inspection. Lune continues to use their combined patch stack: ungoogled
commit `de09e0c70c6bc1ac83d4ecdfd0e82c7e250c9a3c` is an ancestor of core commit
`42da6c50c04f3b411879d5bdb1304f4d78ea9c81`. This port does not replace that stack
with stock Chromium.

## Inputs and workspace

Source: [imput's Chromium 158 archive release](https://github.com/imputnet/chromium-tarballs/releases/tag/chromium-158.0.8127.18).
The downloaded `SHA256SUMS` matches the GitHub asset digest
`8d12ad31273497cb5dee97c264e179b6fbc1b740d66a23de1617fee7535fb42c`.

| Verified input | SHA-256 |
| --- | --- |
| Base source archive | `3186d708deaa8dcf622b0f3ce696c8716894b1e047abf7afcef3117796461f34` |
| macOS arm64 host overlay | `fe8f6035fcbf735b8634d28cc5a34756a37450719a3bcd7cde1af7fa13ef17ff` |
| macOS arm64 metadata | `11337ad69b15d025d42c43ae87f8476ee54b2375da82859efe6cb1524ea08b4e` |
| macOS x64 metadata | `ec222d6ecbb31bf060b233c7eab0056a20cb5224aaca0dc30346ed20ed6fb9ec` |

The arm64 host overlay supports both target architectures. The x64 host archive
has not been downloaded; its metadata was retrieved for inspection. Onboarding,
search data, uBlock, and Sparkle archives retain their existing pinned hashes.

Ignored working directory: `.work/chromium-158/`. Native Git clones under `macos/`
and `macos/helium-chromium/` use local `integration/chromium-158` branches based on
the UI candidate's platform and core inputs. Core work is checkpointed on
`integration/chromium-158/helium`; these are not locked build inputs.
`downloads-arm64.ini`, archive metadata, and preparation logs are retained there.

## Preparation and patch-port progress

Strict binary pruning initially stopped on 29 paths absent from Chromium 158.
All previously pruned inputs were restored from the verified archives before
regenerating the pruning and domain-substitution lists with upstream tooling.
The JPEG XL dither-data exclusion now follows `jxl-v0_7` to `jxl-v0_8`; an obsolete
Windows toolchain-file exclusion was removed after confirming the file is gone.

Reviewed core pruning changes add 120 paths and remove 29; domain-substitution
changes add 103 and remove 160. New host-overlay and Sparkle vendor paths were
excluded from the core lists to preserve their separate platform treatment.
Removed domain-list entries that still exist were checked against the unchanged
upstream substitution rules. Strict pruning now passes. Configuration and list
changes are retained in core commit `4074a04d`.

Core commit `d5acb513` adapts the initial privacy patches for changed declarations,
Google URL helpers, profile-avatar checks, GCM startup, and AI integration. The
AI patch also disables Chromium 158's new ScreenAI-backed text-detection binding,
while preserving unrelated lazy service initialization.

Core commit `f139ea99` adapts the Safe Browsing compatibility patch. This preserves
its existing disabled-service behavior across changed checks and moved GN
entries. Chromium removed the entire V2 security-survey handler; its obsolete
hunks were retired after checking both implementation and declarations. The
remaining survey handler is still disabled by the original patch. The cloud
content-scanning test dependency moved into a conditional and is removed there.

Core commit `3fb9b0b3` ports the unused-preferences cleanup across 20 conflicting
files and removes six newly introduced syncable Safe Browsing preferences plus
the new settings allowlist entry. Three obsolete TurnSyncOnHelper file sections
were retired after confirming those files are absent from the verified source
archive inventory and the replacement helpers do not contain those pref uses.

Core commit `1e1a0317` adapts seven additional patches:

- JavaScript optimizer text now initializes directly in `connectedCallback`,
  without observing the removed Safe Browsing preference.
- Hyphenation bundling is attached to the CfT condition, where the upstream
  bundle dependency now lives, with the Apple platform exclusion preserved.
- The maximum-connections dependency follows `browser_process_impl.cc` into
  the new `core` GN target. Connection-limit behavior is unchanged.
- Intranet probing and suggestions-URL editing retain their behavior across
  upstream check changes.
- Extension-sidebar promotions and the privacy-guide promo remain removed
  despite the new helper names and preference observer API.
- Last-tab preservation follows the new tab-handle callback: count live handles,
  add a fallback tab when requested, then resolve handles into pointers under
  the reentrancy guard. Native behavior still needs runtime validation.

Core commit `7f44b696` adapts eleven more patches:

- Popup-to-tab conversion follows the new disposition enum and moves the removed
  Mojo traits behavior into renderer/browser navigation entry points. The browser
  conversions run after parameter validation. Flag-on/off popup behavior and other
  Mojo disposition consumers still require a full behavior audit and runtime tests.
- TLS GREASE retains its command-line toggle; the separate signature-algorithm
  GREASE API and feature guard no longer exist in Chromium 158.
- MRU cycling, service preferences, and the service-schema notice follow changed
  headers, command handling, and checks without dropping their features.
- Onboarding's generated-resource dependency follows the consolidated browser GN
  target; the dedicated onboarding target and PAK dependencies remain intact.
- Both search-engine dialog subtitles use Helium's randomized-list explanation,
  including Chromium 158's newly added picker subtitle.
- Private sync follows the single-encryptor API, updated consent cleanup, static
  history metrics helper, and extension API registration changes. Existing vault
  event/permission IDs remain unchanged and the new upstream event is preserved.
- Google history-sync eligibility moved from the factory into WebHistoryService.
  Helium's disabled Google-upload check now applies at that new location, covering
  both construction and subsequent sync-state changes.

Core commit `72de29a6` adapts twelve further patches:

- Reserved keyboard shortcuts now live in Chromium's shared accelerator command
  table. The copy/inspect, DevTools, DevTools toggle, and tab-search reservations
  remain. Native shortcut behavior and the upstream accelerator unit-test
  expectations still need validation/adaptation before the final build gate.
- Default-browser rejection, extension downloads, bangs, update-channel selection,
  autoscroll, and uBlock resources retain their features across changed contexts.
- Spellcheck's Helium services dependency follows its new `spellchecker:impl`
  target; that target already depends on the profile implementation.
- Chromium removed the Journeys flag and hardcoded the desktop default in Config.
  Helium's disabled default now applies there, retaining the service's early exit
  before backend/observer setup.
- Context-menu cleanup includes the newly inserted Indigo entry in the simplified
  page-menu block and follows the new reading-mode visibility helper.
- Toolbar cleanup preserves newly inserted upstream actions while removing the
  same unsupported actions as before; a complete toolbar audit remains pending.

Core commit `1a7f116a` adapts seven further patches:

- uBlock component registration and allowlisting retain the same IDs and resources
  alongside Chromium's new WebUI NTP declarations.
- Core, canvas, audio, and hardware-concurrency noise retain their implementations
  across changed Blink feature declarations and header lists.
- Offline audio noise runs before resolving the rendered buffer promise, retaining
  Chromium 158's new queue ownership and teardown/reentrancy guards around Resolve.
- Global Privacy Control keeps its independent per-context setting alongside the
  upstream UnboundedElementPrivilege enum, without changing that privilege model.
- The adjacent-new-tab preference retains its insertion behavior with updated
  includes.

Core commit `f818b22e` adapts fifteen more patches:

- Tab hibernation, multi-tab URL copying, muting, profile avatars, update-toast
  suppression, component fixups, shortcuts, and password-manager policy retain
  their implementations across changed declarations and surrounding code.
- Close-tabs-to-left follows Chromium's new handle-based candidate list. Menu
  enablement and execution use that same list, preserving pinned-tab, selected-tab,
  split, and focused-group exclusions. Native behavior remains unvalidated.
- The removed side-panel flyover flag is replaced by the shared panel animation
  policy. macOS retains upstream continuous resizing and arm64 surface sync;
  other platforms use continuous resizing instead of clipping. The shared policy
  also affects the vertical tab strip and needs platform behavior validation.
- Glow-up features retain their selected defaults; WebUI rounded icons are now
  already enabled upstream, so that redundant change is no longer needed.
- Force Paste uses metric ID 174 and raises the maximum to 175, preserving
  Chromium's newly assigned Indigo ID 173 in both C++ and the metrics XML.
- Experimental WebUI removal follows the shared code-cache resource list, now
  also consumed by macOS's separate cache PAK. The removed location-bar-actions
  file was confirmed absent from the verified archive inventory; its old image
  resource substitutions are obsolete. The remaining consumers stay adapted.
- Lazy session restoration preserves Chromium's new ephemeral-group handling
  alongside Helium's deferred-load policy and saved-group checks. Runtime
  restoration, activation, split, and group behavior still require validation.

Core commit `1375f659` adapts ten Settings patches:

- Autofill-page suppression and search-help-link removal follow the new Lit
  settings-main template, preserving the existing disabled/removed UI behavior.
- Chromium removed the notification-page Safety Hub property and template module;
  those obsolete hunks were retired after inspecting both current files. The
  remaining Safety Hub route and entry-point suppression stay applied.
- Custom shortcuts retain their strings, feature gate, handler factory, receiver,
  frame-interface registration, and TypeScript/GN dependencies alongside the new
  upstream settings-search interface and accessibility Mojo resources.
- Settings icons retain the same replacement artwork. Search suggestions, profile
  avatars, privacy noise, and network/security settings follow changed imports,
  checks, string declarations, and the Secure DNS toggle's synthetic pref binding.

Core commit `29259af3` adapts eight new-tab and tab-chrome patches:

- The clean new-tab page follows upstream composebox/import changes while keeping
  Helium shortcuts, customization, and theme attribution. TypeScript parser checks
  passed for the new-tab entry point, app, and Lit template; this is syntax-only
  evidence, not type checking or runtime validation.
- Tab sizing and group-header padding preserve the new upstream unfocus chip.
  Toolbar tab search preserves the separate organizer action when enabled.
- App-menu changes retain the new scheduled-restart menu entry. Toolbar categories,
  multi-contents GN dependencies, frame corners, and panel clipping follow the
  current source structure.

Core commit `dc415a20` adapts seven notification and styling patches:

- Dead-toolbar-action removal preserves the new tabs-from-other-devices action and
  keeps the autofill action-existence guard with the new controller accessor.
- Helium's disabled-extension-download command uses value 24, preserving upstream
  Windows OPEN_WITH value 23. The corresponding metrics enum is updated too.
- Toasts retain Helium's scale/fade animation and remove the replacement upstream
  vertical-offset animation fields. The window-movement regression test now drives
  the layer animator; the width test uses Helium's shadow-free margin. These test
  adaptations have not yet been compiled or run.
- Compact infobars preserve upstream queued-count pill handling and focus
  restoration. Color mixers, status-bubble setup, and incognito text are adapted
  without changing their intended Helium behavior.

Core commit `2c8892b9` adapts nine layout and shortcut patches:

- Custom shortcuts retain Chromium's macOS-only Escape handling and ChromeOS
  unified-lock-controller logic. Vertical layout state keeps the collapse-action
  refresh when releasing its state lock.
- Layout settings, horizontal tabs, toolbar dependencies, dynamic and compact
  layouts follow current source locations. The minimal location bar keeps the new
  upstream placeholder refresh before updating steady-state text alignment.
- Ctrl/Cmd-S behavior and collapse-shortcut removal follow the reorganized
  accelerator tables; the macOS mappings remain in their platform files.

Core checkpoints `8838affd` and `8996e539` finish the vertical/Zen layout,
native-frame-materials, debugger-warning, and progress-bar ports. Preserve 158's
organizer-panel behavior, new macOS first-frame input-context deferral, current
permission dashboard, and current GN target boundaries. The obsolete Polymer
ripple mixin is absent from both the source archive inventory and source tree;
the Lit and native ripple changes remain.

Platform checkpoint `e07137b0` pins core `8996e539` and completes strict patch
application. The adaptations preserve:

- Keychain failure protection for both default (`v10`) and custom-profile (`v11`)
  keys, including 158's custom salt and unavailable-default-key provider.
  Key reads retain bounded transient retries and stop profile startup on failure.
- Native translation menu behavior with noncolliding UMA values (175 and 37),
  Sparkle linking, macOS fullscreen behavior, and remaining Safe Browsing guards.
- Sidebar address-bar hit testing alongside the organizer panel; density-aware
  group headers and pinned rows in Chromium's newly split vertical layout files.
- Collapse sizing and frame attachment while retaining upstream animation and
  browser-test changes. The old duplicate group-header dependency fix is already
  included in the adapted comfortable-tab patch.
- Visual-switcher thumbnails, command-bar ownership, and link peek. Explicit
  `window.open()` split requests keep Chromium's split behavior instead of being
  intercepted as featureless popup previews.

**All 397 patches apply with zero fuzz.** No series entry was skipped or forced.
At this checkpoint, source substitutions/resources, GN generation, compilation,
and runtime checks were outstanding for 158. This is patch-application evidence, not proof that the
adapted code compiles or all behavior is correct. Component branches are published
at `integration/chromium-158/{helium,macos}`; they are not release inputs.

The separate 157 UI build completed 41,297 actions in 2h4m53s. Its headless smoke
test passed page loading, JavaScript, profile persistence, 18 default preferences,
both Helium credits, Kagi-first recommendation with paid-account disclosure, and
the packaged icon hash. See [UI integration](../xelium-ui.md). This does not satisfy
the Chromium 158 build requirement.

All selected UI features, Lune defaults, Kagi recommendation, Helium attribution,
and artwork remain required in the forward-port. New immutable component tags
and the main lock will be published only when the candidate is ready.

## Upstream work-in-progress check

Checked 2026-11-05: the upstream repository exposes only `master`,
`PF4Public-patch-1`, and `pf-bin`; none is a Chromium 158 port. The six open PRs
contain no version-update PR. `master` is still `de09e0c7` (Chromium
157.0.8103.38). Ahrotahn authored the recent version updates; their public
`major` branch has the same 157 commit, `refresh` remains at the previous 156
update, and the `bugfix` branch contains older work. No publicly available 158
port was identified in these sources; this does not rule out unpublished work
or work elsewhere in the fork network.

Sources: [upstream branches](https://github.com/ungoogled-software/ungoogled-chromium/branches),
[open PRs](https://github.com/ungoogled-software/ungoogled-chromium/pulls),
[latest major update PR](https://github.com/ungoogled-software/ungoogled-chromium/pull/4032),
and [Ahrotahn's major branch](https://github.com/Ahrotahn/ungoogled-chromium/tree/major).
Prefer reviewing and incorporating an upstream 158 port when one is published;
retain Lune's independent stable target and full feature scope.

## Source preparation and compilation

Domain/name substitutions, localization, Lune display-name handling, versioning,
and resource generation subsequently passed. GN initially rejected unconditional
Chromium 158 OCR test dependencies while Screen AI is disabled by the ungoogled
configuration. Platform commit `7edc1a7cc9629cd529a9ca34e2aeb8c8dff14def` adds
`helium/ui/chromium-158-build.patch`, guarding those two test dependencies with
`enable_screen_ai_service`. The series now has **398 applied patches**.

GN generation passed: **36,640 targets from 5,027 files**. The actual onboarding
generator passed all **80 messages**, with identical header and TypeScript output
with and without an XML declaration. The arm64 compilation began against core
`8996e5399efc7694ffd155ae9e5098eb4450345b` and the platform commit above, using
Xcode 27.2/27B52 and the pinned 158 toolchain. It runs with ten compile jobs and a
sanitized environment; Sparkle and special branded entitlements remain disabled.
No signing or publication is part of this build.

Local evidence: `.work/chromium-158/post-patches.log`, `gn-gen.log`,
`development-build.json`, and `build.log`. The GN arguments hash is
`05f104d8ff57cff89116b982222f7b7b99e2ba7587d1d328a116f865370b5de6`.
Compilation and 158 runtime checks remain incomplete; the main lock still pins
the earlier development candidate.

Focused GN header checks identified two missing direct dependencies in the
browser-view and link-peek targets. Platform commit
`d48a5b3e8f55ead37f1840f4fbbd09dd8d119b50` adds those dependencies in a separate
patch (399 total). Checks now pass for OSCrypt async providers, browser view,
vertical-tab-strip region, common tab views, and all Helium UI targets.
Compilation was deliberately interrupted for this fix and resumed from cache;
the first log and build metadata remain under `*-before-dependency-fix.*`.

The main orchestration validator now supports an explicit, hash-reviewed
Chromium forward-port without relabeling the upstream ungoogled version. It
also rejects source archives for a different version/host. All 29 guardrail
tests and validation of the unchanged current lock pass. The actual 158 input
lock remains pending build/runtime verification.

The smoke runner now asserts the requested architecture and exact Chromium
version for both driver and running browser. CI invokes it after compilation.
The strengthened test passes against the explicit 157 diagnostic artifact, and
negative checks reject that artifact when 158 or x86_64 is requested. This is
test-harness evidence only; the 158 app is still compiling.

## Internal Lune artwork

The owner found Helium artwork inside the diagnostic app. Platform commit
`97336e6642a0759ffa6245690a59efc962dc4d82` replaces all 34 upstream logo-resource
destinations and two onboarding assets. Color and monochrome vectors, scaled
PNGs, and light/dark wordmarks now use the Pelagic Signal paired lunes. A separate
Lune patch replaces onboarding's embedded logos in welcome, services, import,
and finish screens. It removes the unused Helium asset catalog from app/helper
bundles and selects Lune's `.icns` in notification helpers too. Helium attribution
remains; partner text explicitly names Helium instead of falsely claiming that
upstream partnerships fund Lune.

The new patch reapplied without fuzz (400 total). GN generated 36,639 targets
from 5,027 files. Onboarding's generated resources and the native vector targets
built successfully. The resource coverage check matches all 36 prepared assets
against their committed inputs. Re-rendering the existing app icon reproduces
its original SHA-256 exactly:
`3b6224273905dc9a7c789f9a332c81982d75becf75793e1d47e0d152692f3dc0`.

The new `--internal-icons` smoke option reads the packaged About and onboarding
images and checks their Pelagic Signal pixels, as well as helper bundle icons.
Its About-page check rejects the old 157 app's Helium logo as expected (zero
matching colors). Positive runtime validation awaits the 158 build. These are
resource/guardrail results, not a completed browser build or native UI validation.

Local evidence: `internal-icons-resources.json`, `internal-icons-targets.log`,
`internal-icons-targets-confirmed.log`, and `old-icons-negative-smoke.json` under
`.work/chromium-158/`. Compilation was paused deliberately to apply the change,
then resumed from cached outputs. The previous log/metadata are retained as
`build-before-internal-icons.log` and `development-build-before-internal-icons.json`.

Final source inspection also identified two inline `cr:chrome-product` SVG paths
in shared WebUI. Platform commit `34193a6e5d30abaf1edfe29a687cc98122e2aba3`
adds `lune/webui-logo.patch`, replacing both with the same Lune monochrome
geometry. The patch reapplied without fuzz (**401 total**); the coverage checker
now compares those paths with the generated SVG too. Compilation resumed from
this final component commit. The preceding run is retained under
`*-before-webui-icons.*`. Shared WebUI compilation and final runtime checks remain
part of the full build in progress.

The shared WebUI resource target subsequently passed. The full build exposed a
separate PDF lint error: ungoogled's `disable-ai.patch` removes the OCR progress
toast, but Chromium 158 still declares it in the TypeScript interface and calls
it from a plugin event handler. Platform commit
`29adb275d03bd66b195e9cccc93634985ba1c437` removes those obsolete bindings/imports
and ignores the disabled feature's progress notification. PDF TypeScript
compilation and lint both pass (`pdf-fix-targets.log`). The patch reapplied without
fuzz (**402 total**). The full build resumed from this commit; its preceding
failure evidence is preserved under `*-before-pdf-fix.*`.
