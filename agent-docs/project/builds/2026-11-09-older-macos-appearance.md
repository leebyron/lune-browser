# Older macOS appearance fixes — November 9, 2026

Status: included in the default development lock for both architectures.
No replacement public binary or feed promotion is included.

## Source

The appearance-only platform branch `topic/older-macos-appearance` starts at
released input `1cabd52145c9dc2ef1b3459c71b0133a81b6c4b4` and retains its core gitlink.
Two signed, single-thesis commits:

- `e5178412`: adaptive physical-pixel edges and 5% shadows for fallback header
  controls and Command-T. Shadows retain the existing 10 pt blur and 3 pt offset.
- `bd3ea4cf`: restore the inherited 12 pt content radius before macOS 26; preserve
  AppKit's older native frame and the accepted 16 pt modern frame.

The permanent input is `inputs/older-macos-appearance-1/macos`. The default
build lock and patch provenance pin its full commit, tree, and patch hashes.
New release preparation reads that lock; historical frozen releases remain
reproducible from their original records. Preserve these patches in future
upstream compositions.

These commits do not include the separate default-browser prompt investigation.
The owner authorized committing and pushing these appearance fixes on November 9.

## Validation

Both architecture builds and browser smoke checks passed with these appearance
fixes in the initial three-patch compatibility candidate. That candidate also
included the independent first-launch prompt change. Intel runtime validation
used Rosetta. The appearance-only branch has not had a separate full build.

The production-source fallback fixture passes on arm64 and x86_64: rasterized
hairlines in Aqua, Dark Aqua, and both high-contrast schemes; input pass-through;
content bounds; resize tracking; 5%/10 pt/3 pt shadows; and both radius branches.
The existing native chrome fixture also passes on both architectures, including
modern glass and Command-T. Host: macOS 26.6.2, Xcode 27.2/27B52, SDK 27.2.
Fallback branches are selected in the isolated fixture, not in production code.
Strict replay against released source baselines passes without fuzz or offsets
and matches the prepared appearance source bytes.

The default-input update passes all 65 orchestrator tests, lock validation with
ancestry/tag/tree/gitlink and ordered patch-hash checks, and documentation link
and whitespace checks. The Actions audit confirms only the three reviewed local
workflows are active. A fresh recursive GitHub checkout reconstructs the exact
platform/core input and passes both patch-series lints and translation lint.

Native macOS 13 visual acceptance remains pending. The 12 pt fallback comes from
Helium; it is not an Apple API guarantee or a measurement of every older OS.
These checks do not reproduce the older compositor. macOS 14/15 and native Intel
execution of the fixes remain unverified. No new signed/notarized distribution
has been produced for these commits.

See [source findings and implementation](../features/older-macos-appearance.md).
