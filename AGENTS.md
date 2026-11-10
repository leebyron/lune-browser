# Working on Lune

Lune is a personal Chromium browser distribution assembled from
ungoogled-chromium, Helium, selected upstream PRs, and our own contributions.
Read [the project definition](agent-docs/project/README.md) and
[architecture](agent-docs/project/architecture.md) before changing its structure.

## Current state

Lune `26.1109.2` is reserved for the next production release on
`release-26-1109-2`, with notes and the frozen record committed together.
It selects `inputs/native-window-close-1/macos`, preserving the complete accepted
appearance/downloads/footer/startup/sidebar stack. Input validation and all 65
orchestrator tests pass. Initial storage is about 50 GiB, below the preparation
and compilation thresholds; release builds and signing have not started.
Do not publish or reuse this version with different inputs. See
[next-release preparation](agent-docs/project/builds/2026-11-09-release-26.1109.2.md).

The development input `inputs/native-window-close-1/macos` includes the accepted
red-window-button fix and safe fullscreen-control teardown. Replacement native
controls close their owning Chromium widget, retaining unload confirmation and
ordinary Command-W behavior. It preserves the entire themed-sidebar/startup/
footer/downloads stack. Both candidate builds and smoke checks pass; exact replay,
native close regressions, and changed-unit compiles pass on the current main
composition for both architectures (Intel runtime under Rosetta). The owner
accepted Lune Close Test 2 and requested adoption for future builds. See
[native window close](agent-docs/project/features/native-window-close.md).

The development input `inputs/themed-sidebar-1/macos` adds the owner-accepted
palette-aware unpinned sidebar, a shared 216 px default/snap width, and Lune
selection colors that are lighter in Dark and darker in Light. Three signed,
single-thesis platform commits follow the session-restore default input. Both
accepted-preview browser builds, exact composed-unit compiles, native fixtures,
and fresh/saved-width browser checks pass (Intel under Rosetta). Main adopts the
input for future builds; frozen release inputs are unchanged. See
[themed sidebar](agent-docs/project/features/themed-unpinned-sidebar.md).

The development input `inputs/continue-session-default-2/macos` defaults macOS
startup to **Continue where you left off**, preserving saved and managed choices.
It retains the accepted footer prompts, downloads, Dock-prompt removal, and
older-macOS fixes. Both architectures and new release preparation inherit it
from the main lock. Patch replay, lint, and both changed-unit compiles pass;
no browser rebuild or runtime acceptance was performed for this default change.
See [startup default](agent-docs/project/features/startup-default.md).

The development input `inputs/floating-infobars-1/macos` includes the owner-approved
floating footer prompts from the Dock-message conversation. Prompts span the combined
content area with 8 px edge insets and stack gaps, native corner geometry and hairline,
subtle shadows, and equally inset dismiss buttons. Multiple ordinary prompts display
together. Both architecture builds pass; native arm64 acceptance and exact published-stack
replay pass. Existing downloads changes remain in the baseline; sidebar tint and width
edits from the wrong chat were discarded. See [footer prompts](agent-docs/project/features/floating-infobars.md).

Future development builds include the owner-accepted downloads fix through
`inputs/downloads-1/macos`, preserving the Dock-prompt and older-macOS fixes.
Toolbar-anchored menus reveal and retain the header. Downloads use native SF status
badges and the original SF ring for progress, with no clock or completion underline.
Both architecture builds and focused checks pass; Intel runtime fixtures use Rosetta.
See [downloads](agent-docs/project/features/downloads.md) for acceptance and validation.

Future development builds disable the macOS Dock-pinning message bar through
`inputs/remove-dock-infobar-1/macos`, retaining the older-macOS appearance fixes.
Strict replay, patch lint, and changed-unit compilation pass on both architectures;
full browser/runtime checks were not run for this removal. Existing frozen release
inputs are unchanged. See [Dock message bar](agent-docs/project/features/dock-infobar.md).

Lune `26.1109.1` is published as the production release in `leebyron/lune-downloads`.
The signed private source tag identifies frozen commit `24f6531a`; publication
policy is tracked separately on `production-release-policy`. Both frozen builds,
source inventories, signing/notarization, and local acceptance pass. All 18
public assets have verified digests. Anonymous versioned/latest downloads and
paired GitHub Sparkle feeds match the signed bytes, and public HTTPS installed
updates from build 2 pass on Apple silicon and Intel under Rosetta, including
relaunch and profile persistence. The publication freshness check observed
Chromium macOS Stable 157.0.8103.51; the shipped 158.0.8127.18 engine is ahead.

The owner explicitly deferred physical Intel testing for this release and chose
to publish now, with any fixes in later versions. The owner subsequently reported
a successful download and generally good fallback UI on Intel macOS 13.7.8,
with corner gaps and low-contrast fallback surfaces. Full native Intel acceptance
remains incomplete; see [older macOS appearance](agent-docs/project/features/older-macos-appearance.md)
for source findings and the native-radius/fallback-edge plan. The private optional Intel test kit remains
available. This production policy supersedes older hardware-blocking summaries
below. No new public staging release or prerelease is authorized; historical
build-1/build-2 artifacts remain unchanged. Website download links and old-feed
redirects are deployed and verified at lune.computer. Setup checks and website
CI pass on the local Mac runner; a real website download matches the release. See
[release delivery](agent-docs/project/release-delivery.md) and
[release evidence](agent-docs/project/builds/2026-11-09-release-delivery.md).

The default development input `inputs/older-macos-appearance-1/macos` includes
adaptive physical-pixel edges and 5% shadows for pre-glass header controls and
Command-T, plus the inherited 12 pt pre-26 content radius. Both architectures
are pinned to these fixes; new release preparation inherits the same lock.
Preserve both patches during future upstream integration. Native macOS 13 visual
acceptance remains pending. The separate default-browser prompt investigation
is not included in this input. Published 26.1109.1 and frozen release records
remain unchanged. See [appearance validation](agent-docs/project/builds/2026-11-09-older-macos-appearance.md).

The Helium November 9 development input imports main through `0a5feb31`,
adding independent history/bookmark autocomplete settings while retaining
Chromium 158.0.8127.18 and the accepted onboarding/UI stack. The four upstream
Git-conflicted patches preserve Lune's Chromium 158 bodies; strict archive-backed
replay also repairs pre-substitution context and XML newline assumptions in
platform patches. All 524 patches replay without fuzz; both architecture builds,
autocomplete/settings/persistence smoke checks, and packaged onboarding flows
pass (Intel under Rosetta). Build/runtime adoption evidence is recorded in
[the integration review](agent-docs/project/builds/2026-11-09-helium-update.md).
This does not publish a browser release or change the Chromium/ungoogled pins.

Main now pins the complete reviewed UI stack plus the accepted onboarding and
native toolbar refinements, plus Command-T corner/tint fixes through
`464c5298` under `inputs/command-style-2026-11-09/macos`.
Toolbar inset and cover modes require no launch flag. “Always cover (experimental)”
retains its explicit label. All toolbar modes preserve native sidebar glass and
4 px side padding. Sidebar hover/accessibility labels say Pin sidebar or Unpin sidebar.
Setup uses locally packaged artwork/fonts, separate update consent, Startpage first
and selected by default, native System/Lune themes, and the final Customize Lune
controls. Its tab reads Welcome to Lune and uses the envelope.open SF Symbol.
See [onboarding and toolbar integration](agent-docs/project/features/onboarding.md)
for the thirteen signed implementation commits, validation, and remaining limits.
This is a source/development-lock update, not a binary release.

Command-T now uses an 18 pt panel radius around the unchanged 10 pt result corners,
with equal 8 pt visible side/bottom gaps. Its native glass uses the same 5% theme
midpoint tint as the address bar; System theme remains untinted. The owner accepted
the preview and authorized publication on November 9. Two signed source commits,
strict six-file replay, both architecture builds, and native checks pass (Intel
runtime fixtures under Rosetta). See [Command-T corners](agent-docs/project/features/command-bar-corners.md).

The following feature summaries retain their original validation history. Their
statements that reviewed candidates are absent from the development lock are
superseded by the integration record above; published-binary limitations remain.

The issue #12 candidate on `topic/address-suggestion-selection` adds rounded
selection fills and shares native result rendering with Command-T. Both menus use
`HeliumNativeResultRow` for 52 pt rows, 16 pt icons, primary/secondary typography,
semantic colors, and the 25% selection fill. Address suggestions retain their
providers, ranking, activation, and keyboard-only selection; Command-T keeps its
hover selection, optional action labels, and scrolling. Signed platform commits
`3379baa0` and `f0e2df52` follow the accepted header-scroll stack. Both architecture
builds, native rendering checks, UI/settings/persistence smoke checks, and strict
source replay pass (Intel under Rosetta). Live arm64 checks cover selection/wrapping, result replacement/empty
results, navigation, dismissal, profile appearances, narrow/wide layout, and
Command-T scrolling. The corrected Lune Suggestions Test preview uses the normal
unpinned header setting. The owner accepted the shared row and selection styling
on November 8, 2026, requesting a smaller address-to-results gap and Command-T
layout refinements. Native Intel acceptance remains unverified. The candidate is not in the development lock or published builds.
See [address suggestion selection](agent-docs/project/features/address-suggestion-selection.md).

The accepted issue #13 refinement on `topic/command-bar-corners-reviewed` gives
Command-T a 48 pt shadow margin, margin-click dismissal, a centered 52 pt empty
input, a 600 pt maximum width with 36 pt side insets, and top placement centered
against the five-row maximum. Shared result rows use native 16 pt medium SF
Symbols without stretching, proportional favicons, tertiary action labels, and
“Switch to Tab”. A faint 5% black supplemental shadow retains the native glass.
Address results have a 4 pt top gap and expand the glass 10 pt per side while
header controls stay fixed. Shared icon padding aligns the result columns.
The owner accepted final alignment in Lune Corners Test 7 on November 8, 2026,
and authorized single-thesis commits, pushing, and resolving the issue. Twelve
signed platform commits end at `7b9dda91`; the original draft is preserved.
Strict replay matches the accepted source, both builds and native checks pass,
and smoke checks pass on both architectures before the final padding refinement
(Intel under Rosetta). Evidence and portable fixtures are on
`command-bar-corners-evidence`. Native Intel hardware and the older macOS fallback
remain unverified. The source is not in the development lock or published builds.
See [Command-T glass bounds and layout](agent-docs/project/features/command-bar-corners.md).

The accepted issue #16 implementation on `topic/header-scroll-through` forwards native
wheel events over floating header controls and gaps to content under the pointer,
including nested scrollers and either split pane. It preserves the original event
and corrects coordinates from the trailing controls' child window. Momentum keeps
its receiver, and direct delivery completes Chromium's wheel-end cleanup.
Autocomplete and extension popups retain their own scrolling. Both architecture
builds, native routing/appearance checks, and browser UI/settings/persistence smoke
checks pass (Intel under Rosetta). Arm64 browser interaction checks cover address
editing, controls, gaps, nested scrolling, split panes, popup exclusion, and
fullscreen. The owner confirmed scrolling across all header areas on November 8,
2026 in the distinctly named Lune Scroll Test preview and authorized publishing
the commits and resolving the issue. A simplicity review retained
the shared router, original events, weak momentum target, and existing Chromium
cleanup without additional implementation changes. Native Intel acceptance remains
unverified. The signed platform commit `d0c49b0a` is published on
`topic/header-scroll-through`; the regression fixture and evidence are published
on `header-scroll-evidence`. This implementation is not
in the development lock or published builds. See
[header scroll-through](agent-docs/project/features/header-scroll-through.md).

The owner accepted issue #7's final Content aware implementation and visual
refinements on November 8, 2026, and authorized publishing and resolving the issue.
The reviewed platform stack is `topic/chrome-appearance-reviewed`: three signed,
single-thesis commits for content adaptation and foreground legibility, shared
theme tint, and native header shadows. Content aware defaults on while respecting
saved opt-outs; regular glass and attached controls survive toggling. The tint
is the HSL midpoint of light/dark theme accents at 5%, identical across schemes.
Header shadows use 5% black, 10 pt blur, and a 3 pt downward offset. The sidebar
keeps AppKit's native large-surface behavior, with no dependency on header
visibility or page sampling. Its lack of toolbar-style light/dark inversion
remains a known native limitation. Inactive tint rendering remains unverified;
no activation workaround was added. Each commit compiles its changed units,
strict replay matches all accepted source bytes, and native checks pass on both
architectures. Both browser builds pass for the identical final source; Intel
runtime checks use Rosetta. The draft remains preserved. The candidate is not
in the development lock or published binaries. See
[native chrome appearance](agent-docs/project/features/chrome-appearance.md).

The accepted issue #15 candidate on `topic/media-toolbar-controls` restores the
existing media controller in the floating trailing group, orders its control
before Home, and uses `play.circle` in both the toolbar and Customize. The owner
confirmed it appears and requested no gap before the next icon; a floating
margin adjustment removes the 2 pt gap while preserving the hit target.
Two signed platform commits follow the reviewed issue #9 stack. Both architecture builds,
focused controller/symbol checks, and UI/settings/persistence smoke checks pass
(Intel via Rosetta). Live arm64 playback, multi-session controls, preference
toggles, empty/single-item groups, classic restoration, fullscreen, and appearance
checks pass. The owner accepted the refined preview on November 7, 2026 and
authorized pushing the commits and closing #15. The candidate is not in the
development lock or published builds. The unchanged full native gesture fixture failed its
short-click check; focused symbol checks pass. See
[media toolbar controls](agent-docs/project/features/media-toolbar-controls.md).

The local `trailing-toolbar-reviewed` candidate for issue #9 adds native toolbar
symbols and semantic state colors, tighter spacing, immediate preferred widths
for floating action containers, and a window-local Customize reveal hold.
Header SF Symbols, including Customize close, use 16 pt medium, with 14 pt site
information/reload icons; tab and sidebar-footer close icons use 11 pt medium.
The ellipsis target includes 1 pt extra padding on each side, and empty trailing
groups hide both glass and the input window. Single-item groups are 36 pt circles
with the button centered. Layout visibility intent keeps newly enabled Customize
actions from staying hidden after animation or overflow. Navigation, site info, reload, and
trailing icons fade their semantic hover color over 100 ms. The address glass
caps at half the available header width, and the Extensions menu button has no
layout gap before the first extension. Reload has a 2 pt trailing glass inset.
The rebuilt arm64 preview retains a clickable ellipsis after opening Customize.
The owner accepted the visuals on November 7, 2026, then supplied a Profile hover
crash report. Its animation-callback routing fix passes both architecture builds,
callback regression checks, and an arm64 Profile-menu interaction check.
The next candidate shares those symbols with Customize Toolbar, adds Home first
in the trailing pill, and honors Back/Forward, New Tab, and Collapse Tabs toggles.
A right sidebar without its toggle replaces the empty header with a 10 pt top
inset; the left retains traffic-light space. Reload visibility follows its toggle,
missing favicons use SF globe, and the duplicate Views sidebar toggle is hidden.
Orientation changes preserve the footer below the tab strip. Dragging a pinned
action exposed a null empty-icon name; the shared renderer handles it safely.
Both architecture builds and native regression checks pass. Live arm64 checks
confirm toolbar toggles, fallback globe, the 10 pt top inset, stable address text
when Reload is hidden, and Back/Forward/Reload context menus using the original
Chromium controls. The owner confirmed the footer stays at the bottom and toolbar
actions reorder without crashing on November 7, 2026. The owner also accepted the
10 pt right-sidebar top inset and stable address text when toggling Reload that
day. The next refinement adds 500 ms press-and-hold menus for Back, Forward, and
Reload, with native gesture checks passing on both architectures. Normal clicks
remain available when Chromium has no menu, including Reload without DevTools.
The next fixes remove the header drag shield above the raised right-sidebar rows,
return hidden Reload's 32 pt width to long addresses and editing while keeping
short addresses stable, and toggle Site Information closed on a second click.
Both browser builds and native gesture/address-layout checks pass; Back/Forward
held menus pass live arm64 inspection. The owner accepted the sidebar hit-region
and reclaimed-address-space fixes,
but Site Information still reopened on release. A subsequent widget lifecycle
observer now suppresses that release even after focus-loss dismissal destroys
the bubble. Both builds pass, and the owner confirmed a second click leaves
Site Information closed after release. A held Reload now also passes live
arm64 inspection with DevTools open. The issue #9 work is consolidated into
nine signed, single-thesis platform commits on `trailing-toolbar-reviewed`;
the stack is imported locally as `topic/trailing-toolbar-reviewed`, and the draft
branch remains preserved. The review removes duplicate sidebar margin
state, shares an opaque native symbol mask across color states, and centralizes
navigation menu wiring. Changed implementation units compile at every commit
boundary, and strict replay reproduces the final source. Final full builds,
native regression checks, and headless UI/settings/persistence smoke checks pass
on both architectures (Intel under Rosetta). The candidate is not yet
in the development lock or a published build. See
[trailing toolbar controls](agent-docs/project/features/trailing-toolbar-controls.md).

The development input `inputs/sidebar-pin-activation-2/macos` makes the sidebar
pin button follow its owning window/app activation. Inactive windows use native
semantic disabled text; active windows restore AppKit's default symbol rendering.
The owner accepted the inactive tint but found input 1's explicit active color too
dark; input 2 removes that override without changing symbol weight or size.
It remains clickable and updates without pointer movement. Native activation,
owner-isolation, and teardown tests pass on arm64 and Intel via Rosetta. Both
browser builds and the arm64 smoke check pass. Live arm64 inspection verifies
active/inactive tint and independent window states. The owner accepted input 2
on November 7, 2026; issue #10 is resolved. See
[sidebar pin activation](agent-docs/project/features/sidebar-pin-activation.md).
This is not in published builds 1 or 2 or release-accepted.

The development input `inputs/menu-retention-2/macos` adds window-local lifetime
holds for sidebar and header menus, including the default-browser footer menu.
It bridges transient tab expansion locks, refines the native green-button guard,
and resumes cursor retention after the final menu closes. Input 2 fixes a stuck
detached sidebar caused by AppKit retaining an idle remote-menu helper: retention
now checks its running flag rather than its presence. Both architecture builds
and native regression checks pass (Intel via Rosetta), including idle attached
menu helpers. Arm64 smoke checks pass; the input-2 Intel browser smoke run was
interrupted to reopen the owner test preview. Arm64 checks confirm footer and nested tab-menu holds acquire and
release. The owner confirmed normal sidebar dismissal and accepted the fix
on November 7, 2026; issue #8 is resolved. The preview includes a no-op Sparkle update fixture. See
[menu reveal retention](agent-docs/project/features/menu-reveal-retention.md).
This is not in published builds 1 or 2 and is not release-accepted.

The development input `inputs/window-menu-2/macos` retains already revealed
header/sidebar chrome while the native green-button popover is open, including
pending collapse timers. It preserves the accepted sidebar-footer-5 base.
Native lifecycle, isolated controls tests, both architecture builds and smoke
checks pass (Intel under Rosetta). The owner accepted the arm64 preview on
November 7, 2026; issue #6 is resolved. See
[window-menu retention](agent-docs/project/features/window-menu-retention.md).

`main` contains the project definition, locked development build inputs, local
build commands, validation tests/CI, and the Cloudflare website. Imported histories
are published on `component/helium`, `component/macos`, and `component/services`;
permanent `inputs/bootstrap-1/*` tags retain the first development inputs.
Read [the build runbook](agent-docs/project/building.md) before running the tools.

Lune's first arm64 development build passed full source preparation, GN generation,
compilation, and a headless app smoke test (page loading, JavaScript, and profile
persistence). The onboarding XML parser fix is pinned under `inputs/bootstrap-2/macos`.
See [the first build evidence](agent-docs/project/builds/2026-11-05-arm64.md).
Native Intel hardware acceptance remains outstanding; signing and update progress is below.
The local Mac passes storage and toolchain preflight. Xcode 27.2/27B52 and SDK
27.2 are pinned for an experimental development build after Chromium source review.
The owner requires no additional CI spend: use this Mac as a self-hosted GitHub
Actions runner. The manual browser workflow accepts reviewed main-branch runs
from the owner only; no scheduled or automatic public-release job is enabled.
Signing and notarization credentials stay in Keychain. Stable automatic updates,
self-hosted services deployment, and recurring browser builds remain disabled.
Targets are macOS arm64 and x86_64. Website status is recorded in
[the website runbook](agent-docs/project/website.md).

The development lock now targets Chromium 158.0.8127.18 with the reviewed
ungoogled/Helium forward port and Xelium UI stack. Both architectures build;
arm64 headless/headed and Intel-under-Rosetta smoke checks pass, including Lune
artwork, defaults, settings, and French/German upstream attribution. Permanent
`inputs/chromium-158-1/{helium,macos}` tags retain the inputs. Focused native arm64
inspection passed with the inherited command-bar internal-URL limitation recorded.
The original port validation used development builds. See
[the port evidence](agent-docs/project/builds/2026-11-05-chromium-158-port.md).
Setup checks and website deployment now pass on the existing Mac runner; inherited
component hosted workflows are disabled. See the build runbook before changing CI capacity.

The first signed release candidates (builds 1 and 2) now pass Developer ID,
Apple notarization, stapling, Gatekeeper, and Sparkle signature checks on both
architectures. Installed updates and profile persistence pass on arm64 and Intel
under Rosetta. Public test releases and corresponding source are published in
`leebyron/lune-downloads`; staging feeds are live on `lune.computer`. Stable
promotion still requires native Intel acceptance. Public HTTPS installed updates
pass on arm64 and Intel under Rosetta. See
[release bootstrap](agent-docs/project/builds/2026-11-06-release-bootstrap.md).
Run acceptance browsers sequentially because Sparkle shares macOS bundle state.

The development inputs include a subtle shared-core content-pane shadow under
`inputs/content-shadow-1/{helium,macos}`. Both architectures compile and pass
smoke checks (Intel via Rosetta); native arm64 visual acceptance covers light/dark,
vertical/horizontal tabs, split panes, rounded-frame toggling, and fullscreen.
See [the feature evidence](agent-docs/project/features/content-pane-shadow.md).
This feature is not in published builds 1 or 2.

The development inputs under `inputs/floating-address-2/helium` and
`inputs/floating-address-20/macos` include
an editable AppKit glass address capsule, 48 pt distance retention, whole-surface
focus, fade-only top controls, fullscreen edge reveal, sidebar-aware geometry, and
softer content/sidebar shadows. The subsequent toolbar revision adds paired
native navigation, the original extension/menu controls in a trailing glass
group, native window dragging, fixed traffic lights without a pill, and
4 pt rails with a fixed 26 pt outer radius and 8 pt surface insets.
The native chrome refinement changes the inherited AppKit frame-radius hook to
26 pt, removes the extra content inset and outline, and keeps fullscreen
edge-to-edge. Glass honors profile Light/Dark overrides and follows the OS in
System mode; native input regions prevent cursor fall-through and enable toolbar
dragging only while visible. Sidebar pinning and
context menus are restored, with pinned-left defaults for new profiles. The
sidebar toggle stays solely inside the sidebar; its former floating toolbar pill
is removed. Glass is recreated on appearance changes, detached tab rows use
AppKit semantic colors, and toolbar cursor regions exclude the resize perimeter.
The owner accepted resize cursors and fullscreen behavior on input 12. Input 13
restores detached-sidebar blank-area drag/context-menu routing and top-row
clearance, uses a 12 pt adjacent glass gap and 4 pt toggle inset, and reveals the
top bar from either sidebar header. Input 14 removes the trailing icon window's
remaining vertical motion, keeps traffic lights on the left during right-sidebar
animation, retains sidebar menus and the fullscreen pinned-sidebar shadow, and
reveals the left sidebar from visible traffic lights. Its larger toggle uses a
2 pt popover inset, retaining 4 pt when pinned. Customize removes its extra native
header, keeps the existing Appearance row first, and adds a native glass close
button. Toolbar dragging excludes that panel and its scroll clipping is square.
Inputs 15–16 add 2 pt per side around pinned tabs, narrow the popover by 2 pt,
restore its inner-edge resize handle, and move the detached sidebar with the
fullscreen menu-bar offset while pinned sidebar controls stay fixed. They also
correct direct frame-view build dependencies. Input 17 anchors native headers
and their child control windows during asynchronous vertical resizing, and
reduces detached width by another 2 pt (4 pt total).
Both architectures compile and pass headless smoke/default/settings checks
(Intel via Rosetta). Native arm64 sidebar context-menu, unpin, app-menu, editor,
and clean-shutdown checks pass. The owner previously accepted
the distance behavior and animation, and accepted input-16 popover resizing on
both sides and fullscreen menu-bar synchronization on November 6, 2026. The
owner also accepted input-17 header stability during bottom-edge resizing.
Other pending interaction checks remain listed in
[the feature evidence](agent-docs/project/features/floating-address-bar.md).
Input 18 restores the full popover width, undoing the 4 pt reduction.
Input 19 derives traffic-light spacing from AppKit and compacts its container.
Input 20 uses normal omnibox editing text, preserving an empty new-tab field.
This is not in published builds 1 or 2 and is not release-accepted.

The current development macOS input adds a text-only frame-thickness label
restoration under `inputs/frame-label-1/macos`. Patch replay and XML checks pass;
it is included in the day/night development rebuild. Source-string coverage remains
advisory while accepted English
fallbacks are reconciled in GitHub issue #4. See
[the string review](agent-docs/project/features/string-review.md).

The development macOS input now includes the approved 30% wider Lune artwork,
Chlorophyll Daylight / Pelagic Signal palettes, and appearance-aware Dock icons
under `inputs/day-night-2/macos`. Website and app validation is recorded in
[day/night branding](agent-docs/project/features/day-night-branding.md).
These assets are not in published builds 1 or 2.

The development Command-T palette uses native AppKit glass, text input and result
buttons under `inputs/command-bar-3/macos`. Direct URL
navigation ranks first; default search remains within the first two results.
Helium bang keywords and partial completion use the existing catalogue. The resolved
provider name is an inline pill. Escape leaves the scope; Backspace at the start
of the query restores the editable bang text. The scoped input has no generated
placeholder or instructional helper text. The panel shows five results with
native scrolling; keyboard selection keeps its result in view.
See [command palette evidence](agent-docs/project/features/command-bar.md).
This prototype is not in a published browser build or release-accepted.

The Xelium UI candidate is described in [UI integration](agent-docs/project/xelium-ui.md).
Target the latest stable Chromium independently of upstream browser release cadence;
never downgrade Chromium to satisfy optional UI patches. Discovery reports stable lag.

## Engineering rules

- Prefer native Git fetch, merge, cherry-pick, rebase, and worktree operations
  for repository history. Preserve upstream ancestry and original authorship.
- Helium and ungoogled-chromium are patch/configuration repositories, not full
  Chromium trees. Use Helium's source preparation and quilt workflow at that
  boundary. Do not apply the ungoogled series twice.
- Keep reusable browser features independently upstreamable to Helium. Keep
  Lune branding, domains, signing keys, and release policy in separate commits.
  Follow the target upstream's current contribution guidelines; technical
  portability does not guarantee maintainer acceptance.
- Pin release inputs to full commit IDs and dependency/archive hashes. Record
  PR base/head, ordered commits, dependencies, provenance, and local adaptations.
  Never build a release from a moving PR URL or an unrecorded dirty tree.
- Stop integration on conflicts or failed validation. Do not automatically drop
  patches, choose ours/theirs, or accept fuzzy patch application to make CI green.
- A clean merge is not a release gate by itself. Validate source preparation,
  builds, browser behavior, signatures, and the installed-app update path on
  both supported architectures.
- Keep signing credentials out of source and untrusted build jobs. Use Lune's
  own identity, profile directory, service endpoints, and Sparkle public key.
- Publish immutable artifacts before updating the feed. Preserve the last good
  feed on failure and never overwrite a published binary or reuse its version.
- Keep Chromium source trees, build products, caches, private credentials, and
  generated workspaces out of the main branch.

## Working practices

- Keep changes focused and use descriptive branch names. Do not add a `codex/`
  prefix unless tooling explicitly requires it.
- Update project docs when a design decision changes. Distinguish recommendations,
  implemented behavior, source inspection, and runtime verification.
- Run checks appropriate to the actual change. Documentation changes need link,
  consistency, and whitespace checks, not a Chromium build.
- Browser patches should be developed in the prepared source tree, refreshed
  with quilt, unmerged into the correct core/platform repository, then committed.
- Preserve imported licenses and attribution. Check current upstream guidance
  before preparing a contribution; Helium currently requires human-written
  upstream issue/PR descriptions. Do not submit upstream messages automatically.
- Do not create schedules, releases, or deployments merely because they are
  described in the roadmap. Implement and activate them when that work is requested.

## Project references

`agent-docs/` contains documentation written by and for agents. Keep human-facing
documentation separate when it is added.

- [Definition and scope](agent-docs/project/README.md)
- [Repository and patch architecture](agent-docs/project/architecture.md)
- [Builds, releases, and updates](agent-docs/project/releases.md)
- [Services and website](agent-docs/project/services.md)
- [Website deployment runbook](agent-docs/project/website.md)
- [Implementation roadmap](agent-docs/project/roadmap.md)
- [Research and primary sources](agent-docs/project/research.md)
