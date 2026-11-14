# Preferred setup defaults

Owner-accepted November 14, 2026 through `inputs/setup-defaults-1/macos` at `d819cd5a5adf9ed6ceb162b1edb063c6e3861ef4`. Selected for future main builds; published 26.1113.1 is unchanged.

Custom Setup starts with the preferred selections used by Use defaults. Following every Next without edits produces the same preferences as Use defaults; importing data and installing a password manager still require separate choices. The existing service consent boundary remains at Next. Search suggestions appear selected for fresh profiles without changing the backing preference until Next or an explicit toggle. User choices, policy values and completed profiles retain their existing values. Back, reload and browser restart preserve opt-outs.

Setting descriptions are 14px and page subtitles 16px, both 2px smaller than before. Their color mixes 70% secondary foreground with 30% setup background; headings and controls retain their colors and opacity. The footer fade begins 12px above the buttons, reaches solid background at their lower edge, and extends behind the dots to the true bottom of the viewport. Scroll clearance keeps final content above the fade at scroll end.

Welcome omits the extra Defaults include line. Its footer explains that Setup reviews and changes the defaults; the services description explains that Next confirms those settings. Lune-specific copy remains in a separate patch and commit.

## Validation

Both architecture builds, packaged onboarding/footer checks, defaults parity and opt-out restart regressions, and browsing/Settings/profile-persistence smoke pass. Intel runtime uses Rosetta. All six source files replay without fuzz or offsets and exactly match the final prepared source. Svelte and TypeScript checks, inherited patch/translation lint and 78 repository tests pass. The [completion record](../builds/2026-11-14-setup-preferred-defaults.json) binds results to source and artifact identities.

The owner reviewed settled screenshots of every setup page and explicitly waived another visual review after selecting 70% description foreground. Preference-boundary checks do not claim a fresh network audit. Fresh full source preparation, native Intel, macOS 13 runtime and broader accessibility review were not performed for this change.

[Issue #35](https://github.com/leebyron/lune-browser/issues/35) stays open for service explanations and hidden inactive options, guided import and privacy work. Privacy remains last. Temporary previews and test profiles are closed and removed after evidence retention; shared prepared source and incremental outputs remain available.
