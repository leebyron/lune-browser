# Expanded-group boundary separator

Requested and accepted November 13, 2026. Signed input `inputs/expanded-group-separator-1/macos` (`cc1132cbbe1b2edf19c1fe6b234693a466126abd`) is selected for future main builds. Published browser releases retain their frozen inputs.

## Behavior

An expanded vertical group followed immediately by an ungrouped tab row receives a horizontal rule in the gap. Ungrouped split rows use the same boundary. The rule reuses `SidebarScrollSeparator`, its one-pixel themed paint, the pinned rule's tab-content horizontal bounds, the group's existing trailing margin and eight DIP of clearance below the rule.

Collapsed groups, adjacent groups, the end of the list, New Tab and Older Tabs/date headings do not create this boundary. The existing pinned-section divider is reused without a second rule. Adjacency follows visible rows, including focus and Older Tabs presentation. Rules are presentation views, not tab-model children, drag destinations or focus targets.

## Implementation and current evidence

The quilt patch is `helium/ui/expanded-group-separator.patch`, based on published macOS input `60d037df61f275ec2edff170da907308a0fe3c54` with unchanged core `49bdc572bee38436250f9058351c8a328cd8c8ad`. `UnpinnedTabContainerView` owns one stable separator per direct group and uses its existing inherited view observer to follow group attachment/removal. The vertical layout shares the pinned-rule geometry and selects qualifying visible boundaries. Horizontal containers do not create these views.

Archive-backed replay covers all three affected files through seven parent patches with zero fuzz, zero feature offsets and exact source parity. Patch lint, both final builds, UI/Settings/browsing/persistence smoke and all 73 repository tooling tests pass. Apple silicon executes natively; Intel runs under Rosetta. The accepted native preview shows the rule after an expanded group followed by an ungrouped tab, and no rules between adjacent groups. Collapse removes the rule and re-expansion restores it. Closing the final group member removes its rule without a crash. Pin/unpin transitions use exactly one appropriate divider. Its framework UUID is `4C4C441B-5555-3144-A1C7-C30EE1523CFB`.

The owner accepted the appearance and requested shipment. The [completion record](../builds/2026-11-13-expanded-group-separator.json) binds the accepted preview, replay, both builds and smoke reports. No separate GitHub issue is associated with this follow-up. No physical Intel or full Older Tabs/date-heading, split-row, focused/narrow/hover sidebar or detached-drag matrix is claimed.

The temporary preview exited normally. Its disposable app, profiles, fixtures, replay copies and clean patch clone are removed. The current prepared source, active quilt stack and incremental build/compiler caches remain available.
