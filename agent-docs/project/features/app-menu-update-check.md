# Application-menu update check

Status (2026-11-10): implemented and accepted by the owner in Lune Update Test. Signed platform commits `e02bcdba6eecaa8fa953551fec10c2e6388c98a4` and `9ceaaad8a2f71ece40aab464c6504ee1f356312f` are retained under `inputs/app-menu-update-1/macos`. Main adopts this input for future builds. Published 26.1109.1 and 26.1109.2 binaries remain unchanged.

## Behavior

Check for Updates… appears immediately below Import Bookmarks and Settings… in the macOS application menu, with no keyboard shortcut. It is localized and excluded from PWA menus. The action uses the existing asynchronous profile-loading path and opens About Lune. An already-open About page reloads for an explicit check; a new or loading page requests status during its normal initialization.

The shared Sparkle updater remains authoritative. Each About load requests a background check, including when a release is ready. A load during an active check or download joins that session and displays its progress. Successful updater startup is retained; failed startup can be retried. The action does not restart the browser, bypass consent, change the selected channel, or create a second updater. When updates are off or unavailable, About explains the state and links to the existing Update settings page.

The separate Lune patch changes the Sparkle delegate's feed base to `https://raw.githubusercontent.com/leebyron/lune-browser/main/updates/stable/` and corrects the settings disclosure to identify GitHub as the browser-update host. Release tooling also embeds the canonical architecture-specific URL in `SUFeedURL`. Changing only the plist would not update the delegate's feed selection.

## Staged-update regression

Sparkle checks the feed on its regular schedule while a release is ready. An About load also checks immediately. When the feed contains a newer eligible release, Sparkle downloads it and prepares it for installation. Normal quit installs the latest prepared version. Relaunch to update installs that version and opens it again. An unchanged offer keeps the staged copy without downloading it twice.

Lune previously returned early from the About check and held Sparkle's postponed-relaunch callback, keeping its update cycle busy. Sparkle 2.10.1 also resumed the staged installer on subsequent background checks. The platform input ports the framework's supersession support and lets the background cycle finish after recording the staged version and its release notes. Sparkle keeps its upstream restriction on superseding installers that required administrator authorization. [Sparkle PR 2928](https://github.com/sparkle-project/Sparkle/pull/2928)

A download failure preserves the earlier installer. Once the replacement installer takes over, a signature failure clears the ready action and About reports the error. Quitting then leaves the running version installed.

[The loopback integration test](../../../scripts/release/check_staged_update.py) copies an updater-enabled, pre-signing Lune.app to a temporary directory. It gives that copy a unique bundle identifier, a private profile and an ephemeral public key. A mutable local appcast serves two Ed25519-signed ZIPs with matching fixture bundles. After About reports the first update ready, the server switches to the second. The test requires a new feed request, a request for the second archive, a fresh ready notification and the second version installed on quit. It writes request timings and the installed version to `result.json` and exits nonzero on regression.

```sh
.work/venv/bin/python scripts/release/check_staged_update.py \
  --app "$OUT/Lune.app" --driver "$OUT/chromedriver" --arch arm64 \
  --trigger about --directory .work/staged-about --openssl /opt/homebrew/opt/openssl@3/bin/openssl
```

Use `--trigger automatic` and a fresh evidence directory for the scheduled case. The fixture uses Sparkle's one-hour release-build minimum. With a Lune test bundle containing a Debug build of the same patched Sparkle framework, add `--debug-interval` to use its supported one-minute minimum. That case starts with an empty feed and waits for the real scheduler to discover the first release before testing the next interval.

Use `--offer unchanged`, `--offer download-error` or `--offer bad-signature` to exercise repeated offers and replacement failures. Use `--finish relaunch` with a newer offer to verify the native relaunch action starts the new executable. [Replacement validation](../builds/2026-11-21-staged-update-replacement.json)

On 2026-11-21, platform input `100deb1ff459c2c496650d4dd9e335c26ba4488b` with Sparkle 2.10.1 reproduced the regression. About reloads on native arm64 and x86_64 under Rosetta made zero feed requests in the following 30 seconds. On arm64, the Debug scheduler checked the initially empty feed again at 63.8 seconds, staged 99.1.2, then made zero feed requests in the following 90 seconds with 99.1.3 available. All three runs installed 99.1.2 on quit. An arm64 control with an empty initial feed fetched 99.1.3 on About reload, emitted a fresh ready event and installed 99.1.3 on quit.

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
