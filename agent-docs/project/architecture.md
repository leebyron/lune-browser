# Repository and patch architecture

Status: component histories and locked checkout/bootstrap tooling implemented.
Chromium 158 builds and smoke checks pass on arm64 and on x86_64 under Rosetta.
Reviewed Xelium UI composition is implemented
in a development candidate; generic replay and release orchestration remain planned. Based on the
[upstream source review](research.md) dated 2026-11-05.

## Recommendation: one remote, preserved component histories

Use this GitHub repository as the project home. Keep orchestration, manifests,
documentation, the website, and deployment configuration on `main`. Store browser
core, platform packaging, and services on component branches descended from their
respective upstreams. Assemble a working directory from exact component commits.

This gives us one repository and a unified local workspace, but not one source
tree containing every component on `main`. A lockfile commit defines the atomic
project version. It preserves upstream paths and ancestry for ordinary Git
merges/cherry-picks without relocating every upstream file into a subtree.

| History | Purpose |
| --- | --- |
| `main` | Project policy, lockfiles, orchestration, website, deployment overlays |
| `component/helium` | Integrated core patches/config, descended from Helium |
| `component/macos` | Platform patches/build tooling, descended from helium-macos |
| `component/services` | Self-hosted services, descended from helium-services |
| `topic/<feature>` | A focused contribution based on its target upstream |
| `integration/<id>/<component>` | Candidate assembly with an exact recorded base |

The three component branches are imported and published. Their first development
inputs are retained under `inputs/bootstrap-1/*`; see [building](building.md).
Never merge the unrelated `main`, macOS, and services roots into one another.
Use namespaced upstream tag refs to prevent unrelated version tags colliding.

These are ordinary branches with upstream parents, not orphan branches.
"Detached HEAD" is useful for checking out an immutable build input; it is not
durable storage. Every released component commit must remain reachable through
a permanent namespaced tag/ref, not only a SHA written into JSON.

## Planned main-branch layout

```text
AGENTS.md
README
agent-docs/project/            definition, decisions, research, operating procedures
config/                 product identity, platforms, channels, feature policy
manifests/              upstream policy, PR selections, exact release locks
scripts/                fetch, compose, validate, build, release entry points
website/                Lune website and download presentation
deploy/                 service overlays, host config, deployment automation
.github/workflows/      checks, integration, build, sign, publish
.work/                  ignored component checkouts and generated sources
.cache/                 ignored download/compiler caches
out/                    ignored artifacts and reports
```

Documentation, website, config/manifests, local build tooling, and validation CI
exist. Deployment overlays and browser release jobs remain planned. Commands
that prepare and compile Chromium pass for both targets; see
[current build evidence](builds/2026-11-05-chromium-158-port.md). Native Intel
hardware and release validation remain outstanding.

Use worktrees for core/services topic development when suitable. For macOS
packaging, prefer an ordinary isolated clone with its `helium-chromium` submodule:
Git documents incomplete support for submodules in multiple worktrees. Keep the
upstream directory layout so `dev.sh` and the build tools continue to work.
The macOS integration commit must pin the exact composed core gitlink and point
its submodule URL to a repository containing that commit. With this design that
can be the same Lune remote; the core branch has no recursive Lune dependency.
Publish the core ref before the platform ref and lockfile, then prove a fresh
recursive clone works. Do not use `submodule update --remote` in a release build.

## Two distinct kinds of patches

**Git commits** change the Helium configuration repository: patch files, series,
resources, flags, and tooling. Fetch/merge/rebase/cherry-pick these normally.

**Quilt patches** change the prepared Chromium source. Helium's preparation also
performs pruning, domain/name substitutions, resource generation, and localization.
Preserve that pipeline. Replacing it with `git apply` alone would omit build inputs.
Git-native integration does not require discarding upstream's patch format.

Helium already contains its ungoogled-chromium ancestry and patches. Integrating
a new ungoogled release updates that combined configuration history; it does not
mean applying a complete ungoogled series followed by a complete Helium series.

## Integration sequence

1. Discover the latest stable Chromium independently of downstream releases.
   Fetch ungoogled-chromium stable tags, Helium core/platform refs, and explicitly
   selected PR refs. Resolve names to full commit IDs before composing anything.
2. Set the integration target to that Chromium stable version. Select the newest
   compatible ungoogled release by parsed Chromium version and revision, not
   lexicographic tag ordering. If ungoogled itself is behind, forward-port its
   required patch/configuration stack rather than lowering the Chromium target.
   Pin Chromium source and matching dependencies.
3. Prefer a Helium core revision that already incorporates that release. Check
   ancestry and `chromium_version.txt`; a matching version string alone does not
   prove the ungoogled changes are present.
4. If Helium is behind, attempt a forward-port in a disposable integration branch:
   merge the selected ungoogled commit into the Helium-derived core, reconcile
   version/download/toolchain metadata, and validate the combined patch stack.
   Failed merges or source preparation block that candidate. Do not silently
   substitute an older release and call it current. Optional UI compatibility
   must not determine the Chromium version; conflicting features require explicit
   review and adaptation, never silent removal or a Chromium downgrade.
5. Apply reviewed PR commits in declared dependency order with
   `git cherry-pick -x`. Store explicit commit lists; blindly picking
   `base..head` can include unrelated history or merges. Preserve attribution.
6. Replay focused Lune contribution commits, then separate distribution changes.
   Resolve core/platform ordering through the manifests and the upstream series.
7. Pin the composed core into the composed platform, prepare fresh Chromium
   sources, and run the release gates on both architectures.

The automation does not choose conflict resolutions. A human-reviewed resolution
becomes a separate, attributable adaptation commit. `git range-diff` helps inspect
topic replays; `git rerere` may suggest prior resolutions but is not permission
to publish an unreviewed resolution automatically.

Use the complete Helium stack initially. "Some patches" should mean documented
feature groups and explicit removal commits, with dependencies on patches,
resources, settings, and build flags. Deleting arbitrary lines from `series`
is not a reliable feature-selection mechanism.

## PR and contribution lifecycle

Each selected PR records repository, number/URL, base/head SHAs, ordered commits,
dependencies, rationale, review status, and any local adaptation. New PR head
commits require review before the daily builder includes them. Upstream release
updates may be automated under the established integration policy.

When a PR lands, check whether its behavior is included in the selected Helium
base, including squash/rebase merges, then retire the downstream copy. Do not
treat an empty cherry-pick as sufficient evidence. Closed or force-pushed PRs
retain their pinned source until deliberately updated or removed.

Develop Lune features against a clean Helium base where possible. Use quilt in
the prepared Chromium tree, refresh, run `he unmerge`, and commit the resulting
core/platform patch changes on the appropriate topic branch. Integration branches
combine topics; upstream submissions contain only the relevant topic and declared
dependencies. Branding, bundle IDs, hosting, and release automation stay separate.

Helium's current [contribution policy](https://github.com/imputnet/helium/blob/42da6c50c04f3b411879d5bdb1304f4d78ea9c81/CONTRIBUTING.md)
requires maintainer agreement for nontrivial contributions and human-written issue
and PR descriptions. Lune can preserve technical upstreamability; it cannot
guarantee acceptance. A small fork in Helium's GitHub network may be needed when
actually submitting a PR, because a standalone Lune repository is not automatically
a valid cross-repository PR source. Treat that fork as a publication remote.

## Lockfile contract

Before enabling automation, define and validate a versioned lock schema containing:

- Orchestrator commit and product/config hash.
- Selected ungoogled release/tag/commit and Chromium version/source identity.
- Upstream core/platform commits and resulting composed commits.
- Ordered PR and Lune topic commits, adaptations, and patch/series hashes.
- Download/dependency hashes, toolchain/SDK/Sparkle versions, GN arguments.
- Target architecture, channel, build number, and required validation policy.

For the release-commit contract, the build version is the same `YY.MMDD.N`
string used for display and Sparkle ordering. The enclosing Git commit supplies
the orchestrator SHA; do not embed a commit's own SHA in its lock. See
[release commits](release-commits.md) for required records, hash boundaries,
preparation steps and the remaining implementation work.

Service deployment locks are separate from browser release locks, linked by a
service protocol/config version. A service outage or website edit should not
force a Chromium rebuild. Release reports add artifact hashes, signatures,
provenance, and validation results; they do not mutate the input lock.

The development validator supports an explicit `chromium_forward_port` record
when Chromium is newer than the recorded ungoogled release. It requires
`review_status: reviewed-port`, full `base_core_commit` and `chromium_commit`
IDs, and a `review` Markdown path under `agent-docs/project/builds/` included in
the lock's file hashes. Git validation checks ungoogled-to-base-to-integrated-core
ancestry and the original base version; the existing checks still require the
final core version, permanent tags, tree hashes, and platform gitlink to match.
Both host download manifests must name the exact target version and host archive.
Unrecorded mismatches and downgrades fail. Remove the forward-port record once a
matching upstream release is adopted. This supports documenting a reviewed port;
it does not establish successful compilation or runtime validation by itself.

## Alternatives considered

| Layout | Benefit | Cost / decision |
| --- | --- | --- |
| One remote, component branches | Native history and upstream paths; one project home | Requires checkout/lock tooling; recommended |
| Main repo with submodules in separate forks | Conventional dependency pinning and easy upstream PRs | Multiple hosted repos; best fallback if branch tooling becomes awkward |
| Git subtrees on main | Everything visible in one checkout | Path translation, split/export workflow, nested submodule adaptation; less direct upstream contribution |
| Full Chromium Git fork | Source-level Git history | Large history/DEPS and maintenance burden; unnecessary for this patch-based upstream |
| Orphan branches for imported components | Separate roots | Loses useful upstream ancestry; do not use for code imports |

Validate the component-branch/submodule bootstrap before investing in build CI.
If it adds more machinery than it saves, adopt conventional separate component
forks with pinned submodules without changing the release and patch policies.
