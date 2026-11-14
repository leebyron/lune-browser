# Feature and bug-fix development loop

This is the default workflow for browser feature and bug-fix tasks, adopted from [issue #36](https://github.com/leebyron/lune-browser/issues/36). Use the [build runbook](building.md) for toolchain, source preparation and locked-input commands, and the [completion process](committing.md) for adoption and cleanup.

## Validation stages

| Stage | Required work |
| --- | --- |
| Edit → preview → feedback | Reuse the prepared source and incremental arm64 output. Run checks relevant to the edit and inspect the native behavior. Repeat this short loop until accepted. |
| Accepted → main | Refresh/export the focused quilt patch, verify strict replay and source parity, then pass both architecture builds, relevant regressions and browsing/profile-persistence smoke on the final candidate. Run broader integration checks once the composition settles. Publish exact component inputs, lock and provenance using the completion process. |
| Release | Use a fresh source preparation and paired production builds, then all existing signing, notarization, runtime, installed-update, freshness and publication gates in [release delivery](release-delivery.md). |

Intel belongs earlier when the bug or edit concerns architecture-specific code, compiler/ABI behavior, dependencies or cross-compilation. Intel runtime under Rosetta is recorded as Rosetta; physical Intel remains optional follow-up under current policy. Native visual acceptance is on the physical review device.

A changed final composition must be revalidated. Reuse an existing final build/check result only when its relevant source, configuration, toolchain and tested artifact identities still match; a passing earlier preview alone is insufficient. Stop on conflicts or failed validation. This policy does not bypass locked-workspace guards or authorize editing a frozen release workspace.

## Choose checks from the change

- **Sidebar/native layout or interaction:** compile arm64, run the affected native/model regression if available, and inspect the actual gesture, focus or layout. A spacing revision does not need unrelated onboarding, translation, credits or artwork checks before native review.
- **Onboarding, Settings, strings or artwork:** run the relevant frontend/resource checks and preview that surface. Include native integration when the edit crosses into browser behavior or packaging.
- **Shared infrastructure, engine, dependencies or build configuration:** widen validation early to cover affected targets and both architectures where relevant.
- **Documentation or tooling:** check links, consistency, whitespace and the actual tool behavior. A Chromium build adds no evidence for unchanged browser code.

Keep cheap relevant regressions in the immediate loop. Run the existing broad locked-input checks for final browser integration, including resource/onboarding checks and UI/Settings/attribution smoke where applicable; release coverage remains unchanged. Record the reason for omitted or deferred checks. If later edits affect a previous result's inputs, rerun that check. Do not rerun unrelated successful checks solely because the preview has a new name.

## Preserve and coordinate incremental work

Before using a prepared tree, read its preparation/input records and any active task record. Keep one coordination record next to the source tree, outside generated Chromium sources, for example `.work/<workspace>/development-workspace.json`:

```json
{
  "owner": "<active task or chat identifier>",
  "task": "<issue URL and short purpose>",
  "source": "<absolute prepared Chromium path>",
  "base_core_commit": "<full commit ID>",
  "base_platform_commit": "<full commit ID>",
  "chromium_version": "<exact version>",
  "outputs": {"arm64": "<output path>", "x86_64": "<output path, if present>"},
  "active_patches": ["<ordered active quilt patches, including pending work>"],
  "command_in_progress": null
}
```

This record coordinates work; it is not an automatic lock or proof of source parity. The owner serializes source/quilt mutations, GN changes, fixtures that alter the build graph, and builds in that tree. Record the current operation before starting and clear it after exit. Another task must coordinate with the owner or use a separate prepared workspace. Do not edit sources while compilation runs or consume an output while it is being replaced.

Update the record after a reviewed input/patch change or handoff. Keep pending work explicit and out of unrelated focused exports. A record does not make an incompatible prepared tree reusable: preserve the lock, GN and toolchain guards in the build runbook.

Retain prepared sources, incremental outputs, downloads and compiler caches across revisions and after completion. Clean up task-owned disposable app copies, profiles and fixture processes under the completion policy. Do not delete or reprepare a reusable tree to start another small edit. Inspect stale ownership, active processes and unpublished changes before any handoff or cleanup.

## Measure the feedback loop

Use [scripts/time-development.py](../../scripts/time-development.py) to append command timings to an ignored JSONL report. Give each preview revision an iteration name and record build, fixture setup, preview readiness, checks and export separately. The tool runs the exact argument vector without a shell, preserves command output, records failures and returns the command's exit status. It inherits the caller's environment; build commands must still use the project's clean build environment.

```sh
python3 scripts/time-development.py --report .work/<task>/timings.jsonl \
  --iteration preview-1 --phase build --arch arm64 -- \
  python3 scripts/lune.py build --arch arm64 --jobs 10

python3 scripts/time-development.py --report .work/<task>/timings.jsonl \
  --iteration preview-1 --phase checks --arch arm64 -- \
  python3 scripts/check-native-focus-retention.py <prepared-source> --arch arm64
```

Use the existing reviewed incremental build command for a feature workspace when appropriate; the locked-input wrapper above remains subject to its normal guards. The timer does not select build targets, launch a browser or manage profiles. Use phases `compile` and `link` when those steps are independently measurable. Otherwise use `build` for their combined duration and retain the underlying build log; do not invent a split. Other phases are `fixture`, `preview`, `checks`, `export` and `edit-to-preview`.

For `preview`, time a command/probe that returns when the correct binary and scenario are ready for inspection. Timing only `open` measures a launch request; waiting for the entire browser session measures review time instead. Label either limitation explicitly. Record edit-start and preview-ready timestamps in the task evidence for the total feedback interval, including gaps between commands; phase sums alone do not measure that interval. A timed driver that performs the whole loop may use `edit-to-preview`.

Keep timings bound to the workspace record, relevant source/patch hashes and binary identity in the task's validation evidence. Compare like-for-like edits and cache state, and report one-time preparation separately. Retain failed attempts rather than counting only successful commands.

The first sidebar and native-editor tasks using this workflow should retain real before/after measurements. Existing compile-only references are [pinned groups](builds/2026-11-12-pinned-tab-groups.json) (arm64 253.85 s, Intel 285.56 s) and the [separator](builds/2026-11-13-expanded-group-separator.json) (135.24 s and 162.39 s). Removing Intel from those recorded pairs would save about half the compilation time; this is a counterfactual estimate, not an observed edit-to-preview speedup. Real comparative feedback-loop baselines remain pending in #36.

Component builds, a unified preview command, automated quilt/export/check-result reuse and compiler/job tuning remain deferred experiments in #36. The current GN configuration, CI coverage and release gates are unchanged.
