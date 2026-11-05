# Lune macOS component

This branch is Lune's platform fork of helium-macos. Preserve upstream history,
licenses, and attribution. The `helium-chromium` gitlink pins the imported core.
Keep Lune distribution changes in separate commits from reusable features.

Read the orchestrator's `AGENTS.md` and `agent-docs/project/` at
https://github.com/leebyron/lune-browser/tree/main before changing build policy.
Do not submit issues, PRs, or messages to upstream repositories automatically.

Use exact locked source archives and `--no-fuzz` for patch application. Stop on
conflicts. Never automatically reset an existing source/build directory.
Browser build and signing are separate operations. No release is authorized by
a successful compilation alone. Do not publish until both architectures and the
installed update path have passed the release gates.
