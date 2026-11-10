# Application-menu update check

Status (2026-11-10): implemented and accepted by the owner in Lune Update Test. Signed platform commits `e02bcdba6eecaa8fa953551fec10c2e6388c98a4` and `9ceaaad8a2f71ece40aab464c6504ee1f356312f` are retained under `inputs/app-menu-update-1/macos`. Main adopts this input for future builds. Published 26.1109.1 and 26.1109.2 binaries remain unchanged.

## Behavior

Check for Updates… appears immediately below Import Bookmarks and Settings… in the macOS application menu, with no keyboard shortcut. It is localized and excluded from PWA menus. The action uses the existing asynchronous profile-loading path and opens About Lune. An already-open About page reloads for an explicit check; a new or loading page requests status during its normal initialization.

The shared Sparkle updater remains authoritative. Repeated checks retain an active download's progress or a ready update rather than creating competing sessions. Successful updater startup is retained; failed startup can be retried. The action does not restart the browser, bypass consent, change the selected channel, or create a second updater. When updates are off or unavailable, About explains the state and links to the existing Update settings page.

The separate Lune patch changes the Sparkle delegate's feed base to `https://raw.githubusercontent.com/leebyron/lune-browser/main/updates/stable/` and corrects the settings disclosure to identify GitHub as the browser-update host. Release tooling also embeds the canonical architecture-specific URL in `SUFeedURL`. Changing only the plist would not update the delegate's feed selection.

## Validation

- Strict zero-fuzz replay of both patches matches all twelve changed source files; both resource XML files parse and platform patch lint passes.
- Both complete browser builds pass. Apple silicon runs natively; Intel smoke checks run under Rosetta.
- `scripts/check-native-update-menu.py` compiles production menu, dispatch and updater state code into an AppKit fixture for each architecture. It checks placement, separator, target, localization, no shortcut, PWA exclusion, asynchronous profile loading, no-window dispatch, profile failure, shutdown, startup retry, repeated checks, progress replay, ready updates and disabled consent. Browser/profile/Sparkle dependencies are stubbed; this does not establish a physical Intel or full installed-update test.
- UI/settings/persistence and internal-artwork smoke checks pass on both architectures with isolated profiles and local update feeds.
- Live Apple silicon inspection confirms menu placement, visible progress from the canonical public feed, repeated checks, disabled-update explanation and navigation to Update settings without changing consent. The owner accepted this flow. The native automation cannot interact with the menu when no windows exist; that path is covered by the dispatch fixture rather than a live pointer test.
- The compiled Apple silicon framework contains the canonical feed base and no former repository feed base; its bundle plist uses the matching architecture endpoint.

Local evidence is under `.work/issue-24/`: `strict-replay.json`, native-menu logs, both validated build logs, `smoke-arm64.json`, `smoke-x86_64.json` and `menu-disabled.png`. These are development builds, not new signed/notarized release artifacts. The next frozen release requires fresh complete source preparation, both frozen builds, packaging and installed-update acceptance.

## Patch workflow and isolation

The prepared source and build caches were APFS-cloned from the frozen 26.1109.2 workspace. That baseline was not edited. Full source comparison isolated the twelve intended changes before native Siso cache import. The patches were developed with quilt, refreshed and unmerged into the platform repository. The generic menu/updater behavior is separate from Lune's hosting and disclosure patch; the core gitlink and all prior feature patches are unchanged.

A first build used an inherited GNU `ln` before macOS `ln`, causing Sparkle's Xcode script to reject `-h`. Rebuilding with the project's existing clean `lune.build_env()` passed without source or toolchain changes. Keep using that build environment.
