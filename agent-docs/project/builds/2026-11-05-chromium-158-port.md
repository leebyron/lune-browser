# Chromium 158 integration work

Status: source inputs verified and extracted; integration incomplete. This is a
separate workspace from the running Chromium 157 UI validation build. No build,
runtime check, or release validation of 158 has passed yet. The main lock remains
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

The first **322 patches apply with zero fuzz**. Application currently stops at
`helium/ui/layout/vertical.patch`, including changed layout/animation code and the
missing old `tab_group_view_layout.cc` path. No patch has been skipped or forced.
Full preparation, GN generation, compilation, and runtime validation remain
incomplete for 158. The older 157 UI validation build is still a separate
running diagnostic build.

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
