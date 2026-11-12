# Toolbar hover modes

Requested November 12, 2026. The development lock selects signed input `inputs/toolbar-hover-order-1/macos` at `3aa1b256f8b18b802b2d076a293a953417c9697d` for future main builds.

## Behavior

Show toolbar uses **On hover edge**, **On hover sidebar**, then **Always** in setup. The toolbar/sidebar context menu and Appearance settings use those three choices followed by **Always cover (experimental)** as the final option. Setup continues to exclude experimental cover.

The new mode disables only entry through the page's top-edge hover rail. A visible sidebar's upper region still reveals the toolbar. Address editing, Downloads details, toolbar bubbles, explicit menu holds, pinning and Customize retain their existing behavior. Once revealed, ordinary pointer retention and dismissal remain intact, including the existing exclusion of side-docked DevTools. The preference applies to the profile and updates open windows immediately. Existing profiles and fresh profiles keep the edge-hover behavior as their default.

The edge-triggered mode is labeled **On hover edge** throughout these surfaces. The profile preference `helium.browser.top_controls_hover_disabled` defaults false. On hover sidebar sets it true and clears toolbar pinning and overlay. Selecting any other toolbar mode clears it. The native menu and Settings derive their mutually exclusive selection from these preferences; setup preserves its existing Always display for a saved experimental cover mode.

The independently accepted [extension-popup retention fix](extension-popup-retention.md) keeps the toolbar visible while an extension action popup is open in either hover mode.

## Source and validation

The platform quilt patch is `helium/ui/toolbar-not-on-hover.patch`. It was developed in an isolated prepared-source subset, then exported on top of the separate accepted extension-popup fix and the current selected-search-engine input. The prepared development source also contains a separately active native-editor focus patch; that patch is excluded from this component's changes.

Focused replay reproduces all 19 changed files with zero fuzz and zero offsets. Composition replay of the 14 Chromium-origin files applies the selected core/platform stack from the pristine archive with zero fuzz and reproduces the source after production substitutions and the separately recorded editor delta. The five onboarding files use retained exact prepared-source preimages. This is changed-file validation, not a fresh full-tree preparation.

`scripts/check-toolbar-visibility.py SOURCE --arch arm64|x86_64` compiles the production preference-selection, preference-write, rail and native presentation expressions. Both architectures pass mutually exclusive modes, all four transitions, rail gating and 2,048 engagement states. Existing DevTools hover and sidebar-drag decision fixtures pass on both architectures. These are production-expression fixtures, not physical pointer acceptance. Onboarding Svelte/TypeScript checks and production bundling pass. Both final browser builds, packaged Settings transitions/defaults/restart checks, browsing smoke and packaged setup flow pass. Intel executes under Rosetta. Native Apple silicon inspection confirms the four final menu labels and setup exposes the requested two hover labels alongside Always. The owner accepted the extension-popup fix and supplied the exact final hover labels.

No specific GitHub issue was assigned to this request. The current published browser and frozen release records remain unchanged.

The [validation record](../builds/2026-11-12-toolbar-hover-options.json) retains exact source/input hashes and test-artifact scope. Initial Intel test copies were silently replaced by Sparkle with published 26.1111.3. Final tests use an exact development package, disable browser updates only in the disposable Settings profile, use loopback update feeds and verify the app hash/version remain unchanged after every check. This does not change production update behavior.

## Confirmed ordering

The owner confirmed the final order and requested a focused commit/push. `helium/ui/toolbar-hover-order.patch` reorders the shared native menu, Settings options and setup options without changing preferences or reveal behavior. Both builds and packaged mode/persistence/setup checks pass, with Intel under Rosetta. Native menu inspection confirms the four-item order. The [ordering validation record](../builds/2026-11-12-toolbar-hover-order.json) retains exact inputs, package hashes and limits. The concurrent session-restore input is preserved as this input's parent.
