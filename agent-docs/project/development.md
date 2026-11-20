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
