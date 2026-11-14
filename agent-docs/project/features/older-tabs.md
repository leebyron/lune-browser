# Automatic Older Tabs

Issue [#20](https://github.com/leebyron/lune-browser/issues/20). The owner accepted the native preview on November 11, 2026 and requested a focused commit for future main builds. The original adoption selected signed platform commit `a7fef19376b799585e4a62bfd9bfe25ba6d26d47` through `inputs/older-tabs-1/macos`. Published 26.1111.2 and its frozen inputs are unchanged. Later changes and input selections are recorded below.

## Lifecycle and ordering

Older Tabs remain live WebContents in their original browser window. A browser-owned controller maintains a trailing tab-model segment, so extension indices, keyboard cycling, selection, close buttons and Command-T switching continue to refer to the actual tabs. This feature does not itself discard pages or save memory.

| Action | Regular age baseline | Older close clock | Placement |
| --- | --- | --- | --- |
| Activate or send trusted page input to a regular tab | Reset | None | Regular |
| Reorder regular tabs or complete a batch/no-op drag | Preserve | None | Use the chosen regular placement |
| Reach the move threshold | Preserve | Start at transition | Older, sorted by frozen last use |
| Interact with an Older tab | Preserve | Preserve | Stay in its frozen date bucket |
| Keep Tab | Reset | Clear | Restore its logical regular-stack position |
| Complete drag into regular tabs | Reset | Clear | Use the chosen drop position |
| Cancel drag or return to the Older region | Preserve | Preserve | Retain the original Older position |
| Reopen a recently closed tab | Fresh | Clear | New regular residency and identity |

Activity updates last-use history without extending an Older tab’s fixed entry-based retention clock. Qualifying input is activation or Chromium's browser-side trusted pointer, key, touch or scroll-start event. Background navigation, network traffic, title changes, animation and hover do not count. Arrangement-only movement preserves last use and the regular aging baseline, including regular-tab and group reorders, extension/model moves, window transfers and completed drags that end at the original positions or only move a window. Normal activation still counts if the gesture selects a different tab. Deliberately dragging an Older tab into the regular stack retains its Keep semantics. Persisted state includes a stable random identity, last use, independent regular age and close baselines, frozen pre-entry last use and a logical ordering key. Keep preserves relative order even when several tabs age out and are kept in reverse order. Missing neighbors use surviving logical order; a newly formed group uses its leading boundary. Explicit drag establishes the new position.

Lifecycle metadata follows window transfer and replacement/discard. Recently-closed recovery clears residency and receives fresh aging grace. Missing, malformed or future metadata is treated conservatively. Existing tabs receive a first-observed last-use fallback and a fresh regular age baseline. One sweep performs at most one transition per tab; downtime cannot move and immediately close the same regular tab.

## Settings and protection

Appearance and behavior provides two independent local profile settings. **Move inactive tabs to Older Tabs after** defaults to **1 day**, with Never, 6 hours, 1 day and 2 days. **Close Older Tabs after** defaults to **3 days**, with Immediately, 1 day, 2 days, 3 days, 7 days and Never. Durations use elapsed hours independently of calendar headings. Browser-side validation rejects invalid finite values and bounds them to one year.

Never for moving suspends cleanup, hides the Older section and date headings, shows all live tabs, and restores ordinary tab menus. It collapses the close and group controls without erasing their values. A finite duration restores the section and its commands; latent membership is retained. There is no separate Organize inactive tabs switch. Immediately closes eligible regular tabs directly at the move threshold, without entering Older Tabs. Protected or grace-delayed tabs stay regular until safe.

Pinned and split tabs never age into Older Tabs. **Move inactive tabs from groups**, described as “Allow moving inactive tabs from tab groups to Older Tabs”, defaults off. When enabled, eligible members leave their groups individually; Keep does not recreate the original group. Cleanup waits for saved-group initialization and restoration connections before removing group members.

Selected/visible or loading tabs, audible media, capture/sharing and either picture-in-picture mode are protected. Automatic closing also defers unload handlers and active profile downloads. It uses Chromium's historical close path without impersonating a user gesture. A page without an unload handler cannot reliably advertise unsaved state; Recently closed retains Chromium's normal recovery limits.

Automatic closing waits five minutes after launch, resume or a settings change, and waits for restoration and dragging to finish. A one-minute window timer drives reconciliation; input persistence is coalesced. Incognito cleanup is disabled and data remains in memory. Horizontal tabs suspend transitions and show every tab. Preferences are shared by a profile's windows and are not synced.

Older tabs follow the startup preference: Continue where you left off restores them across a clean quit, including their identities, frozen dates and close clocks. Open the new tab page and Open a specific page or set of pages start without Older tabs. Recovery history remains separate from automatic restoration.

## Sidebar and commands

Older Tabs has no count or leading icon. It uses semibold system text at tab-label size and native secondary color. Its hover-only native chevron uses the same shared 11pt medium SF Symbol renderer and 16px canvas as tab close icons, with the header foreground as its fallback and the native glass control color when available. The accepted layout retains the label's optical vertical alignment and removes the additional 2px chevron adjustment. The header has 18px content and a 24px hit target extending upward; separation above it is two thirds of a blank tab-row slot.

There is no extra nesting inset. Full-width tab rows retain their normal content alignment. Compact uppercase date headings align with the section title, three font-size steps below tab text. Their 16px rows trim the previous spacing, consume the preceding tab's 2px gap, and raise the glyph 1px within its box. Date labels use native secondary color with a further 15% alpha reduction. Today and Yesterday have no heading; days two through seven use localized weekday names, and dates beyond seven calendar days share Older. Calendar arithmetic is independent from elapsed-hour deadlines and handles daylight-saving changes. Refreshes reflect the current locale and timezone.

Date views are stable calendar-bucket views animated with surrounding tabs, not groups or drag sources. An Older tab may return to its original chronological slot or move above the divider; the Older region rejects arbitrary reordering. Activation expands the section without keeping the tab. Disclosure is local per profile.

The header context menu offers Close All Older Tabs, Keep All Older Tabs and Settings. Bulk close uses ordinary user-initiated historical closing with unload handling; bulk Keep restores logical positions. Individual Older-tab menus omit New Tab Below, Add/Move submenus, Pin, Close Other Tabs and Close Tabs Above. Keep Tab appears in both Command-T and Command-/ only for an active Older tab while cleanup is enabled, with dispatch revalidation.

## Source and validation

The reusable platform patch is `helium/ui/automatic-older-tabs.patch`, based on platform `651e911573be598a6cf348467169b4ce25ea6d36` and unchanged core `49bdc572bee38436250f9058351c8a328cd8c8ad` (Chromium `158.0.8127.18`). It was developed in prepared Chromium with quilt and exported into the platform. Final cleanup shares the close/disclosure symbol renderer, centralizes duration defaults, removes unused toggle/help resources, reuses one calendar calculation, and formats touched code.

The [adoption record](../builds/2026-11-11-older-tabs-adoption.json) identifies the final patch, builds, checks, owner acceptance and completion. The two earlier [initial](../builds/2026-11-11-older-tabs-review.json) and [revised](../builds/2026-11-11-older-tabs-review-2.json) reports retain review-stage evidence, not current inclusion state.

Both complete browser/driver builds pass on the local Apple silicon Mac. Runtime checks pass natively on arm64 and under Rosetta for x86_64: exact Settings choices/defaults and Never collapse, pinned exclusion/stale-state repair, group exclusion and opt-in after restore, direct Immediately closing with unload protection and recovery, all three startup modes, and Never persistence. Initial Rosetta ChromeDriver attachment timeouts are retained; subsequent serial cases pass with a longer attachment deadline. Command-registry regressions pass on both architectures, including conditional Keep availability and stale-state rejection. Native preview checks cover section disclosure, reduced tab menus, header actions, both Keep palettes, bulk Keep/Close, and Never hide/re-enable behavior. The owner accepted the final appearance.

Focused replay applies the feature to retained prepared preimages with zero fuzz, zero offsets and exact byte parity. An independent check extracts the SHA-256-pinned pristine Chromium archive and replays all 100 composed core/platform patches touching the 29 feature files, followed by the official domain/name substitutions; every final byte matches the compiled source. It uses the preparation tool's normal whitespace policy and zero fuzz. The pre-substitution XML has four extra lines, producing one recorded four-line offset in the feature's settings-string hunk. This is composed-file validation, not fresh full-tree preparation. Earlier replay attempts omitted the preparation tool's whitespace option and failed on a historical EOF context; they are superseded by the matching pipeline check.

Nine model-regression sources compile for both architectures. The complete Chromium unit-test executable was not linked or executed. Native pointer automation did not establish actual drag gestures, so drag behavior has source/model coverage and aggregate owner acceptance, without a separate recorded manual gesture matrix. Physical Intel hardware was not tested. New strings retain English fallback; translations were not authored.

`scripts/check-older-tabs.py BUILD_OUTPUT NEW_EVIDENCE_DIR` uses isolated local profiles/pages, matching ChromeDriver, mock Keychain and Python requests. Its default retention case takes about six minutes. Short variants include `--settings-check`, `--pinned-check`, `--group-check` (optionally `--move-grouped`), `--startup-check continue|new-tab|urls`, and `--never-check`; `--immediate-check` observes the real launch grace. `--interactive --review` creates a disposable manual preview. Temporary profiles and preview copies are removed after completion; screenshots and compact reports remain under `.work/older-tabs/`.

## Shared disclosure and collapse animation — November 11, 2026

The owner accepted the final Older Tabs presentation and motion alongside the sidebar group and scrolling refinements. Future main builds select signed input `inputs/sidebar-reviewed-1/macos`, ending at platform `51acf1cc9d8cb0ec4b6a71e40c4416bb10b93175`. Published release inputs are unchanged.

Older Tabs now expands and collapses through the existing tab-collection animation coordinator, with the same timing, easing and reduced-motion behavior as tab groups. Rows and date headings retain full geometry inside an animated clipped host. Their visibility and content extent no longer jump at collapse start, and a reversal starts from the currently drawn host height. The shared section-header disclosure is 2 px farther left, aligning group and Older Tabs chevrons with the tab controls.

Weekday headings cover tabs from the preceding six calendar days, with the existing unheaded Today/Yesterday treatment retained. Tabs seven or more calendar days old share Older. The date-label text and bucket key use the same boundary. Aging, automatic closing, Keep actions, saved tab order and protected-tab rules are unchanged.

These are three focused patches: `helium/ui/older-tabs-collapse-animation.patch`, `helium/ui/older-tabs-weekday-headings.patch` and `helium/ui/sidebar-disclosure-alignment.patch`. The [adoption record](../builds/2026-11-11-sidebar-reviewed-adoption.json) records builds, compiled test files, visibility/extent and reversal fixtures, date-boundary checks, exact archive replay and owner acceptance. Intel runtime uses Rosetta. The review apps and test profiles are cleaned up after acceptance; prepared source and build caches are retained.

## Arrangement preserves inactivity — November 13, 2026

Signed platform input `inputs/older-tabs-arrangement-1/macos` at `3543de9e3f4030a7c221e9d70792b52b2f38d394` selects the arrangement fix for future main builds. Published 26.1113.1 and its frozen source and artifacts remain unchanged.

Completing a regular-tab drag previously reset its independent aging baseline even when the tab returned to the same position. A select-all drag could therefore give every regular tab another 24 hours without updating its last-use date. Ordinary model reorders also synthesized interaction. The focused `helium/ui/older-tabs-arrangement-aging.patch` removes those activity writes while retaining logical placement updates, ordinary activation/page input and deliberate Keep/Older-to-regular behavior.

Both architecture browser builds pass. Production clock methods pass a 13-tab no-op, reordered and cancelled-drag fixture, including Older placement/cancellation/Keep and genuine interaction; the released code fails the no-op case. Four added Chromium model regressions compile for both targets. Real isolated browsers pass saved-state single and batch reorders, activation and browsing/settings/persistence smoke; the released arm64 browser fails the saved-clock reorder case. Intel executes under Rosetta. App/framework hashes stay unchanged throughout browser checks.

The patch was developed in a separate APFS clone of the retained release preparation and outputs, refreshed with quilt and exported through platform merge/unmerge. Two-file replay against preimages verified by the frozen complete-source inventory has zero fuzz, zero offsets and exact final parity. This is focused replay, not another fresh full preparation. The full Chromium unit-test executable was not linked or run, and native pointer automation did not independently establish a batch/window drag. The [completion record](../builds/2026-11-13-older-tabs-arrangement.json) records exact identities, checks and cleanup. No specific open GitHub issue tracks this change.

## Native disclosure, motion and outgoing drag slots — November 13, 2026

The owner accepted the final preview. Signed input `inputs/older-tabs-disclosure-1/macos` at `dda1bdf0de0c3e04532adbc16f2aebcd6a1d8d63` selects `helium/ui/older-tabs-disclosure.patch` for future main builds. Published 26.1113.1 and its frozen artifacts remain unchanged.

The Native chevron uses the section foreground as its fallback, matching group headers while retaining the native glass override. The Older Tabs header is excluded from Tab focus while retaining mouse and accessibility actions.

Runtime diagnostics showed the existing disclosure animation completing its 200 ms height transition while its scrolling host filled the viewport instead of shrinking with preferred size. A temporary compositor clip now follows the animated content edge and clears at completion or during dragging. Rows keep full geometry; timing, easing, reversals and reduced-motion handling continue through the existing collection coordinator. The first working animation preview exposed a separate per-row visible-bounds clip that cropped transformed drag images. Removing that individual clip preserves full-height dragged tabs; the owner accepted the correction.

While an Older tab targets the regular stack, its former chronological slot consumes no height. Date headings follow only tabs still targeting Older, so an empty bucket disappears and a shared bucket retains its heading. Returning to Older restores chronological placement. Keep and aging behavior are unchanged.

Both architecture builds and isolated UI/Settings/browsing/persistence smoke pass; Intel executes under Rosetta. The new Views regression covers a viewport taller than content, animation clipping, drag-start clip removal and a drop into regular tabs. Its translation unit compiles for both architectures; the full Chromium unit-test executable was not linked or run. Native visual and drag acceptance comes from physical Apple silicon owner review. Existing coordinator behavior supplies reduced-motion and reversal handling without a new independent runtime matrix.

Five-file quilt/export/replay has zero fuzz, zero offsets and exact source parity against inventory-verified preimages. The [completion record](../builds/2026-11-13-older-tabs-disclosure.json) retains identities, phase timings, checks and cleanup. The adopted arrangement source/output cache is reused and retained, with workspace ownership recorded beside it. No specific open GitHub issue tracks this fix. No release or deployment was performed.

## Fixed entry-based retention — November 13, 2026

At the owner's request, activation and trusted page input no longer extend an Older tab's close clock. Retention uses elapsed time since entry to Older Tabs. Last-use history still updates, while the frozen date bucket and current Older placement stay fixed. Settings now says **Close Older Tabs after**. Regular inactivity, Keep, deliberate drag-out and recently-closed recovery retain their existing semantics.

Existing close protections remain: a selected or visible Older tab is not closed while being viewed. If its deadline passes, it becomes eligible once those protections clear. Existing profile data keeps its saved close baseline; earlier versions could overwrite the original entry time on interaction, so that original time cannot be reconstructed reliably. Fresh Older transitions record the actual entry time.

Signed platform input `inputs/older-tabs-entry-clock-3/macos` at `6712c22a87c728c19d7cb43dc7c794906cbe3ea3` selects the change for future main builds. Both architecture builds, native/Rosetta production-method checks, compiled model regressions, real browser trusted pointer/key/scroll input and restart/deadline/active-protection/recovery checks, Settings and browsing/profile-persistence smoke pass. The old published browser fails the clock-preservation regression. Exact three-file replay against verified preimages has zero fuzz/offsets and final source parity. The complete Chromium unit-test executable and a new full source preparation were not run. The [completion record](../builds/2026-11-13-older-tabs-entry-clock.json) records identities, timings and validation scope. Published 26.1113.1 remains unchanged; no specific open GitHub issue tracks this request.
