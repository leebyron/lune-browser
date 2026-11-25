# Browser development loop

Use the [build runbook](building.md) for setup and exact commands and the [completion process](committing.md) for adoption.

| Stage | Work |
| --- | --- |
| Preview | Reuse the prepared tree and incremental arm64 outputs. Run the affected regression and inspect the actual native gesture, focus or layout for UI work. Use frontend and resource checks for setup, Settings, strings and artwork. Bring Intel forward for ABI, dependency or cross-compilation work. |
| Adopt on main | Refresh and unmerge the focused quilt changes. Run full zero-fuzz preparation against locked archives in isolation, then compare affected files and generated resources with the accepted preview. Build and smoke-test both architectures and run focused regressions and applicable integration checks against the settled composition. Record Intel-under-Rosetta execution accurately. |
| Release | Follow the separate [release preparation and acceptance gates](release-delivery.md). |

Patches apply before substitutions, localization and resource generation. Verify provider and attribution text through both name-substitution passes when affected. Compare the accepted preview against pipeline output at adoption.

Reuse checks when the relevant source, config, toolchain and artifact identities match. Track which checks apply to the final candidate in one task evidence location. Rerun checks affected by edits and keep broader unchanged checks for the settled composition. Use tooling tests and link, consistency and whitespace checks for documentation and tooling changes.

Keep normal site navigation available in previews handed to reviewers, including when the preview also loads a local test fixture. Automated smoke runs can still use an isolated profile with restricted DNS.

## Preview setup without rebuilding Lune

Run the actual Svelte setup project from an existing prepared Chromium tree. Use
the tree's bundled Node or Node 22.18 or newer. The prepared tree supplies the
frontend dependencies. A standalone copy lets you edit while the donor tree stays
available for other work.

```sh
node scripts/preview-setup.mjs /path/to/prepared/chromium/src \
  --copy-to .work/setup-preview
```

Open `http://127.0.0.1:5173/` in a browser that is already installed. Edit `src/`,
`public/`, or `helium_onboarding_strings.grdp` in the working copy. Vite updates
components and styles in place and reloads for artwork and regenerated strings.
The current step stays in the URL across full reloads, which start with the
scenario's original mock preferences. Stop the server with Control-C. Resume by
passing `.work/setup-preview` as the source. You can also pass a prepared tree
you own directly and skip the copy. Use `--port` to run another preview alongside it.

Use `?step=Finish` to open Customize Lune directly. The step names are `Welcome`,
`SearchEngine`, `Privacy`, `HeliumServices`, `DataImport`, `PasswordManager`, and
`Finish`. Add `&scenario=import-empty` or another scenario to the same URL.

| Scenario | How to reproduce |
| --- | --- |
| `fresh` (default) | Walk through setup with simulated search engines, preferences, browser profiles, and extension installs. |
| `services-off` | Open PasswordManager to see the one-time download notice. |
| `import-empty` | Open DataImport and click Import to see an empty result. |
| `import-error` | Open DataImport and click Import to see a discovery error and retry. |
| `import-failure` | Open DataImport, discover and select a profile, then click Next to exercise a failed import response. |
| `extension-error` | Open PasswordManager and click Install on an available manager. |

Use browser DevTools for narrow viewports, light and dark color schemes, and reduced
motion. The loopback preview uses the mock browser bridge. Check native appearance,
safe-area insets, import permissions, localized strings and browser-side side effects
in packaged `chrome://setup/`. When ready to adopt edits from a standalone copy,
apply them in the owning prepared tree with quilt and follow the usual validation
and adoption steps. See [onboarding](features/onboarding.md) for the packaged flow.
The [preview validation record](builds/2026-11-24-setup-preview.json) includes
save-to-preview timings and the scenarios exercised in Lune.

## Coordinate shared workspaces

Reuse sources, outputs, download and compiler caches. Before editing or building, inspect the preparation report and ownership. Keep one ignored coordination record next to the tree, such as `.work/<workspace>/development-workspace.json`, with the owner/task, source and output paths, exact core/platform inputs and engine version, active patch order and current operation.

Serialize source/quilt/GN changes and builds in a shared tree. Coordinate with its owner or use an isolated workspace. Keep pending patches out of unrelated exports. Follow the [completion process](committing.md#quit-temporary-builds-and-remove-their-artifacts) for workspace cleanup.

## Measure the feedback loop

Append timings to an ignored JSONL with [time-development.py](../../scripts/time-development.py). Use the actual build/check command and clean build environment.

```sh
python3 scripts/time-development.py --report .work/<task>/timings.jsonl \
  --iteration preview-1 --phase build --arch arm64 -- \
  python3 scripts/lune.py build --arch arm64 --jobs 10
```

Use `compile` and `link` only when measured independently. Record fixture, preview readiness, checks and export separately when useful. Measure edit-to-preview from edit start until the correct app and scenario are ready, including gaps between commands. Bind outcomes and timings to the input and binary identities. Compare matched edits and cache state, with one-time preparation reported separately.

[Issue #36](https://github.com/leebyron/lune-browser/issues/36) tracks comparative feedback-loop baselines. [Pinned groups](builds/2026-11-12-pinned-tab-groups.json) and [expanded group separation](builds/2026-11-13-expanded-group-separator.json) provide compile-only references.
