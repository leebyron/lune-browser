# Pinned tab groups

Issue [#31](https://github.com/leebyron/lune-browser/issues/31), requested November 12, 2026. The owner accepted the final native preview for future main builds through signed input `inputs/pinned-tab-groups-1/macos` (`40b750326568d91254f3834e0f665a287314a2bc`). Published browser releases retain their frozen inputs.

## Behavior

The vertical sidebar orders pinned tab tiles, pinned tab groups, a separator, New Tab when enabled, regular tabs/groups, then Older Tabs. Pinned groups and everything below them share one scrolling contents and scrollbar. The pinned tiles retain their existing viewport.

Drag a group header across the separator to pin or unpin the whole group; drag within the pinned portion to reorder groups. The group's menu offers **Pin tab group** or **Unpin tab group**, with the native `pin` or `pin.slash` SF Symbol. Pinning keeps the group's identity, title, collapse state, member tabs and split children. It is separate from individual tab pinning.

Ordinary default-position new tabs open at the beginning of the regular list, below all pinned groups. Group-specific creation, opener-relative links and explicit insertion constraints retain their existing paths. Loose tabs and external URLs cannot become standalone rows in the pinned-groups portion; deliberate drops into an existing group remain membership operations.

Dragging an ordinary tab over a collapsed vertical group exposes a temporary first-row slot beneath its header. The tab is appended to the group's existing members; the collapsed metadata and hidden existing rows remain intact. Leaving the target removes the slot, and release hides the incoming row along with the other members. This membership operation works for pinned and regular groups without changing their pin state. The owner confirmed the first-row slot, append order and retained collapsed state.

Only a collapsed group that is the current tab-drop destination receives a selected-tab pill. Its fill, label color and corner radius match the active tab, while its existing header padding and height stay unchanged. Expanded headers remain neutral. Group carets hide throughout internal tab dragging and return to normal hover behavior afterward. Native-theme carets use the header foreground rather than white selected-tab text; the independent color fix retains the native glass control-color override.

Pinned groups are protected from automatic Older Tabs cleanup even when **Move inactive tabs from groups** is enabled. Existing stale Older residency is repaired rather than retained in a pinned group.

## Separator and dragging

The separator is present whenever pinned groups exist, whether New Tab is shown or hidden. It reuses the edge scroll hairline rendering and aligns to the inner contents of a normal tab: the tab background's horizontal bounds inset by the actual left and right content padding. The last group's existing trailing margin is retained, with no additional margin above the rule and 8 DIP below it to New Tab or the first regular row.

During an eligible whole-group tab drag, always show the separator. The populated pinned portion uses the prior target boundary at the rule's bottom. The empty portion uses its existing 8 DIP lower clearance, ending before the first regular row. Starting a drag adds no group-sized empty row above the separator. The first regular drop position below the rule reorders rather than pins, including when New Tab and the pinned tiles are absent. A first pinned group has no extra top margin when no pinned tiles precede it.

Automatic collapse at drag start changes the source group's natural row height. Subsequent pointer movement cannot enlarge the scrolling contents. Only the model's actual destination slot creates an insertion gap. Moving the group back below the rule removes its upper gap; the separator follows the remaining pinned contents without retaining a second reservation. Group reorder targets use header midpoints rather than the midpoint of expanded member tabs. Autoscroll re-evaluates the destination using current contents coordinates.

Partial-window vertical drags remain attached while the cursor stays inside the entire browser window, including the page and title bar. A new-window tear-off begins after the cursor leaves those bounds. Existing valid tab-strip transfers and split-view targets remain available. Dragging every tab together, or the focused visible group, retains Chromium's existing whole-window move shortcut. A window containing only one group therefore moves as a window when its header is dragged; its menu still pins/unpins the group. The gesture mode is selected before views attach: whole-window gestures skip automatic collapse, temporary pin-target visibility, insertion gaps, tab transforms and pin-state mutations throughout the gesture, including after attachment to another window. Existing separators remain visible when pinned content already exists.

For an attached partial drag, the sidebar target extends upward from its scroll viewport through the blank sidebar space to the window edge. Crossing this internal boundary must not reset the active container, transforms or insertion gap. This extension is limited to the attached vertical sidebar lane; page split targets and actual window exits retain their own behavior.

## Implementation

The reusable platform patch is `helium/ui/pinned-tab-groups.patch`. It retains groups as a leading portion of Chromium's unpinned collection rather than pinning individual member tabs, duplicating group views or adding another model collection. Model operations share the group pin state and regular-tab insertion boundary. Local pin metadata is persisted in session commands and recently closed group/tab records; legacy records default to unpinned. Collapse, rename and other ordinary visual-data updates preserve existing pin state.

New Tab belongs to the unpinned contents while the sidebar is mounted. Collection reset precedes region teardown, so removing the contents reparents the button to `TabStripView` before the region retrieves its placeholder. This fixes the review crash in `UnpinnedTabContainerView::RemoveNewTabButtonContainer()` during browser-window destruction. The owner's report occurred during a group drag that may have left the window; the symbolicated stack establishes teardown as the failing path.

A second review crash trapped in `InitializeDragStartAnimation()` when `dragging_views_.at(source_dragged_view)` looked up a source not attached to that container. Rebuilt symbols reproduce the original executable text section byte for byte, despite a different Mach-O UUID, and map all top stack addresses identically. Group-pin destination flags now require an actual group-header drag; ordinary tabs follow normal reparenting into the regular list. Optional contiguity animation skips an unattached source. The owner accepted the completed drag behavior; the automated coverage and remaining matrix limits are stated below.

The final review composition starts from accepted emoji input `cdea745ea5600098e382a7a3c13dc5652b20fd39` (`inputs/tab-group-emoji-1/macos`), with unchanged core `49bdc572bee38436250f9058351c8a328cd8c8ad`. Source development uses the existing prepared Chromium tree and quilt. The Native-theme caret correction and pinned-group feature are separate patches; the already-adopted emoji renderer is excluded from the pinned patch.

## Review evidence and limits

The owner accepted the final Native-theme hover/drag behavior and complete feature on November 12, 2026. Earlier owner checks accepted the separator and destination gaps, collapsed-group append behavior, selected target fill/text, whole-window gesture exclusivity, cursor-outside-window tear-off boundary and upper-sidebar single-tab dragging. Native automation that selected tabs without establishing a real move is not counted as gesture coverage.

Strict archive-backed replay covers 36 affected files, including current cursor and Native-selection dependencies, with zero feature fuzz/offsets and exact final source parity. Both final browser/driver builds and UI, Settings, browsing and persistence checks are recorded in the completion record. Apple silicon execution is native; Intel runtime uses Rosetta. Splitting the caret correction from pinned groups leaves the tested source byte for byte unchanged.

Earlier paired checks passed ten production session-command replay tests per architecture. A saved-session aging fixture confirmed that an overdue pinned group remains protected while an unpinned group ages with grouped cleanup enabled. The corrected headed lifecycle fixture passed group transfer that closes its source window, ordinary window closure and repeated orientation preference changes on both architectures. Its group creation explicitly names the source window.

The standard Chromium model-test executable remains blocked by a missing pruned WebUI Chai input; the added model regression sources were not executed. No physical Intel check or complete sidebar-side, focus-mode, detached, narrow/hover and split-child gesture matrix is claimed. Owner acceptance and the recorded focused checks establish the adopted scope. No browser release or deployment is authorized by this work.

The [completion record](../builds/2026-11-12-pinned-tab-groups.json) binds the final inputs, tested source, owner acceptance and validation limits. Temporary previews, profiles and replay copies have been removed after normal exit; source/build/compiler caches, signed component inputs and concise crash evidence remain.
