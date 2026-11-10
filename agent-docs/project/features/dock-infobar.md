# Dock-pinning message bar

The owner requested removal of the “Keep Lune in your Dock” message bar and
authorized committing, pushing, and including the change in future builds on
November 9, 2026.

The macOS `default_browser::ShouldOfferToPin()` now returns `false`. The
pin-infobar controller checks it before either the legacy or centralized
display path, covering the standard message and experimental wording variants.
Manual Dock pinning remains available through macOS.

The single-thesis platform commit is
`c4f0680e7b37bc5585624b357eba827da88d8647`, following the current older-macOS
appearance input `bd3ea4cf1b20539c1c862af1845efa073d545a30`.
The permanent input is `inputs/remove-dock-infobar-1/macos`. The development
lock and composed-patch manifest select it for both arm64 and x86_64 builds.
Existing frozen release records retain their original inputs.

## Validation

- Developed against prepared Chromium 158 source, refreshed with quilt, and
  unmerged into the platform repository.
- The new patch applies with zero fuzz and zero offsets and reproduces the
  edited source bytes. No other patch in the current platform series changes
  either affected source file.
- Platform patch inventory and inherited lint pass.
- The changed Objective-C++ translation unit compiles for arm64 and x86_64
  using the existing Chromium build commands and isolated object outputs.
- Full browser builds and live UI checks were not run for this change.
  Source inclusion does not mean the installed or published browser changed.

## Related message bars

Source inspection found that default-browser promotion already uses the sidebar
with vertical tabs, while horizontal tabs retain a bar fallback. The optional
centralized infobar migration can bypass that routing; it is disabled by default.
Session-restore messaging remains conditionally available, although its default
new-tab startup case does not produce a message. PDF-default promotion is already
disabled by Helium.

Theme Undo, hostname suggestions, reload notices, sharing, debugging, and security
warnings also use the shared infobar container. These were inventoried, not removed
or runtime-reproduced. Follow-up review should preserve sharing controls and
security/encryption warnings while assessing the presentation of routine prompts.
