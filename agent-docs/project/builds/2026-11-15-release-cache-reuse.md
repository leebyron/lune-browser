# Release cache relocation — November 15, 2026

The 26.1115.1 build reused output files and imported Siso file state, but the earlier transfer left absolute compiler-resource dependencies in `.siso_deps` pointing to a retired preparation workspace. Its missing `stddef.h` and `limits.h` dependencies invalidated 42,940 arm64 and 73,501 Intel actions. The copied objects' existence and compiler cache capacity could not prevent that invalidation. Matching compiler, GN, Siso, Rust and PGO hashes ruled out a necessary toolchain rebuild as the main cause.

## Implemented tooling

Fresh release preparation accepts paired `--cache-source` / `--cache-report` options. An already prepared tree can use `scripts/release/cache_reuse.py`. It compares source contents, preserves timestamps only for identical files, checks symlinks and pinned tools, snapshots idle donor outputs, relocates native Siso file state, and rewrites the separate Ninja v4 dependency log. Equivalent dependency nodes merge without losing dependency lists or timestamps. Legacy Clang resource-header paths require cached digest proof against the fresh inventory. Unknown absolute dependencies, corrupt logs, hidden content changes with identical cached timestamps, existing destination outputs and incomplete transfers fail closed. Donors are preserved, and the outer app is assembled again.

The donor's native Siso lock is held during transfer and its metadata fingerprints must remain unchanged. The pinned Siso v1.6.7 uses `flock` for real builds; a native probe confirmed that it waits on the transfer lock. Dry runs do not acquire that lock, so the earlier dry-run lock probe was inconclusive. The [pinned implementation](https://chromium.googlesource.com/build/+/siso/v1.6.7/siso/sync/lockfile/lock_unix.go) and the retained real-build probe establish the locking behavior.

Before compilation, release builds run a native Siso dry run and retain its explanation. A reversible fault injected into the task-owned cache reproduced the missing-header failure: the new guard rejected it before compilation. Original metadata was restored and its fingerprints verified. The dry run is a dependency check, not a complete prediction of later work; regenerated files can schedule additional downstream actions.

## Measured validation

The comparison uses frozen 26.1115.1 source and recipe `04f86332a4e3e40f3730b7e73f5867c4b6b95bbc`, with the same 596,091 source files and 141 symlinks. The benchmark used an isolated source snapshot and healthy released output caches. Both source inventories passed before and after compilation. It did not allocate, sign or publish another release.

| Architecture | Affected release build | Repaired-cache build | Build actions | C++ recompiles in benchmark |
| --- | --- | --- | --- | --- |
| arm64 | 2h 4m 49.52s | 3m 12.65s | 48,918 → 145 | 6 |
| x86_64 | 3h 9m 10.83s | 3m 13.50s | 83,122 → 163 | 10 |

These are native Siso execution times. Complete benchmark build commands, including initial source/toolchain checks and final source verification, took 378.45s and 382.04s. Paired source comparison, output snapshots and metadata relocation took another 245.77s; that trial timer excludes the initial fresh-source inventory and source clone. The final tool includes verification in its transfer timer, and preparation reuses its just-completed inventory to avoid a duplicate scan. Fresh archive preparation, signing, notarization and update acceptance are separate costs.

Moving to a source tree at a different directory depth changed relative paths to Xcode's `gperf`; onboarding and extension generators also contain absolute workspace paths. Those command changes explain the small remaining regeneration, recompilation and linking cost. The fix does not alter GN commands, enable unsafe compiler-cache path normalization, or bypass dependencies. Real source, engine, PGO, compiler and configuration changes can still require extensive work.

All 106 tooling tests pass, including pinned Ninja 1.12.1 / Chromium Clang interoperability: unchanged relocated output is reused byte-for-byte, a changed header in the new tree rebuilds to the correct executable while the donor remains unchanged, and removing the fixture donor does not trigger a rebuild. Paired browser smoke tests pass for browsing, persistence, UI defaults, Settings and packaged artwork. Intel executes under Rosetta. Original donor metadata remains unchanged. Test fixtures and profiles are cleaned up; reusable sources, outputs and concise evidence remain.

Exact timings, hashes and outcomes are in the [machine-readable record](2026-11-15-release-cache-reuse.json). Raw task evidence and reusable outputs are retained under `.work/cache-reuse-investigation/`. The published 26.1115.1 inputs and artifacts remain unchanged.
