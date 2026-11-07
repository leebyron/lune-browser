# Menu reveal retention

Requested November 7, 2026; tracked in [issue #8](https://github.com/leebyron/lune-browser/issues/8).

## Cause and behavior

The default-browser footer already held a `kKeepCurrentState` tab-strip expansion
lock while its context menu ran. That lock controlled vertical tab expansion,
but not the independent Zen reveal animation or AppKit header presentation.
Moving into the menu could therefore dismiss the sidebar underneath it.

A window-local, reference-counted hold now preserves already revealed chrome
until the last participating menu closes. It stops the cursor-exit timer and
guards the common reveal boundary against callbacks queued before menu opening.
The native frame also retains its current presentation while the hold exists,
including when menu tracking changes window activation. Hidden surfaces stay
hidden; pinning preferences and geometry updates are unchanged.

`kKeepCurrentState` expansion locks acquire this hold, covering the footer,
vertical tabs/groups and existing tab-strip menu/popover presenters. The permanent
Zen `kKeepExpanded` lock deliberately does not: bridging it would hold the
sidebar open indefinitely. Direct menu presenters also acquire holds: horizontal
tab and New Tab menus, toolbar menus, the application menu, extension context
menus, toolbar overflow and split-view menus, and blank-sidebar/header system
menus. The native green-button popover keeps its separately accepted lifecycle
handling from [window-menu retention](window-menu-retention.md).

Each hold is a `ScopedClosureRunner` bound to a weak `BrowserView`. Presenters
release it on menu close and destroy it after their menu runner during teardown,
covering cancellation paths that suppress close callbacks. Independent and nested
menus do not release each other's holds. When the last hold ends, a weak task
reevaluates pointer retention after command dispatch unwinds, so a command can
safely destroy its presenter or window.

## Input and validation

- Base: `inputs/window-menu-2/macos`.
- Input: `inputs/menu-retention-1/macos`, commit
  `cc25e64b6fa85516ce9265f689ee29520f28654c`.
- Patch: `patches/helium/ui/menu-reveal-retention.patch`.
- Development only; not in published builds 1 or 2 and not release-accepted.

Strict no-fuzz replay passes through 61 relevant patches across all 23 affected
files and reproduces the prepared source exactly. The patch includes direct
`browser_view_header` dependencies for the legacy New Tab button and extension
context-menu targets. All eight affected GN dependency checks, inherited patch
and translation lint, lock validation, and all 44 repository tests pass. Evidence
is recorded under `.work/menu-retention/`.

Arm64 and Intel builds and headless smoke/default/settings/artwork checks pass;
Intel ran under Rosetta. Native arm64 checks verify the footer context menu opens
from a detached sidebar and retains one hold until outside-click cancellation.
Read-only inspection of the real browser counter records `0 → 1 → 0`. A tab
context menu acquires two overlapping holds (its presenter and expansion lock);
selecting Close Other Tabs releases both, returning `2 → 0`. The log is
`preview/menu-hold-lifecycle.log`; no debugger remains attached.

The native menu stayed open with its sidebar while synthetic scrolling targeted
the portion beyond the normal 48 pt retention distance. However, automation's
synthetic pointer does not reliably drive macOS global-pointer hover behavior,
so physical pointer exit/resume acceptance remains pending. This is not a claim
of a complete left/right, fullscreen, multi-window or teardown matrix. Native
Intel hardware acceptance remains separate from Rosetta checks. The glass
contrast and trailing button styling issues remain in issues #7 and #9.

## Preview update fixture

At the owner's request, the local preview also receives a simulated downloaded
Sparkle update. `.work/menu-retention/ready-fixture.py` verifies the preview's
process identity, locates its existing Sparkle observer, invokes
`updater:shouldPostponeRelaunchForUpdate:untilInvokingBlock:` on the main thread
with a no-op installation block, then detaches the debugger. This exercises the
real readiness notification and footer layout without a download or installer.
It does not add a production switch, preference, or updater-policy change.

The two footer rows render together. The update row survives dismissal of the
default-browser prompt, and its click clears the fixture without restarting the
process. Both prompts were restored afterward. The current preview is
`.work/menu-retention/Lune Menu Retention.app`, using the isolated profile under
`.work/menu-retention/preview/`; it is left pinned on the left with a simulated
update ready. Unpin it to check physical pointer retention across the menu.
