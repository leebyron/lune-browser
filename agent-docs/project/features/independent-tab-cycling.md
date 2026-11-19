# Independent tab shortcut order

[Issue #49](https://github.com/leebyron/lune-browser/issues/49).

## Behavior

**Appearance and behavior → Behavior** has independent per-profile controls.

| Keys | Default | Setting |
| --- | --- | --- |
| Ctrl+Tab and Ctrl+Shift+Tab | Most recently used | Cycle through tabs in most recently used order with Ctrl+Tab |
| ⌘⇧[ and ⌘⇧] | Sidebar order | Cycle through tabs in most recently used order with ⌘⇧[ and ⌘⇧] |

The Ctrl+Tab control keeps its saved value in existing profiles. The bracket control starts off. Both controls take effect in open windows.

In sidebar order, the left bracket selects the preceding tab and the right bracket selects the following tab. Cycling wraps within the window and follows the current order of pinned tabs, expanded groups, regular tabs and expanded Older Tabs. Collapsed groups and the collapsed Older Tabs section are skipped. In a horizontal layout, cycling uses the tab strip order.

The Ctrl+Tab visual switcher can show all eligible tabs in positional order. Its configured thumbnail limit applies in recent order. With the visual switcher off, Ctrl+Tab still uses the selected order. Bracket shortcuts switch immediately.

## Validation

Run [the native shortcut fixture](../../../scripts/check-native-tab-cycling.py) with Python and `websocket-client` against a built output directory. It uses a disposable profile, a local fixture extension and native Quartz keyboard events. It checks both preference bindings and defaults, both shortcut directions, changes with the browser open, saved settings, the visual switcher disabled, held Command, wraparound and tab arrangement.

The [adoption evidence](../builds/2026-11-19-independent-tab-cycling.json) records both builds, results for all 18 shortcut cases on each architecture, the two restored Older Tabs cases on Apple silicon, and full source parity. The Intel browser ran under Rosetta.
