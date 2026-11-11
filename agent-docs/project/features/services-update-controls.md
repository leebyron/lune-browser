# Helium services notice and update controls

Owner accepted the footer, settings and setup changes on November 11, 2026, including real hover dismissal. The feature is included in future main builds through signed platform input `inputs/services-update-controls-1/macos` at `e61221ca25e8fed639477c667eb8b42115836cd9`. Published releases retain their frozen inputs.

## Behavior

The Helium services schema notice uses a sidebar footer row between the restart-to-update and default-browser rows. It uses the original Helium logo, the existing localized “Services updated” label, and the shared tab-style hover surface and close control. Clicking the row opens `chrome://settings/privacy/services`. The header app-menu button no longer highlights service changes. The existing review command remains in the app menu while a notice is pending.

Closing the row persists the dismissed schema version for that profile and updates other windows immediately. Dismissal does not acknowledge the service changes or grant component-update access. The settings changelog remains available until explicitly acknowledged, and a newer schema version can notify again. Horizontal mode retains the app-menu review command; the dedicated footer belongs to vertical mode.

Settings separates “Allow automatic browser updates” from “Allow automatic Helium services updates.” Browser updates retain their independent preference and appear directly on the Privacy and security page, outside Helium services, as the last row. The Helium services update toggle sits directly below “Allow connecting to Helium services”; it collapses away with the other service controls when that parent setting is off. Its value is retained while hidden. The “Updates to Helium services” changelog follows this toggle inside the same collapsed group, with explicit Got it acceptance text.

The new `helium.services.component_updates` preference controls the existing Helium component updater. Browser update access continues to depend only on `helium.services.browser_updates`. Component update access requires its new preference, service consent, services enabled, and schema acceptance. Existing profiles copy the former combined choice once; subsequent browser changes and relaunches cannot overwrite the independent component choice. Fresh profiles retain the existing defaults and consent gates.

Use defaults explicitly enables Helium component updates, independently of the browser-update checkbox. Custom setup presents a separate services update switch directly below the services connection switch. It starts on for new profiles and is disabled while services are off; an explicit off choice survives toggling services off and on. Existing profile choices remain intact in custom setup.

The Helium services entry restores the upstream description and original Helium logo. The services page restores upstream connection wording, keeps its existing individual controls, and contains no browser-update references. The services changelog explains component updates and follows their toggle; browser-update copy lives on the parent page. The new source messages are English; translation remains follow-up work.

## Implementation and validation boundary

The reusable platform patch is `patches/helium/ui/services-update-footer.patch`, developed with quilt in `.work/search-suggestions/platform/build/src` and exported into `.work/services-ui/platform` on `topic/services-update-footer` at signed commit `e61221ca25e8fed639477c667eb8b42115836cd9`, based on accepted platform input `51faf29296a2287b0b390a3d077606ebb08e6ae6`. Core gitlink is unchanged. The shared prepared tree also contains the separate Command-T candidate; the build boundary is pinned by `.work/services-ui/source-composition.json`. Independent zero-fuzz replay reproduces all 24 services source files without the separate command candidate.

`scripts/check-services-update-controls.py` compiles the production preference gates and migration with isolated preference storage. It tests all combinations of the two update preferences, service enablement, consent, and schema acceptance; versioned dismissal; and migration preserving both old values across later changes. Both architecture checks pass; Intel execution uses Rosetta.

Evidence is retained in `.work/services-ui/`:

- Patch lint and zero-fuzz patch/input replay pass. Svelte and TypeScript checks report zero errors and warnings.
- The accepted development lock validates ancestry, permanent tags, tree hashes, patch order/hashes and the unchanged core gitlink. Locked component patch/translation checks and all 66 repository tests pass (`lock-validation-integrated.log`, `component-inputs-integrated.log`, `repository-tests-integrated.log`).
- The final arm64 and x86_64 builds, standard UI/icon/settings smoke, independent update-control matrix/persistence checks, and complete custom/default onboarding flows pass. Intel runtime uses Rosetta on the Apple silicon host. Setup proves the Helium update choice starts on, can be disabled independently, preserves that choice, and is enabled by Use defaults even when browser updates are off.
- Native Preview 2 confirms the browser control is the last Privacy and security row, the original Helium entry artwork/copy, footer navigation, and collapse of both the services update control and changelog. The owner confirmed the real hover X appears and clears the row in the preceding preview; the footer implementation is unchanged. Persisted preferences show dismissed schema 1 with accepted schema still 0, so dismissal did not grant update access.
- Focused sidebar-footer and toolbar header dependency checks pass. The wider prefs/settings audit reports pre-existing missing dependencies for `helium_crash_reporting.h` and `brave_full_disk_access_confirm_dialog_delegate.h`; those omissions are also present before this patch. They are not new includes from this change.

The final build logs are `build-onboarding-final-arm64.log` and `build-onboarding-final-x86_64.log` (8m07s and 8m38s). Final runtime reports are `settings-complete-ARCH.json`, `setup-final-ARCH/report.json`, `smoke-complete-arm64.json` and `smoke-final-retry-x86_64.json`. The initial concurrent Intel smoke run timed out on local navigation; its standalone rerun passed without source or test changes. The earlier failure is retained in `smoke-complete-x86_64.json`. Native Intel hardware and macOS 13 behavior are not newly verified. No browser release, update feed, or frozen release record is changed.
