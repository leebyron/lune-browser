# Preferred setup defaults

Owner-accepted November 14, 2026 through `inputs/setup-defaults-1/macos` at `d819cd5a5adf9ed6ceb162b1edb063c6e3861ef4`. Selected for future main builds; published 26.1113.1 is unchanged.

Custom Setup starts with the preferred selections used by Use defaults. Following every Next without edits produces the same preferences as Use defaults; importing data and installing a password manager still require separate choices. The existing service consent boundary remains at Next. Search suggestions appear selected for fresh profiles without changing the backing preference until Next or an explicit toggle. User choices, policy values and completed profiles retain their existing values. Back, reload and browser restart preserve opt-outs.

Setting descriptions are 14px and page subtitles 16px, both 2px smaller than before. Their color mixes 70% secondary foreground with 30% setup background; headings and controls retain their colors and opacity. The footer fade begins 12px above the buttons, reaches solid background at their lower edge, and extends behind the dots to the true bottom of the viewport. Scroll clearance keeps final content above the fade at scroll end.

Welcome omits the extra Defaults include line. At this adoption its footer explained that Setup reviews and changes the defaults (removed by the subsequent Welcome refinement below); the services description explains that Next confirms those settings. Lune-specific copy remains in a separate patch and commit.

## Validation

Both architecture builds, packaged onboarding/footer checks, defaults parity and opt-out restart regressions, and browsing/Settings/profile-persistence smoke pass. Intel runtime uses Rosetta. All six source files replay without fuzz or offsets and exactly match the final prepared source. Svelte and TypeScript checks, inherited patch/translation lint and 78 repository tests pass. The [completion record](../builds/2026-11-14-setup-preferred-defaults.json) binds results to source and artifact identities.

The owner reviewed settled screenshots of every setup page and explicitly waived another visual review after selecting 70% description foreground. Preference-boundary checks do not claim a fresh network audit. Fresh full source preparation, native Intel, macOS 13 runtime and broader accessibility review were not performed for this change.

[Issue #35](https://github.com/leebyron/lune-browser/issues/35) stays open for service explanations and hidden inactive options, guided import and privacy work. Privacy remains last. Temporary previews and test profiles are closed and removed after evidence retention; shared prepared source and incremental outputs remain available.

## Welcome refinements — November 14, 2026

Owner accepted through `inputs/setup-welcome-1/macos` at `cefc2023103979f8d88267d5c8ac78972911f603`. Selected for future main builds; published 26.1114.1 is unchanged.

Use Defaults comes before Setup. The automatic-update switch follows “Update browser automatically.” The review-defaults footer sentence is removed, and the two remaining footer paragraphs sit directly above the progress dots. The credit reads “Built on Helium browser and ungoogled-chromium with thanks to their authors and contributors,” with links to both projects. Setup links use the browser-default underline offset and 50% underline opacity at rest, restoring full color on hover. Measured footer height reserves scroll clearance when credits wrap on small windows. Privacy copy and destinations await the separately planned privacy work.

Strict zero-fuzz/zero-offset replay reproduces all six source files. Both architecture builds and packaged onboarding, safe-area footer, defaults parity and browsing/Settings/profile-persistence checks pass; Intel runs under Rosetta. The accepted arm64 preview also verified exact copy, links, control order, actual pointer-hover styles and scroll clearance at 1100×800, 800×600 and 600×500. Frontend checks and 78 repository tests pass. The [completion record](../builds/2026-11-14-setup-welcome-refinements.json) retains source and artifact identities. No additional full source tree was created; the pending Older Tabs patch was excluded from this focused input.
