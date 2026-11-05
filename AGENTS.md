# Working on Lune

Lune is a personal Chromium browser distribution assembled from
ungoogled-chromium, Helium, selected upstream PRs, and our own contributions.
Read [the project definition](agent-docs/project/README.md) and
[architecture](agent-docs/project/architecture.md) before changing its structure.

## Current state

This repository contains the project definition and architecture research.
Build scripts, component branches, CI, hosting, signing, and automatic updates
have not been implemented. Proposed paths and commands in the docs are designs,
not existing interfaces. The initial platform target is macOS, both arm64 and
x86_64.

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
- [Implementation roadmap](agent-docs/project/roadmap.md)
- [Research and primary sources](agent-docs/project/research.md)
