# Lune project definition

This directory contains project context and working guidance written by and for
agents. It is not the browser's user documentation.

A browser built from spare parts. Used by [@leebyron](https://leebyron.com);
you can use it too.

Lune combines ungoogled-chromium's foundation, Helium's browser work, selected
unmerged contributions, and features developed here. Arc is an interaction-design
reference. Lune is an independent distribution with its own identity. Optional browser services currently use Helium; browser updates use Lune’s GitHub releases.

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
7. Operate the website under `lune.computer`; retain Helium-hosted browser services unless a separately validated self-hosted deployment is requested.
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

Every public release and feed/website promotion rechecks the latest macOS stable
Chromium. Known lag requires an explicit, recorded owner exception for that
release; failed lookups leave freshness unknown and block promotion. See the
[release freshness gate](releases.md#chromium-freshness-gate). An exception does
not make an older browser current or waive other release checks.

Daily polling reduces avoidable delay; it cannot promise the latest security
fixes at all times. Chromium, ungoogled-chromium, Helium compatibility, build
capacity, and failed validation can each introduce lag. Track Chromium stable
announcements as well as the latest ungoogled-chromium release.

## Scope and status

Lune's original code, tooling, documentation, and original assets use GNU GPLv3 or later
(`GPL-3.0-or-later`), except where otherwise noted. See the root [LICENSE](../../LICENSE)
and [NOTICE](../../NOTICE). Helium's [GPLv3 license](../../LICENSE.helium) and
ungoogled-chromium's [BSD 3-Clause license](../../LICENSE.ungoogled_chromium) apply
to their respective imported work. Preserve imported component and asset licenses and attribution.

The supported targets are macOS arm64 and x86_64, with macOS 13 as the current minimum. Windows and Linux are future platform adapters. Keep CI free using the local Mac runner. Signing and notarization credentials are provisioned in Keychain.

Read [current status](status.md) for published releases, active release preparation, selected engine inputs, hosting and validation limits. The [development lock](../../manifests/browser.lock.json) and [patch manifest](../../manifests/patches.json) are authoritative for composition. Feature and build reports are dated evidence rather than a second source of current inclusion state.

## Read next

- [Completion process](committing.md): validated commits, resolved issue closure, temporary-build shutdown and artifact cleanup.
- [Architecture](architecture.md): repository histories, patch selection, Git flow.
- [Release delivery](release-delivery.md): current commands and publication/update procedure.
- [Release policy](releases.md): freshness, validation gates and release-note style.
- [Release commits](release-commits.md): version rules, frozen inputs, provenance,
  preparation procedure and tooling migration.
- [Services](services.md): self-hosting and website boundaries.
- [Roadmap](roadmap.md): implementation sequence and acceptance checks.
- [Research](research.md): current upstream evidence and limitations.
