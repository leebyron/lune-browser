# Lune project definition

This directory contains project context and working guidance written by and for
agents. It is not the browser's user documentation.

A browser built from spare parts. Used by [@leebyron](https://leebyron.com);
you can use it too.

Lune combines ungoogled-chromium's foundation, Helium's browser work, selected
unmerged contributions, and features developed here. Arc is an interaction-design
reference. Lune is an independent distribution with its own identity and services.

## Goals

1. Target the latest stable Chromium, independently of Helium and Xelium release
   cadence. Never downgrade Chromium to accommodate optional UI patches. Discover
   new stable Chromium and ungoogled-chromium releases daily and attempt integration
   with the matching Chromium source and a compatible Helium patch/configuration
   stack, without waiting indefinitely for a Helium binary release.
2. Support an explicit selection of Helium functionality and open upstream PRs.
   Begin with the complete Helium stack; selective exclusions need dependency
   analysis and validation.
3. Develop browser features as small changes suitable for contribution to Helium.
   Distribution identity and infrastructure remain separate from those features.
4. Prefer native Git operations for history, integration, and contribution.
5. Produce automated macOS releases for **Apple silicon (arm64) and Intel
   (x86_64)**, up to daily when inputs change and all gates pass.
6. Use Xelium's release approach: Apple signing and notarization, DMGs, GitHub
   Releases, and Sparkle 2 updates under Lune's identity.
7. Operate our own Helium services and website under `lune.computer`.
8. Keep project coordination in one repository where practical.

## Success criteria

- A release can be reconstructed from its recorded source and toolchain inputs;
  bit-for-bit reproducible binaries are a separate, unproven goal.
- A new upstream release can reach users without manual intervention when
  integration, both builds, runtime checks, and update verification succeed.
- Conflicts and failures produce actionable diagnostics and leave the last good
  release usable. The project reports upstream version lag rather than hiding it.
- Both architectures can install, launch, browse, persist a profile, and update
  from the previous Lune release without touching an existing Helium profile.
- A Lune feature can be isolated onto an upstream-based branch without branding,
  unrelated PRs, or release infrastructure mixed into the diff.

If ungoogled-chromium or Helium lags Chromium stable, report the gap explicitly
and forward-port the required patch stack. An older development candidate is not
a current-security release. Compatibility conflicts block that candidate; they
never silently pin the project to an older Chromium.

Daily polling reduces avoidable delay; it cannot promise the latest security
fixes at all times. Chromium, ungoogled-chromium, Helium compatibility, build
capacity, and failed validation can each introduce lag. Track Chromium stable
announcements as well as the latest ungoogled-chromium release.

## Scope and status

The initial target is macOS on both architectures, confirmed by the owner.
Windows and Linux are future platform adapters, not first-release requirements.
The full Helium stack plus selected Xelium UI patches and Helium PRs #2747, #2367,
and #2539 are recorded in the [UI integration notes](xelium-ui.md). The candidate
is under development validation and remains behind Chromium stable 158. Keep CI free: this Mac is the first build host, with
a registered GitHub Actions self-hosted runner and a manual development workflow. The services host remains
undecided. Signing identities are provisioned locally.

As of 2026-11-05 the documentation and minimal Cloudflare website are bootstrapped.
The owner registered `lune.computer` at DNSimple. See the
[website runbook](website.md) for deployment and domain activation status.
Component histories, exact inputs, local build tooling, and configuration CI are
bootstrapped; see [building](building.md). The first arm64 browser build and
headless smoke test passed; see [the evidence](builds/2026-11-05-arm64.md).
No public browser release, deployed browser services, or recurring browser schedule exists yet.

## Read next

- [Architecture](architecture.md): repository histories, patch selection, Git flow.
- [Releases](releases.md): daily integration, signing, publication, update gates.
- [Services](services.md): self-hosting and website boundaries.
- [Roadmap](roadmap.md): implementation sequence and acceptance checks.
- [Research](research.md): current upstream evidence and limitations.
