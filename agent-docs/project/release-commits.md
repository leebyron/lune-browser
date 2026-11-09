# Release commits and version information

Status: release procedure agreed November 7, 2026; two-digit release year
selected November 8, 2026.
This document defines the release contract. The release-download-flow tooling
implements date versions, frozen records and GitHub delivery; see
[the executable runbook](release-delivery.md). The audit checklist below records
the original migration requirements; actual runtime acceptance remains required. No release is allocated
by the examples in this document.

## Identity and version rules

One reviewed commit in the project history freezes the release version and all
declared build inputs for both architectures. Its full Git SHA identifies that
source state. A release version orders updates; a SHA identifies source; an
artifact hash identifies the actual delivered bytes.

Use `YY.MMDD.N`, for example `26.1108.1`. `YY` is the last two digits of the
release year; retain the full four-digit year in the recorded ISO date.
`N` starts at 1 for each date and
increases for each allocated release that day. Use America/Los_Angeles as the
release-calendar timezone, matching the owner's working timezone. Record an ISO
date and timezone explicitly; do not infer them from a build host's clock, Git
author/committer timestamp, or CI run time. Format MMDD with four digits, including
a leading zero for January through September; compare components numerically.

Generate these four values from the same committed version:

| Field | Example |
| --- | --- |
| Outer app `CFBundleVersion` | `26.1108.1` |
| Outer app `CFBundleShortVersionString` | `26.1108.1` |
| Appcast `sparkle:version` | `26.1108.1` |
| Appcast `sparkle:shortVersionString` | `26.1108.1` |

Sparkle accepts numeric `x`, `x.y`, and `x.y.z` versions; a separate lifetime
integer counter is unnecessary. See its [version comparator](https://sparkle-project.org/documentation/api-reference/Classes/SUStandardVersionComparator.html)
and [appcast documentation](https://sparkle-project.org/documentation/publishing/).
Keep Chromium's engine version, framework layout, helper/version dependencies,
and protocol-facing version information intact. About should show the Lune
version and full Chromium version separately; expose the source SHA as diagnostic
information, not as a suffix in the sortable version.

Use `v26.1108.1` as the source release tag and
`Lune-26.1108.1-macos-arm64.dmg` / `Lune-26.1108.1-macos-x86_64.dmg`
as artifact names. Both architectures share one release identity. Feed channel
and architecture are separate metadata, not version suffixes. Staging-to-stable
promotion of the exact same artifacts retains the version.

Serialize allocation against the latest release records on main. Once committed,
a version is reserved even if validation fails; gaps are allowed. Retrying an
unchanged candidate retains its version. Changed release inputs require a new
version and release commit. Never reuse an allocated version for different
inputs, overwrite published bytes, or move a published release/input tag. A
replacement offered to installed clients must compare greater than the latest
version they could have installed, including staging versions. Reject backdated
allocations and stale concurrent promotions. Rollbacks use a new higher version
and the normal profile-compatibility and security-freshness gates.

## What belongs in the release commit

The entrypoint is `manifests/releases/<version>.json`, an immutable
record for each allocation. The release model validates this record before build, packaging and publication.
Existing locks remain the canonical source for component details: the release
record references them by repository-relative path and SHA-256 rather than
maintaining a second independently editable copy. Resolve paths at the release
commit, never at today's main branch.

| Required information | Existing source or required addition |
| --- | --- |
| Release identity | New release record: schema version, Lune version, ISO release date, calendar timezone, daily sequence, intended initial delivery channel, both targets, expected tag and filenames. Derive redundant strings and validate agreement. |
| Chromium | `manifests/browser.lock.json`: full version and source identity; both download manifests: exact source/platform archive URLs and cryptographic hashes. |
| ungoogled-chromium | Browser lock: upstream tag and full commit; retain the reviewed forward-port record when Chromium is newer than that base. Never label the base as a newer ungoogled release. |
| Helium core and macOS | Browser lock: original upstream commits, integrated commits, tree hashes, permanent refs, and the macOS core gitlink. Record an upstream release tag/version when applicable; a full commit is authoritative when no release tag describes the input. |
| Xelium, selected PRs, and Lune patches | `manifests/patches.json` plus retained component history: source commits, PR base/head and ordered commits, dependencies, patch hashes, review status, local adaptations and attribution. |
| Bundled dependencies and assets | Both download manifests and locked component dependency configuration: Sparkle, search data, onboarding, uBlock, compiler/sysroot/PGO inputs and any other fetched build input. Require immutable revisions or verified hashes, including transitive downloads. |
| Product and service configuration | `config/product.json` and component patches: bundle/profile identity, artwork, service provider/origin, Sparkle public key, signing team/identity, minimum supported OS and per-architecture feed URLs. Services deployed independently retain separate locks; their live state does not define browser source identity. |
| Build and packaging recipe | Commit the exact release commands/configuration, per-target GN settings and all overrides, target/host architecture rules, updater settings, branding flags, deployment target, packaging format/options and output-affecting environment settings. Include scripts/workflow revisions through this commit and component pins. |
| Toolchain | Product config currently pins Xcode version/build and SDK version. Add exact Metal, compiler/linker, GN/build tooling, Python, package and packaging/signing tool identities where not already pinned transitively. Pin fetched tools by digest; record host macOS version/build requirements. A Brewfile of formula names is insufficient. |
| Release notes and acceptance policy | Commit the notes and required validation policy or references to their committed files, including known limitations and intended channel. Passing results are produced afterward. |

The release record should contain `browser_lock` and `product_config` path/hash
references and references to the committed build recipe, toolchain inventory,
release notes, and validation policy. Hash referenced inputs with a declared
algorithm and validate the entire reference chain. Configuration that varies by
architecture must be explicit. Referenced files may be shared across releases;
their historical contents remain fixed by the enclosing commit.

Do not put the release commit's own SHA inside a file in that commit, or create
a cycle where a lock hashes itself or a file that hashes it. Obtain the full SHA
with `git rev-parse HEAD` after committing, then place it in generated metadata,
the annotated tag, and release provenance. The release record does not need an
`orchestrator_commit` field; its enclosing commit supplies that identity.

No dirty tracked files, untracked build inputs, mutable branch downloads, or
unrecorded local overrides may contribute to release artifacts. The production
recipe must consume committed data rather than reconstructing flags from prose
or whichever generated workspace happens to exist. Exact source state is the
goal; bit-for-bit reproducibility remains unproven.

## What is produced after the commit

Keep build products and reports under ignored work/output directories and attach
the reviewed source kit and evidence to the immutable release. Do not amend the
release commit to insert results or hashes of its own artifacts.

Record at least:

- Full release commit SHA, version, release-record and lock hashes, exact component
  commits, and target architecture for each artifact.
- Actual host OS, tool versions, effective GN arguments and their hashes,
  preparation/build logs, executable/framework hashes, and source-cleanliness
  verification. Compare these with declared inputs; unexplained differences
  block release rather than becoming retroactive exceptions.
- Smoke and acceptance reports, native versus Rosetta execution, installed-update
  baseline/result, profile persistence, and negative update tests. Record whether
  each required gate passed, failed, or remains outstanding.
- Signing certificate identity/fingerprint, notarization submission/result,
  stapling and Gatekeeper results, and Sparkle signature verification. Credentials
  and private keys stay outside Git and published evidence.
- Final app/DMG and source-kit filenames, sizes, cryptographic hashes, signatures,
  immutable download URLs, source availability, and feed/readback evidence.
- Chromium macOS stable freshness checks at integration, public release publication
  and immediately before promotion: candidate/latest versions, check time, source,
  result and decision. Include any explicit owner-approved known-lag exception
  required by the [freshness gate](releases.md#chromium-freshness-gate), plus
  publication/promotion timestamps and the channel actually promoted.

Signing timestamps, notarization tickets, and packaging metadata can change bytes
without changing the declared source. Record final hashes after signing/stapling;
never treat a source SHA as a binary checksum. A retry may generate new local
outputs before publication, but only the selected, validated bytes may be
published. Once published, promote or redeliver those exact bytes. A replacement
binary needs a new release allocation even if browser source is unchanged.

## Procedure

1. **Finish integration.** Commit the core/platform changes, update the macOS
   gitlink, retain immutable component input refs, and update the browser lock,
   download hashes and patch provenance. Publish required core refs before
   platform refs, then the project lock, when publication is authorized. Verify
   a fresh recursive checkout can reach every pinned input. Resolve conflicts
   and failed checks explicitly; never discard patches to obtain a build.
2. **Prepare the release record.** Inspect existing allocations and published
   feeds, choose the next date/sequence, and record the version once. Freeze the
   notes, recipe, toolchain and per-target settings. Refresh affected lock hashes.
   Verify every external download is pinned and every required tool is identified.
   Do not allocate separate versions for arm64 and Intel.
3. **Review and commit.** Review only the intended release changes; leave unrelated
   work in its existing checkout and build from a clean release checkout. Run
   `git diff --check` and `python3 scripts/lune.py validate --git-objects`, plus
   the relevant configuration tests. The record validator and reservation command check identity,
   ordering and hashes; component validation checks reachability. Commit with a descriptive message such as
   `Prepare Lune 26.1108.1 release`. Obtain its full SHA. Do not amend/rebase
   this frozen release commit; corrections get a new allocation.
4. **Build that exact commit.** Use a clean checkout of the recorded SHA, the
   pinned toolchain and fresh source preparation following [building](building.md).
   `python3 scripts/lune.py doctor` checks current host prerequisites, but does
   not establish a complete immutable toolchain. Generate release metadata and
   all four version fields from the committed record. Build each architecture
   from its declared settings. Use `scripts/release/build.py` for the frozen recipe; the development
   wrapper does not enforce this contract. Stop on input or environment drift.
5. **Validate and package.** Apply every gate in [releases](releases.md), including
   both architecture builds, native Intel acceptance and the installed-app update
   path. Run acceptance browsers sequentially because Sparkle shares bundle
   state. Verify the staged outer plist values and engine/framework versions
   before signing; sign, notarize, staple, package and Sparkle-sign the final
   bytes. Record evidence without altering the input commit. A failed gate leaves
   the candidate unpromoted.
6. **Retain and publish the release.** Apply the
   [freshness gate](releases.md#chromium-freshness-gate): recheck the latest macOS
   stable Chromium, record the comparison, and block known lag unless the owner
   explicitly approves a release-specific exception. An unavailable check blocks
   publication. After acceptance, create an immutable
   annotated `v<version>` source tag pointing to the exact release commit, even
   if main has moved. Assemble corresponding source from that commit and all
   pinned dependencies, preserving licenses and provenance. Publication must
   stay within the authorized payload and destination. The public
   `leebyron/lune-downloads` repository has its own history: its matching release
   tag does not itself identify the private source commit; the published source
   kit/provenance must explicitly identify it. Upload both architecture artifacts,
   source, checksums and evidence before updating any feed, then verify readback.
7. **Promote the validated artifacts.** Generate matching architecture appcasts
   and run staging installed updates before stable promotion. Immediately before
   promotion, recheck macOS stable Chromium and version ordering, and record the
   freshness decision or explicit exception for this promotion. A staging check
   or exception does not automatically authorize stable promotion. Promotion
   reuses the same bytes/version.
   Update both stable feeds and website metadata only after all gates pass;
   preserve the last good feeds on failure and detect partial promotion. Record
   results separately. This procedure does not enable recurring jobs or automatic
   publication.

## Implementation and remaining acceptance

The release-delivery tools now implement frozen records, numeric date versions,
explicit GN/tool identities, both-target source export, GitHub asset publication,
paired feed commits, latest aliases, freshness checks, and native Intel promotion
requirements. `reserve.py` checks retained allocations before creating a record;
fetch all remote branches first and serialize the reservation commit. This is a
manual release flow, not a concurrent release scheduler.

The freshness gate fails closed on unknown or behind-Stable results. An approved
known-lag exception needs a separately reviewed implementation; these tools do
not silently honor an old approval or bypass the check. Fresh checks run before
candidate publication and each channel promotion.

The actual Sparkle 2.10.1 comparator accepts the date format and orders it after
build 2, including same-day and year transitions. Every candidate still needs
installed-update tests from build 2, matching signed artifacts, both architecture
runtime checks, and native Intel owner acceptance before stable. Unit tests are
not substitutes for those gates.

`prepare.py` inventories every prepared source file and symlink except output
and bookkeeping directories. `build.py` compares that complete inventory before
and after compilation, including added or removed files. Reusing cached outputs
requires comparison with a clean preparation from the locked archives. Retain
archive verification, strict replay and preparation evidence. A complete
bit-for-bit reproducible environment remains unproven; tool checks cover the
recorded compiler/build/PGO, Xcode/SDK/Metal, Python and sccache inputs. Signing
and notarization credentials stay external.

Do not rename or replace published build-1/build-2 artifacts, source kits or
historical evidence. They remain valid migration baselines.
