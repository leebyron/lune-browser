# Header visibility during sidebar window dragging

Issue [#29](https://github.com/leebyron/lune-browser/issues/29). Implemented and committed locally on November 11, 2026. The local development lock selects signed platform `4c97c78c54a326e093e35552c466181269ea4e10` through `inputs/sidebar-drag-header-1/macos`, based on `a7fef19376b799585e4a62bfd9bfe25ba6d26d47` with unchanged core `49bdc572bee38436250f9058351c8a328cd8c8ad`. Publication and owner-confirmed native gesture acceptance remain pending; the issue stays open.

## Behavior

The pinned sidebar's native blank-space handler and the floating sidebar's child-window handler both feed `IsFloatingChromeDragging()`. Previously `UpdateFloatingAddressBar()` treated that flag as a reveal request, making a hidden header appear on a sidebar press/drag.

The new `helium/ui/sidebar-drag-header-retention.patch` places native window dragging in the existing presentation-hold branch with live resize and native menus. A hidden header stays hidden and a visible header stays visible throughout the gesture. Geometry continues updating, sidebar retention and mouse-up detection use the existing native path, and ordinary hover/collapse resumes after release. Explicit Always pinning, Customize and header-menu reveals retain their precedence. No new timers, event interception or persistent state were added.

## Validation and limits

Developed in the existing prepared Chromium workspace with quilt, refreshed and exported with the platform unmerge tool. Replaying all 73 locked core/platform patches touching the source file from its retained prepared preimage matches the compiled source byte for byte with zero fuzz. The new patch has zero offsets; six earlier patches retain recorded offsets. This is changed-file composition validation, not a fresh full-tree preparation.

`scripts/check-header-drag-retention.py SOURCE --arch arm64|x86_64` compiles and executes the production Objective-C++ presentation expression against lightweight state stand-ins. All 4,096 combinations pass, covering hidden/visible dragging, pointer triggers, explicit pin/menu/Customize precedence, existing resize/menu holds, editing and bubbles. A transition sequence checks release and subsequent hover/collapse. Before the fix the same check failed for a hidden header with dragging active. These are presentation-decision tests, not physical drag tests.

Both full browser/driver targets pass, as do both browser smoke/default/settings/persistence checks and the existing DevTools hover regressions. Intel execution uses Rosetta on the Apple silicon host; physical Intel was not tested. Core/platform patch and translation lint pass. Compact evidence is in [the validation record](../builds/2026-11-11-sidebar-drag-header.json).

An isolated arm64 preview was launched, but the native computer-use service timed out before returning its UI state. No native drag, inactive-window, left/right floating-sidebar, resize-handle or fullscreen gesture matrix is claimed. Owner acceptance remains required before publication and issue closure. The installed app and published 26.1111.2 release are unchanged.

The temporary preview app/profile and disposable replay tree were removed after recording results. Prepared Chromium, both build outputs, the component input and compact logs remain available.
