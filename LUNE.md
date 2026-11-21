# Lune macOS component

This branch preserves helium-macos ancestry and pins Helium core from the same
Lune Git repository. Start builds with `scripts/lune.py` on Lune's `main` branch;
it selects exact inputs, checks disk/tooling, and separates preparation, compile,
and signing. Do not use the inherited `build.sh` as the Lune release interface.

Initial distribution changes:

- Lune application name and `computer.lune.browser` bundle/profile identity.
- Separate `Lune Storage Key` Keychain entry and Apple team `RBC9EP7948`.
- Service origin `https://services.lune.computer` (not deployed yet).
- Lune display strings using upstream's GRIT-aware substitution utilities.
- Strict patch application and a single hash-pinned downloads configuration.
- Automatic updates remain disabled until release/update validation is complete.

The first candidate remains a development baseline. Some upstream visual assets,
onboarding, attribution, and help links still require a complete branding and
endpoint audit before public distribution. Chromium's `helium://` compatibility
scheme, preference names, and internal C++ identifiers are intentionally retained.
