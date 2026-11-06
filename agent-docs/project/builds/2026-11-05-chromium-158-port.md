# Chromium 158 integration work

Status (2026-11-06): the complete arm64 build and headless runtime smoke check
passed on Chromium 158.0.8127.18. Intel compilation is in progress. Native UI and
release validation remain incomplete. The main lock remains on the earlier 157
candidate until promotion; this workspace is a separate reviewed forward port.

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

## Intel preparation

The same prepared source at platform `29adb275d03bd66b195e9cccc93634985ba1c437`
also generates an Intel graph in `out/Intel`: 45,761 targets from 5,029 files.
Its arguments differ from the arm64 output only in `target_cpu="x64"` (argument
hash `8f4a52436f0d502d7ca1bc90c5e0aadd3ce42178ef2874710d1ea40485196f3e`).
All five focused dependency checks pass for Intel too: OSCrypt async providers,
browser view, vertical-tab-strip region, common tab views, and Helium UI.
Evidence: `intel-gn-gen.json`, `intel-gn-gen.log`, and `intel-gn-check.json` under
`.work/chromium-158/`. Intel compilation and runtime validation have not run.

After the branding changes, source checks still pass for defaults, Kagi, Helium
credits, and all 80 onboarding messages. Svelte checking reports zero errors and
warnings. Main's current renderer hash is refreshed and all 29 orchestration
tests pass. A candidate input lock is staged locally by `stage-lock.py`; it is
not promoted, and its proposed permanent refs have not been created. Refresh
that staging after any further source or review-document change.

## Shared encryptor compatibility

The next full-build failure was a stale `encryptors[1]` reference in Helium's
custom sync backend initialization. Chromium 158 removed the two-request barrier
and passes one `scoped_refptr<Encryptor>` instead. Source inspection confirms
`OSCryptAsync::GetInstance()` returns the same reference-counted instance, so
the custom backend now receives `encryptor` alongside the existing sync engine
and crypto initialization. No encryption provider, key selection, or failure
handling changes.

Core commit `0afa9ac4de2f328a61af6439b52d6a114e0d23f3` contains this one-line
adaptation; platform `f4d1aa063531f5f580f6e35cbd227283d5d89359` pins it. Quilt
refresh used an isolated reconstruction of the original patch's input files
because later patches shadow other files in that patch. The refreshed patch
reapplied with zero fuzz, and the resulting sync source is byte-identical to the
prepared build source. The previously failing object compiled successfully
(`sync-fix-compile.log`). Full compilation resumed from cache; the preceding
failure evidence is saved under `*-before-sync-fix.*`. The series remains at
402 patches. Sync runtime behavior has not been validated by this object build.

## Settings preference compatibility

Platform commit `26b5039cf2b0ed81df1e8b971068c685bfd9f428` migrates the Helium noise and
services settings pages from the removed `PrefsMixin` to Chromium 158's
`pref-key` controls and `PrefServiceObserverMixin`. Consent, service enablement,
and origin override remain observed; origin changes use `PrefService`. The
Polymer WebUI listener and shortcut action-link stylesheet use their relocated
modules. This retains the existing settings rather than removing their controls.

The patch reapplied with zero fuzz (**403 total**). Settings TypeScript compilation
and lint pass (`settings-fix-targets.log`). Full compilation resumed from cached
outputs; the preceding failure is preserved under `*-before-settings-fix.*`.
Runtime interaction with the migrated settings remains to be verified in the new
app.

## Device-info sync namespace

The subsequent build reached 8,580 more actions before finding an unqualified
Helium `private_sync_prefs` reference in `DeviceInfoSyncClientImpl`. Core commit
`60b1a6f6c3374e4ff30abb3c29d63c98c7fbd18d` qualifies it with `browser_sync::`;
platform `d9ea2beeea2bc8946bf4bae13d67901c2216bfdd` pins that core. The private-sync
condition and returned sign-in metadata are unchanged. The refreshed original
patch reapplied without fuzz, and its resulting file matches the prepared source.
The affected object compiles (`sync-namespace-fix-compile.log`). The series remains
at 403 patches; prior failure evidence is retained under
`*-before-sync-namespace-fix.*`. Full compilation resumed from cache.

## Sync-vault extension event arguments

Chromium 158's extension `Event` constructor takes reference-counted `EventArgs`
instead of a `base::ListValue`. Core `6dcde0fc736157833bb24f2655b3092db01e3d94` wraps the
request and release event payloads with `base::MakeRefCounted<EventArgs>` and
includes the current declarations. Platform `827621d6e711f62df838047f01e698c59b70b770`
pins the change. Provider selection, browser-context restrictions, request limits,
and dispatch callbacks are preserved.

The original patch was refreshed in isolation and reapplied without fuzz; the
result matches the prepared source. `sync_vault_provider_service.o` compiles
(`sync-events-fix-compile.log`). The series remains at 403 patches. The preceding
full-build failure is preserved under `*-before-sync-events-fix.*`; compilation
resumed from cache. End-to-end sync-vault behavior has not been tested.

## Toolbar action label compatibility

Core `2b31a14abffd7a7f1cb2a3ed0be6a4ae9f37b19b` replaces the removed
`BrowserActions::GetCleanTitleAndTooltipText` in toolbar customization with
`chrome::GetCleanText(..., chrome::CleanTextOptions::kAll)`, retaining mnemonic
and ellipsis cleanup for the dynamic New tab action. Platform
`a5698d0d2f083f2f1f8f6edd0beb32ea63d2f5b0` pins it. The target already depends on the
current action-utility library. Other refreshed-patch changes are hunk offsets
and context labels; the functional delta is the helper call and its include.

The patch reapplied without fuzz and the prepared handler matches the isolated
result. The affected object compiles (`toolbar-label-fix-compile.log`). All 403
patches remain selected. The preceding full-build failure is preserved under
`*-before-toolbar-label-fix.*`, and compilation resumed from cache.

## Filtered flag-list initialization

Chromium 158 rejects the global constructor introduced by the filtered flag list.
Core `6fb39b67efedb92b29bdf98ae82a97972c86ddbd` initializes the same filtered vector in a
function-local `NoDestructor` and returns a const reference to callers. Platform
`9fe85b49247314b2ffa19fc6f6814a5fb558c3db` pins it. Flag exclusions, iteration order,
and process-lifetime storage remain unchanged.

The refreshed patch reapplied without fuzz. The prepared file matches its isolated
result after applying the existing domain-substitution rules; no substitutions
were reverted. `about_flags.o` compiles (`flags-init-fix-compile.log`). The series
remains at 403 patches. The preceding failure is preserved under
`*-before-flags-init-fix.*`; compilation resumed from cache.

## Navigation disposition names

Chromium 158 renamed the window disposition enum members. Core
`de04e61ab2cbcf27ef689a3291f140f8e4a49b8d` updates the download action that opens services
settings. Platform `995cbf877f327fe79e5367a6c9e97b289ceaac5d` also updates command-bar,
link-preview, and navigator references to the equivalent current names. Foreground,
background, current-tab, and new-window behavior remains selected as before.

The refreshed core patch and new platform patch applied without fuzz (**404 total**).
All four affected objects compile (`navigation-enum-fix-compile.log`), and a source
scan finds no old uppercase disposition names in Chrome or component C++/Objective-C++
files. The preceding failure is preserved under `*-before-navigation-enum-fix.*`;
full compilation resumed from cache.

## macOS first-paint feature declarations

The native-frame patch removed `ui_features.h`, which Chromium 158 still needs
for `kMacDeferInputContextUntilFirstPaint`. Core
`fd5342cd999dcc9e4d9083cf54182d00e73e7a5d` retains that include and adds the direct
`base/feature_list.h` include. Platform `4d87fd0a52e501f6b758761289b8de38bc9aa121`
pins it. Input-context deferral, presentation callbacks, and visual-switcher
keyboard handling are unchanged.

The core patch reapplied without fuzz; applying the existing visual-switcher
patch afterward produces the prepared source exactly. The macOS frame object
compiles (`mac-frame-includes-fix-compile.log`). The series remains at 404 patches.
The preceding failure is preserved under `*-before-mac-frame-includes-fix.*`;
compilation resumed from cache. Input-method startup behavior still needs runtime
validation.

## Caption settings and disabled AI installer

Ungoogled removes the AI speech-model installer from `BrowserProcess`, while
Chromium 158's caption settings still reference it. Platform
`c787971280052e3b3916cbea61088f706b09c233` removes the obsolete model-installation
callbacks and observer bindings and explicitly hides those unavailable controls
in the settings data. The model feature was already disabled by default. System
caption settings and SODA language-pack handling remain; all 12 regular caption
and SODA methods have byte-identical implementations before and after this patch.

The patch reapplied without fuzz (**405 total**). Both the caption handler and
shared settings-data provider compile (`captions-fix-compile.log`). This verifies
source compatibility, not live speech recognition. The preceding failure is
preserved under `*-before-captions-fix.*`; full compilation resumed from cache.

## Disabled-service link guards

The first main-framework link reported two references to unbuilt services:
Safe Browsing pings in lazy profile startup and enterprise real-time reporting
in the cloud-profile factory. Platform `84ee191b109c99f3d7a331d0353abbdcd5346c47`
guards those calls and includes with the same feature conditions as their GN
source selection. The existing disabled Safe Browsing/content-analysis
configuration is retained; these services are not enabled to satisfy linking.

The enterprise target also now declares its direct policy-header dependency,
which its existing callers require. GN generation succeeds with 36,639 targets,
and header checks pass for both profile and enterprise targets. Both affected
objects compile; `llvm-nm` confirms the two unavailable service references are
absent (`service-guards-symbol-check.json`). The patch reapplied without fuzz
(**406 total**). The failed main link is preserved under
`*-before-service-guards-fix.*`; the full build resumed to retry linking.


## Completed arm64 build and internal artwork

The full arm64 compile/link completed successfully at **2026-11-06 10:19 UTC**,
using core `fd5342cd999dcc9e4d9083cf54182d00e73e7a5d` and platform
`84ee191b109c99f3d7a331d0353abbdcd5346c47`, with all **406 patches** applied.
The final cached resume completed in 2m16s; this is not the total clean-build time.
GN arguments hash: `05f104d8ff57cff89116b982222f7b7b99e2ba7587d1d328a116f865370b5de6`.
The app and matching ChromeDriver are under
`.work/chromium-158/macos/build/src/out/Default/`.

The headless smoke check passed page loading, JavaScript, profile persistence
across two launches, 18 fresh-profile defaults, Kagi's suggested-search wording,
and explicit Helium credits in About and onboarding. Runtime preference tests
passed noise-toggle persistence, consent observation, five service bindings,
and service-origin normalization/persistence; remote services stayed disabled.
The flags page populated 407 entries and excluded the three sampled incompatible
flags. Evidence: `out/validation/chromium-158-arm64-smoke.json`.

Internal artwork coverage passes for 36 mapped resources and two shared WebUI
paths. The running app serves the exact Lune About PNG and welcome/services SVG.
App and both notification-helper icons match Lune's `.icns`; there are no bundled
asset catalogs or `CFBundleIconName` overrides. Helium attribution is retained.

An initial exact-color canvas test failed because fingerprinting protection adds
noise to canvas readback. The smoke test now hashes the actual loaded resource
through DevTools, retaining image and color-profile chunks and ignoring only
PNG EXIF metadata stripped by packaging. Standard and Retina About assets have
separate expected hashes. Protection remains enabled. Use the exact component
commit when validating this candidate against the still-157 main lock:

```sh
.work/venv/bin/python scripts/smoke-browser.py \
  .work/chromium-158/macos/build/src/out/Default \
  --arch arm64 --chromium-version 158.0.8127.18 \
  --platform-commit 84ee191b109c99f3d7a331d0353abbdcd5346c47 \
  --ui --internal-icons --settings \
  --report out/validation/chromium-158-arm64-smoke.json
```

Intel compilation uses the same source/component commits and a separate
`out/Intel` directory, with ten local jobs. Its log and build metadata are under
`.work/chromium-158/intel-build.log` and `intel-development-build.json`.
Neither this development build nor its runtime checks establish signing,
notarization, native Intel behavior, or installed-app updates.


### Native arm64 inspection

The headed smoke check also passed on a Retina display, including the 64-pixel
About resource. Native inspection confirmed the Lune About and welcome artwork,
setup-tab favicon, monochrome sidebar browser symbol, and visible Helium credit.
The right-hand vertical sidebar renders; Cmd-T/Cmd-L open the command bar;
Ctrl-Tab opens the quick-tab-switching list and Escape dismisses it.
Screenshots are retained locally as `out/validation/chromium-158-about.png` and
`chromium-158-onboarding.png`. This is focused inspection, not full UI acceptance.

A separate defect remains: submitting `helium://setup` or `chrome://setup/` in the
command bar starts a search and opens a new tab, including from Cmd-L. Direct
entry through the sidebar's address field navigates correctly. External DNS was
blocked in the disposable test profile, so these searches reached only the
network-error page. Fix and retest command-bar URL classification/disposition
before treating the full UI as validated. Onboarding still inherits upstream
policy/terms links; those also require the planned branding/services review
before a public release.


Further native arm64 checks passed with disposable loopback-only fixtures:
Shift-click opens the opt-in link preview, and its button promotes the preview
to a normal tab. A tab can be pinned; unpinning the sidebar hides it after focus
moves into the page; the settings toggle pins it again. Ordinary HTTP URLs load
through the command bar. Ctrl-Tab shows cached page thumbnails, Return activates
the selected tab, and the list-mode setting produces the alternate list UI.
Escape dismisses either switcher. Native evidence is recorded separately in
`out/validation/chromium-158-arm64-native-inspection.json`; the automated smoke
report deliberately does not claim to automate these controls.

Source inspection confirms the command-bar limitation is inherited from the
selected Xelium patch, not introduced by the 158 port: `UrlOrSearchForQuery`
accepts HTTP(S) URLs only, and `OpenUrl` explicitly chooses a new foreground tab
unless the active tab is a blank new-tab page. This remains a documented
limitation of the development candidate, separate from icon verification.


### Fresh component reconstruction

A fresh recursive clone from GitHub under `.work/chromium-158/fresh-checkout`
resolves the exact `84ee191b109c99f3d7a331d0353abbdcd5346c47` platform and
`fd5342cd999dcc9e4d9083cf54182d00e73e7a5d` core, with both worktrees clean.
The staged lock passes schema/configuration hashing, ungoogled/forward-port and
component ancestry checks, tree/gitlink checks, and all selected patch hashes,
order, and provenance checks. Evidence:
`out/validation/chromium-158-input-checks.json`. This verifies reconstruction
of the component repositories, not a second fresh Chromium preparation/build.
Permanent 158 input tags and main-lock promotion remain pending Intel validation.


## Full source replay and localized attribution

A clean source preparation from the published `84ee191` platform, pinned archives,
and exact core completed with all **406 patches** applied strictly, followed by
substitutions, localization, resources, and GN. Fresh arm64 and Intel GN arguments
match the active builds exactly. Both target graphs generate successfully from
the arm64 host archive, including their bundled PGO profiles. The UI/onboarding
and resource validators pass on the fresh tree. Reports and logs are under
`.work/chromium-158/fresh-preparation.json`, `fresh-prepare.log`, and
`fresh-intel-gn.json`.

A full checksum dry run against the incremental build source found only
translation-catalog differences plus generated caches/onboarding strings and
modification times; it did not modify either tree. The catalog differences
exposed a name-substitution bug: protected English partner messages retained
Helium, but translations were still renamed to Lune. The previous incremental
catalogs also retained stale fingerprints for these messages after the branding
patch was added. This must be reconciled before final lock promotion.

Platform fix **`d44db707dc84799b09f4ddf7bef2498ced44ab74`**, published on
`fix/upstream-credit-localization`, carries protected message fingerprints through
the existing worker map as identity mappings. XTB substitution skips precisely
those IDs; ordinary localized branding retains its existing behavior. The first
broader approach was superseded after full-output comparison showed unrelated
changes; do not use its intermediate `1eb6ed0` commit alone.

The final fix passed another clean preparation and GN generation, again with all
406 patches and unchanged build arguments. `scripts/branding/check-names.py`
checks source IDs, protected translations, ordinary branding, unmapped translation
behavior, and the actual multiprocessing command. Its `--prepared` audit verifies
**162 protected translations**. Comparing all 1,390 files written by either name
substitution run found exactly **151 intended translation changes in 77 XTB files**,
with no other changes. Evidence: `fresh-preparation-credit-final.json`,
`fresh-credit-diff.json`, and `out/validation/chromium-158-credit-final-check.log`.

The active Intel compilation still uses `84ee191` and is intentionally untouched.
After it reaches a terminal result, fast-forward the build component to `d44db70`,
reconcile the affected catalogs against the verified fresh source, rebuild both
apps from cache, and rerun runtime checks including localized attribution before
publishing permanent input refs or promoting the main lock.
