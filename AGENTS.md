# Working on Lune

Lune is a personal Chromium browser distribution assembled from
ungoogled-chromium, Helium, selected upstream PRs, and our own contributions.
Read [the project definition](agent-docs/project/README.md) and
[architecture](agent-docs/project/architecture.md) before changing its structure.

## Current state

`main` contains the project definition, locked development build inputs, local
build commands, validation tests/CI, and the Cloudflare website. Imported histories
are published on `component/helium`, `component/macos`, and `component/services`;
permanent `inputs/bootstrap-1/*` tags retain the first development inputs.
Read [the build runbook](agent-docs/project/building.md) before running the tools.

Lune's first arm64 development build passed full source preparation, GN generation,
compilation, and a headless app smoke test (page loading, JavaScript, and profile
persistence). The onboarding XML parser fix is pinned under `inputs/bootstrap-2/macos`.
See [the first build evidence](agent-docs/project/builds/2026-11-05-arm64.md).
Native Intel hardware, signing, packaging, and update validation remain outstanding.
The local Mac passes storage and toolchain preflight. Xcode 27.2/27B52 and SDK
27.2 are pinned for an experimental development build after Chromium source review.
The owner requires no additional CI spend: use this Mac as a self-hosted GitHub
Actions runner. The manual browser workflow accepts reviewed main-branch runs
from the owner only; no scheduled or public-release job is enabled. Signing identities exist
in Keychain; notarization and packaging remain to be validated. Automatic updates,
public browser releases, services deployment, and recurring browser builds are
not enabled. Targets are macOS arm64 and x86_64. Website status is recorded in
[the website runbook](agent-docs/project/website.md).

The development lock now targets Chromium 158.0.8127.18 with the reviewed
ungoogled/Helium forward port and Xelium UI stack. Both architectures build;
arm64 headless/headed and Intel-under-Rosetta smoke checks pass, including Lune
artwork, defaults, settings, and French/German upstream attribution. Permanent
`inputs/chromium-158-1/{helium,macos}` tags retain the inputs. Focused native arm64
inspection passed with the inherited command-bar internal-URL limitation recorded.
These are development builds, not signed/notarized releases. See
[the port evidence](agent-docs/project/builds/2026-11-05-chromium-158-port.md).
Hosted setup checks are currently blocked by GitHub account billing; their local
equivalents pass. See the build runbook before retrying or changing CI capacity.

The Xelium UI candidate is described in [UI integration](agent-docs/project/xelium-ui.md).
Target the latest stable Chromium independently of upstream browser release cadence;
never downgrade Chromium to satisfy optional UI patches. Discovery reports stable lag.

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
