# Repository and patch architecture

The public GitHub repository holds orchestration, manifests, policy, website and releases on `main`. Browser components retain their upstream histories on separate branches.

| History | Purpose |
| --- | --- |
| `component/helium` | Helium-derived core with ungoogled-chromium ancestry |
| `component/macos` | Helium macOS platform patches, tooling and core gitlink |
| `component/services` | Upstream service history for optional future hosting |
| `topic/<feature>` | Focused changes on the owning upstream base |
| `integration/<id>/<component>` | Reviewed composition pinned to exact inputs |

Keep the histories separate and use native Git operations. Namespace upstream tags. Retain exact component commits under permanent `inputs/*` refs. Detached checkout SHAs alone do not keep inputs reachable.

Use an isolated clone for the macOS component, preserving the upstream `helium-chromium` submodule layout. Pin the composed core via the platform gitlink and a reachable submodule URL. Publish core before platform and verify a fresh recursive clone. Keep build sources, outputs and caches in ignored workspaces.

## Two distinct kinds of patches

Git changes the configuration repositories. Quilt changes prepared Chromium sources. Develop in the prepared tree, refresh with quilt, run `he unmerge`, then commit the exported core/platform patches. Use Helium's upstream preparation for the full pipeline, including pruning, patching, substitutions, resources and localization. Helium already incorporates the ungoogled patch series.

## Integration sequence

1. Resolve latest official macOS Chromium Stable, downstream source and any selected PR refs to exact versions and commits. Keep the compatible ungoogled provenance and match its ancestry in Helium. If either project lags, forward-port the required patch/config stack in an isolated integration branch.
2. Apply reviewed PR commits in declared dependency order with `git cherry-pick -x`. Record repo/URL, PR base/head, explicit ordered commits, dependencies, review status, adaptations and patch hashes. Review changes to a pinned PR head. Before retiring an upstreamed downstream patch, verify the behavior is present after a squash or rebase.
3. Replay focused Lune topics and separate distribution changes. Inspect conflicts with the original intent and downstream dependency order. Stop on failed replay or validation. Record a reviewed adaptation in an attributable commit. Preserve Chromium freshness and optional feature behavior.
4. Pin the platform's exact core gitlink, update `manifests/browser.lock.json` and `manifests/patches.json`, and follow the [development adoption checks](development.md) before main adoption.

For a Chromium forward-port, `chromium_forward_port` in the browser lock requires `review_status: reviewed-port`, full `base_core_commit` and `chromium_commit` IDs, and a hashed review Markdown file under `agent-docs/project/builds/`. Validation checks ungoogled-to-base-to-integrated-core ancestry, original base version, final component commits/trees/tags and matching platform gitlink. Both host download manifests must pin the exact target Chromium archive. Remove the forward-port record once a matching upstream release is adopted.

Check [Helium's contribution guidance](https://github.com/imputnet/helium/blob/42da6c50c04f3b411879d5bdb1304f4d78ea9c81/CONTRIBUTING.md) against the current upstream before contributing. Nontrivial changes need maintainer agreement and upstream issue/PR descriptions are human-written. A GitHub fork in Helium's repository network may be required for submission.

See [release identity](release-commits.md) for frozen inputs and signed public tags. Keep service deployment independent of browser source and update delivery.
