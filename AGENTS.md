# Working on Lune

Lune is a macOS Chromium distribution assembled from ungoogled-chromium, Helium, selected upstream contributions and Lune patches. Browser features should remain independently upstreamable; distribution identity and release policy stay separate.

## Start here

1. Read [current status](agent-docs/project/status.md) and the [project definition](agent-docs/project/README.md).
2. Read [architecture](agent-docs/project/architecture.md) before changing repository structure or patch composition.
3. Use the task's runbook below. Treat dated feature/build records as historical evidence; the current lock and frozen release records determine inclusion.

| Task | Read |
| --- | --- |
| Prepare sources or compile | [Build runbook](agent-docs/project/building.md) |
| Freeze, sign, publish or verify updates | [Release delivery](agent-docs/project/release-delivery.md) |
| Release policy, freshness and notes | [Release policy](agent-docs/project/releases.md) |
| Version allocation and commit boundaries | [Release commits](agent-docs/project/release-commits.md) |
| Native UI changes | [Feature index](agent-docs/project/features/README.md) and the relevant feature record |
| Website deployment | [Website runbook](agent-docs/project/website.md) |
| Helium services | [Services](agent-docs/project/services.md) |

## Project constraints

- Support macOS arm64 and x86_64, with macOS 13 as the current minimum. Record Intel-under-Rosetta results separately from physical Intel acceptance.
- Target the latest macOS Chromium Stable independently of Helium/Xelium cadence. Check official freshness at input selection and immediately before publication and promotion; never downgrade Chromium to accommodate optional UI patches.
- Keep CI free: use the existing local Mac runner. Owner/main/canonical-repository guards must protect this public repository; do not run untrusted PR or fork code on the signing host. Recurring builds and automatic publication require an explicit request.
- Source and browser releases belong in public `leebyron/lune-browser`. Upload one `Lune-macos-ARCH.dmg` per architecture, appcasts, checksums and compact delivery metadata. Release-tag and latest URLs reference the same asset. Do not upload duplicate DMGs, source kits, Git bundles or unchanged dependency archives.
- Use production/stable delivery. Unpublished drafts and local fixtures are preparation tools, not a public staging channel. Release versions use `YY.MMDD.N`; never reuse a published version.
- Release notes are terse and factual: new features first, then bug/security fixes, compatibility, testing and known issues. No humor or lighthearted framing. Keep each paragraph and list item on one source line and allow natural wrapping.
- Optional browser services are hosted by Helium and require independent consent. Browser updates are delivered by Lune through GitHub. Lune service hosting is not deployed.
- Signing, notarization and Sparkle credentials remain in Keychain. Use the project's clean build environment; inherited shell tools can shadow macOS utilities and break upstream scripts.

## Engineering rules

- Prefer native Git fetch, merge, cherry-pick, rebase, and worktree operations
  for repository history. Preserve upstream ancestry and original authorship.
- Helium and ungoogled-chromium are patch/configuration repositories, not full
  Chromium trees. Use Helium's source preparation and quilt workflow at that
  boundary. Do not apply the ungoogled series twice.
- Keep reusable browser features independently upstreamable to Helium. Keep
  Lune branding, domains, signing keys, and release policy in separate commits.
  Follow the target upstream's current contribution guidelines; technical
  portability does not guarantee maintainer acceptance.
- Pin release inputs to full commit IDs and dependency/archive hashes. Record
  PR base/head, ordered commits, dependencies, provenance, and local adaptations.
  Never build a release from a moving PR URL or an unrecorded dirty tree.
- Stop integration on conflicts or failed validation. Do not automatically drop
  patches, choose ours/theirs, or accept fuzzy patch application to make CI green.
- A clean merge is not a release gate by itself. Validate source preparation,
  builds, browser behavior, signatures, and the installed-app update path on
  both supported architectures.
- Keep signing credentials out of source and untrusted build jobs. Use Lune's
  own identity, profile directory, service endpoints, and Sparkle public key.
- Publish immutable artifacts before updating the feed. Preserve the last good
  feed on failure and never overwrite a published binary or reuse its version.
- Keep Chromium source trees, build products, caches, private credentials, and
  generated workspaces out of the main branch.

## Working practices

- Keep changes focused and use descriptive branch names. Do not add a `codex/`
  prefix unless tooling explicitly requires it.
- Update project docs when a design decision changes. Distinguish recommendations,
  implemented behavior, source inspection, and runtime verification.
- Run checks appropriate to the actual change. Documentation changes need link,
  consistency, and whitespace checks, not a Chromium build.
- Browser patches should be developed in the prepared source tree, refreshed
  with quilt, unmerged into the correct core/platform repository, then committed.
- Preserve imported licenses and attribution. Check current upstream guidance
  before preparing a contribution; Helium currently requires human-written
  upstream issue/PR descriptions. Do not submit upstream messages automatically.
- Do not create schedules, releases, or deployments merely because they are
  described in the roadmap. Implement and activate them when that work is requested.

## Project references

`agent-docs/` contains documentation written by and for agents. Keep human-facing
documentation separate when it is added.

- [Definition and scope](agent-docs/project/README.md)
- [Repository and patch architecture](agent-docs/project/architecture.md)
- [Builds, releases, and updates](agent-docs/project/releases.md)
- [Services and website](agent-docs/project/services.md)
- [Website deployment runbook](agent-docs/project/website.md)
- [Implementation roadmap](agent-docs/project/roadmap.md)
- [Research and primary sources](agent-docs/project/research.md)
