# Working on Lune

Lune is a personal Chromium browser distribution assembled from
ungoogled-chromium, Helium, selected upstream PRs, and our own contributions.
Read [the project definition](agent-docs/project/README.md) and
[architecture](agent-docs/project/architecture.md) before changing its structure.

## Current state

The development input `inputs/menu-retention-2/macos` adds window-local lifetime
holds for sidebar and header menus, including the default-browser footer menu.
It bridges transient tab expansion locks, refines the native green-button guard,
and resumes cursor retention after the final menu closes. Input 2 fixes a stuck
detached sidebar caused by AppKit retaining an idle remote-menu helper: retention
now checks its running flag rather than its presence. Both architecture builds
and native regression checks pass (Intel via Rosetta), including idle attached
menu helpers. Arm64 smoke checks pass; the input-2 Intel browser smoke run was
interrupted to reopen the owner test preview. Arm64 checks confirm footer and nested tab-menu holds acquire and
release; physical pointer hover
acceptance remains pending. The preview includes a no-op Sparkle update fixture. See
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

The development input `inputs/edge-frame-17/macos` supersedes the earlier macOS
frame: a 16 pt native perimeter, edge-to-edge content without gutters or shadow,
a flush square glass sidebar, and a pinned-only semantic separator. Reveal uses
8 pt windowed edge bands, four physical top pixels and one side pixel fullscreen.
The header is 52 pt tall with 36 pt controls and 8 pt outer insets. Both sidebar
modes follow the fullscreen menu-bar offset and share their header geometry.
Native blank-space dragging/context menus, the full popover width, standard
traffic-light spacing, and autocomplete teardown protection remain in place.

The owner accepted header/popover geometry, blank-area dragging and menus, and
input-13 header/sidebar retention during native resizing. Cursor acceptance was
subsequently withdrawn: inputs 14–15 did not reliably fix resize cursors or tab
content drift. Input 16 removes 183 lines of accumulated cursor overrides,
tracking areas and the unsuccessful local-coordinate workaround. It retains
native resize hit routing and resize retention, and selects Chromium's existing
synchronous resize path. The owner initially accepted the synchronous A/B, then
reported intermittent cursor flicker and invisible toolbar icons; do not treat
that experiment as cursor acceptance. Input 17 fades toolbar content rather than
NSWindow opacity, which Chromium also controls while waiting for compositor frames.
Live inspection confirmed the invisible toolbar window had alpha 0 while still
visible and clickable. Both architecture builds and smoke checks pass (Intel via
Rosetta), along with native arm64 fullscreen/menu checks. The owner confirmed
input-17 icons remain visible but cursors still flicker while Lune is active.
Further cursor work is deferred at the owner's request and tracked in
[GitHub issue #5](https://github.com/leebyron/lune-browser/issues/5). These are
development inputs, not published builds 1 or 2. See
[edge-to-edge frame evidence](agent-docs/project/features/edge-to-edge-frame.md).

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

The development macOS input under `inputs/sidebar-new-tab-2/macos` places New Tab
below pinned tiles and above regular tabs. Default new tabs prepend; links open
immediately after the active tab. New Tab uses regular tab hover colors and the
same 2 pt row spacing; pinned tiles use fills and 6 pt spacing shared with the
New Tab section gap. See [sidebar evidence](agent-docs/project/features/sidebar-new-tab.md)
for build and runtime validation. This is not in published builds 1 or 2.

The development input `inputs/sidebar-footer-5/macos` adds a compact sidebar
footer for the default-browser prompt and downloaded Sparkle updates. The default
row reads “Make default browser”; its close control and sidebar tab close controls
appear on hover, with native SF Symbols and targets 6 pt larger than the original
tab control. Row side margins are 1 pt narrower and icon left insets 2 pt larger.
The footer bottom inset is 5 pt. New Tab has no hover tooltip. Navigation beside
the traffic lights gains 4 pt of clearance; the right sidebar toggle is inset 9 pt.
Close symbols are horizontally centered. The default row keeps its height on hover
and relayouts its faded label when the close control appears. Labeled footer
actions have no hover tooltip; close symbols use 11 pt SF Symbols.
Other infobars retain their existing placement. See
[sidebar footer evidence](agent-docs/project/features/sidebar-footer.md)
for implementation and validation limits. This is not in published builds 1 or 2.

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
