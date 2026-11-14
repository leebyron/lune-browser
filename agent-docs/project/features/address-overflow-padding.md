# Address text padding while scrolling

Issue: [#34](https://github.com/leebyron/lune-browser/issues/34).

## Behavior and implementation

Cmd-L keeps the address text aligned with the completion titles when a URL exceeds the available width. The text retains its spacing beside Site Information and Reload while scrolling to either end.

AppKit's normal 2 pt line-fragment padding belongs to the scrolling text, so clipping can consume it. The native address field now reserves that margin in its frame and removes the duplicate internal padding from its field editor. Short editing text keeps its existing position. The idle display retains native padding and centering. Shared field editors restore normal padding when used by another control.

The focused platform patch is `helium/ui/address-overflow-padding.patch`. It changes only `chrome/browser/ui/views/frame/browser_frame_view_mac.mm`, including ordinary editing, relayout and bang scope geometry. Word navigation still inherits the existing native cell.

## Validation and acceptance

The owner accepted the native Apple silicon preview on November 13, 2026: “Fix looks correct.” Native screenshots show matching address/result text columns for short and overflowing URLs, including a horizontally scrolled URL.

`scripts/check-address-overflow.py` checks the production address cell and frame helper with real AppKit editing. It verifies the short-text origin, fixed clipping margins at the start/middle/end, empty input, widths representing Reload visibility and bang scopes, resizing, and shared-editor padding reset. Both architectures pass; Intel executes under Rosetta. The original layout fails the clipping assertion.

Final composition, build, smoke, source identities and cleanup are recorded in [the completion evidence](../builds/2026-11-13-address-overflow-padding.json). The patch replays with zero fuzz and zero offsets against the accepted parent. There is no fresh full Chromium preparation, physical Intel or macOS 13 runtime claim.

Adopted for future main builds on November 14, 2026 through signed input `inputs/address-overflow-padding-1/macos` at `d7c555a12b3753694f9cd97427a41cbea68e9c41`, based on `6712c22a87c728c19d7cb43dc7c794906cbe3ea3`. Both final browser builds and browsing/UI/Settings/persistence smoke checks pass; Intel executes under Rosetta. Issue #34 is resolved by this adoption. Published 26.1113.1 remains unchanged.
