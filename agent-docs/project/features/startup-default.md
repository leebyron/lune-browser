# Startup default

Lune defaults Settings > On startup to **Continue where you left off** on macOS.
The registered `session.restore_on_startup` default is `LAST` (integer `1`),
using Chromium's existing session restore behavior. Saved startup selections
and managed preferences retain their precedence; guest sessions retain their
existing behavior. Profiles with no saved selection inherit this default.

The platform input `inputs/continue-session-default-2/macos` contains signed commit `bc7e8558d217c37ee41168ff2c0744a0a2e7183b`,
based on `inputs/floating-infobars-1/macos`, with the core input unchanged.
The existing older-macOS, Dock-prompt, downloads, and footer-prompt patches
are preserved byte for byte. Both architectures and new release preparation
inherit this default from the main development lock.
`patches/lune/continue-session-default.patch` changes the macOS default branch
and updates Chromium's existing `DefaultStartupType` unit-test expectation.
The development lock includes this input. The frozen `26.1109.1` release record
and its binaries are unchanged.

Validation on November 9, 2026:

- All 65 main-branch repository tests pass.
- Lock validation verifies ancestry, permanent refs, tree hashes, patch hashes,
  series order, and the unchanged core gitlink.
- Platform patch lint and patch-aware whitespace checks pass.
- The patch replays with zero fuzz and zero offsets against the prepared
  Chromium 158 source; both resulting files match the quilt source exactly.
- The implementation and existing unit-test translation units compile for
  arm64 and x86_64 with the prepared Chromium build flags. Compilation outputs
  are isolated from the browser build.

No full browser rebuild or linked unit-test execution was performed for this
preference-default change. Runtime session restoration has not been revalidated
with this input, and the change has not been published in a browser release.
