# Stable command-menu glass

Owner-accepted fix for [issue #27](https://github.com/leebyron/lune-browser/issues/27), November 11, 2026. Both Cmd+T and Cmd+/ use `HeliumCommandBarView` and share this material policy.

## Cause and change

The menu already uses `NSGlassEffectViewStyleRegular`; it does not select Clear when results disappear. Its height changes from the 52 pt input-only state to a five-row panel as results change. Regular AppKit glass itself becomes clearer and can change light/dark tone when its surface becomes small. A headed native comparison reproduced a frosted light large panel and a transparent dark compact panel over the same black backdrop, despite an explicit Aqua appearance.

Apple describes this size-dependent behavior in its [glass sizing discussion](https://developer.apple.com/videos/play/wwdc2025/284/?time=188) (UIKit guidance; the native comparison is the AppKit evidence). The installed public `NSGlassEffectView` header exposes Regular/Clear style, corner radius, tint, content, and interactivity. It has no public control to force the larger-surface treatment at every size.

The fix keeps the menu's existing neutral 80%-opacity backing visible at every size. Previously Content aware hid that backing, exposing the size-dependent transparent/tone-switching behavior. This is a menu-specific use of the existing fixed composition policy: the browser's Light/Dark/System appearance still chooses the neutral backing, and regular Liquid Glass, theme tint, native foreground legibility, and existing shadows remain. Header/sidebar Content aware behavior is unchanged.

The material stays attached. Search, ranking, commands, bounds, keyboard focus, provider pills, scrolling, selection, and dismissal are unchanged. No private API, sampling, polling, hidden material, or additional blur pass is introduced. The older-macOS popover fallback is unchanged. Native compositing can still subtly vary; this prevents the transparent/tone-inversion transition rather than claiming identical pixels across sizes or arbitrary page colors.

## Source and workflow

The focused platform branch starts at locked input `009caf230874153962f9965367ab79e789c8ed36` (`inputs/search-suggestions-context-1/macos`). Eighteen patches from that input strictly replay to the exact current prepared `helium_command_bar_view_mac.mm` before editing. The canonical development source is `.work/search-suggestions/platform/build/src`; frozen release trees are untouched.

The change was made in the prepared source with quilt, refreshed, and exported through Helium's platform merge/unmerge tooling. It adds one patch, `helium/ui/command-menu-stable-glass.patch`, and one platform series entry. Its zero-fuzz replay matches the source used for compilation byte for byte. The development lock now selects this accepted fix for future main builds through `inputs/command-menu-glass-1/macos`. Published releases keep their frozen inputs.

## Validation

- Platform patch lint, strict zero-fuzz replay, locked ancestry/tag/tree/gitlink validation, and all 73 repository tests pass.
- `check-native-chrome-appearance.py` passes on arm64 and x86_64 under Rosetta, retaining the shared header/sidebar lifecycle checks and updating Command-T's backing expectation.
- `check-native-command-menu-glass.py` compiles the production material and construction. It passes 162 combinations per architecture: profile Light/Dark, black/white/red backdrops, widths of 600/360/220 pt, and repeated heights of 52–319 pt. Checks cover effective foreground appearance, persistent material/content, backing and shadow bounds, and editor focus/selection. The original implementation fails the new regression because it hides the backing in Content aware mode.
- These native fixture checks establish appearance/lifetime behavior, not compositor pixel equivalence. Headed browser review remains separate.

Both full browser builds pass (arm64 and x86_64). Live arm64 inspection of **Lune Menu Glass Test** confirms compact Cmd+T over black, full/two-result/empty Cmd+/ over black in Light appearance, Cmd+T results over red, and full/empty Cmd+/ over white in Dark appearance. The material stays frosted with readable foregrounds. Content aware was enabled in the disposable profile. Escape dismissal and result filtering work. The preview has its own bundle identity and disposable profile, and its ad-hoc code signature verifies.

Implementation is signed commit `7e40287873ebf0e5bc465c64960485f76391cd6a` on `topic/command-menu-stable-glass`, with permanent input `inputs/command-menu-glass-1/macos`. The native regressions and evidence are committed on main. The temporary preview and comparison app were quit after acceptance. Task-specific profiles, native fixture binaries, and scratch replays are cleaned after durable source and validation are published; the shared Chromium source and compiler outputs are retained.

The owner accepted the preview on November 11, 2026, and requested quitting and cleaning up the temporary artifacts, adopting the fix in future main builds, and closing #27 after pushing. Physical Intel, live Device appearance, system accessibility-setting visual checks, and older-macOS visual checks remain unverified. Native Intel evidence is limited to x86_64 fixtures under Rosetta. No broad browser/settings smoke matrix was repeated for this material-policy change. Source publication and development-input adoption resolve #27; this does not publish a new browser release.
