# Header hover beside docked DevTools

Requested November 10, 2026. Side-docked DevTools should not reveal the floating header when the pointer enters its top edge. The page content and visible tabs sidebar remain eligible.

## Implementation

`BrowserView::IsPointInTopChromeHoverArea()` projects each visible content container's current page bounds onto the top hover region. Left- and right-docked DevTools columns are excluded, including the frame border beside them. A visible tabs sidebar takes precedence when it overlaps those columns. Bottom-docked, undocked, and hidden DevTools preserve the existing top-edge behavior.

Both Views trigger/retention checks and native macOS trigger/retention checks use this gate. Entering DevTools also stops pointer retention of an already visible header. Existing keyboard editing, pinning, menu holds, Customize, dragging, and native resize holds retain their independent behavior. The top/side trigger thicknesses and toolbar layout are unchanged.

The reusable platform patch is `patches/helium/ui/devtools-header-hover.patch`, committed as `470c9465957673cfd817d557635f5f676ccfba75` on `devtools-header-hover` and retained by signed tag `inputs/devtools-header-hover-1/macos`. It is based directly on the preceding locked platform `1cd15a9c968749af7911e609445823c3092512e6`. The development lock and patch provenance include it for future builds; published releases retain their frozen inputs.

## Validation

The patch was developed in the prepared Chromium tree with quilt, refreshed, and unmerged into the isolated platform checkout. Zero-fuzz replay reproduces all three affected source files. Platform patch lint passes.

Run the production-method regression fixture with:

```sh
python3 scripts/check-header-devtools-hover.py .work/search-suggestions/platform/build/src --arch arm64
python3 scripts/check-header-devtools-hover.py .work/search-suggestions/platform/build/src --arch x86_64
```

Both pass; the Intel fixture executes under Rosetta. Cases cover exact left/right dock boundaries, visible and hidden overlapping sidebars, bottom/undocked/hidden DevTools, inactive hidden content containers, both split panes, and changing splitter geometry. The fixture also checks that native and Views entry/retention paths call the shared gate. This verifies the production geometry method with lightweight view stand-ins, not physical cursor behavior.

Both arm64 and x86_64 browser builds pass. UI/defaults, loopback browsing, JavaScript and profile-persistence smoke checks pass on both architectures; Intel executes under Rosetta. The first Intel run timed out during loopback navigation; the repeat using the project's clean runtime environment passed. Both changed GN targets pass dependency checks, all 32 lock/component tests pass, and documentation link/whitespace checks pass.

The owner accepted the live Apple silicon preview on November 10, 2026: “great this looks like a fix to me.” The preview runs with an isolated profile and DevTools docked to the right. Its first shell-sandboxed launch aborted in AppKit/HIServices application registration before the browser window existed; relaunch outside the command sandbox succeeded. The attached crash report is not evidence of a hover-path crash.

The preview/build workspace also contains the concurrent bang-suggestions feature. Its patch does not touch any of the three header source files, and those files replay identically from the focused locked composition. The new platform input excludes that unrelated feature. Fullscreen, bottom docking, left docking and the multi-window pointer matrix were not separately owner-accepted; native Intel hardware was not tested. Local detailed evidence is under `.work/devtools-header/`.
