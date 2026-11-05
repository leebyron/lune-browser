# Upstream architecture research

Reviewed 2026-11-05. Evidence below comes from upstream source and documentation,
not a local Chromium build. No runtime performance, signing, update, or hosting
claim has been validated for Lune. Recommendations are in the companion design
documents; this page distinguishes them from observed upstream behavior.

## Source snapshots

These are observed default-branch heads, not a proposed compatible release lock.

| Repository | Observed commit |
| --- | --- |
| [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium) | `de09e0c70c6bc1ac83d4ecdfd0e82c7e250c9a3c` |
| [Helium core](https://github.com/imputnet/helium) | `42da6c50c04f3b411879d5bdb1304f4d78ea9c81` |
| [Helium macOS](https://github.com/imputnet/helium-macos) | `37efe2c65dccc21aaf1d8ea66fd35d1348c386a8` |
| [Xelium macOS](https://github.com/minervanet/xelium-macos) | `c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42` |
| [Helium services](https://github.com/imputnet/helium-services) | `dc1a6e9038df1898598ea09fbd77e0710486dfc6` |

Files were read from default branches during this review; these commit links
provide snapshot anchors. Revalidate the files when implementing or upgrading.

## Findings

### 1. The upstream layering is configuration plus source preparation

The ungoogled [design document](https://github.com/ungoogled-software/ungoogled-chromium/blob/de09e0c70c6bc1ac83d4ecdfd0e82c7e250c9a3c/docs/design.md)
defines ordered quilt patches, binary pruning, domain substitution, build flags,
and platform packaging. Its [README](https://github.com/ungoogled-software/ungoogled-chromium/blob/de09e0c70c6bc1ac83d4ecdfd0e82c7e250c9a3c/README.md)
defines release tags as Chromium version plus ungoogled revision.

Helium [describes](https://github.com/imputnet/helium/blob/42da6c50c04f3b411879d5bdb1304f4d78ea9c81/README.md)
its origin in ungoogled-chromium and separate platform repositories.
Its macOS [preparation implementation](https://github.com/imputnet/helium-macos/blob/37efe2c65dccc21aaf1d8ea66fd35d1348c386a8/devutils/shared.sh)
applies core and platform patches, then substitutions, localization, versioning,
and resources. The [download config](https://github.com/imputnet/helium/blob/42da6c50c04f3b411879d5bdb1304f4d78ea9c81/downloads.ini)
uses prepared Chromium archives and a hash manifest.

Implication: integrate Git histories at the configuration layer and preserve the
source-processing pipeline. A prepared archive can reduce setup work; a matching
Chromium Git checkout is also supported by the macOS tools' `-c` option. A new
Chromium version may require archive/toolchain work even when Git merges cleanly.

### 2. Upstream contribution format is quilt, with native Git around it

The macOS [build/development guide](https://github.com/imputnet/helium-macos/blob/37efe2c65dccc21aaf1d8ea66fd35d1348c386a8/docs/building.md)
uses `source dev.sh`, `he setup`, `he build`, and `he run`. Development edits are
made in `build/src`, refreshed with quilt, then split back with `he unmerge`.
It documents x86_64 cross-builds on Apple silicon and version-update validation.

The core [contribution guide](https://github.com/imputnet/helium/blob/42da6c50c04f3b411879d5bdb1304f4d78ea9c81/CONTRIBUTING.md)
requires focused changes, correct core/platform ownership, Chromium conventions,
and clean Git history. It also asks for agreement before nontrivial features and
prohibits AI-written upstream issue/PR descriptions. This is a constraint on a
future upstream submission, not a reason to stop local design or development.

Implication: technical upstreamability is an engineering discipline, not an
assurance that any chosen feature will be accepted.

### 3. Xelium is a useful downstream example, not a daily integration service

Xelium's [README](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/README.md)
identifies a personal macOS Apple silicon distribution incorporating Helium PRs
2539 (visual tab switcher), 2747 (comfortable density), and 2367 (sidebar address
bar), plus local UI/identity changes. These are Xelium's recorded selections;
their current PR status and suitability for Lune have not been assessed here.

Its [series](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/patches/series)
combines platform, UI, rebrand, and updater patches. Its core submodule points
to Helium. This demonstrates the patch composition approach; it does not establish
that arbitrary patch subsets are independent.

The inspected [bump](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/.github/workflows/bump.yml)
and [build](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/.github/workflows/build.yml)
workflows use manual dispatch. The inherited build workflow lists both architectures,
but that does not prove Xelium's custom release path supports both.

### 4. Xelium's macOS release path is concrete and reusable

The [release script](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/release.sh)
configures Sparkle 2 with its own public key and raw GitHub appcast URL, a daily
check interval, builds with autoninja, signs the DMG with `sign_update`, and uses
GitHub CLI for releases. It checks clean/pushed source and public submodule
availability, with an explicit dirty-source override.

The [packager](https://github.com/minervanet/xelium-macos/blob/c5a6bfbeb2ec1b8caa33fa987b0947d771f7ea42/sign_and_package_app.sh)
sets `CFBundleVersion`, uses Chromium's `sign_chrome.py`, packages a DMG, invokes
Apple notarization/stapling, and checks signatures/Gatekeeper. Its defaults include
personal signing configuration and arm64 artifact names.

Implementation gaps for Lune: parameterize both architectures, allocate unique
versions, generate provenance-driven notes, isolate signing, avoid asset clobbering,
and keep draft feeds private. The script's `--draft` flag does not bypass its final
appcast commit/push block. Lune should retain the mechanisms while making promotion
an explicit final stage.

### 5. Helium services are explicitly self-hostable

The services [README](https://github.com/imputnet/helium-services/blob/dc1a6e9038df1898598ea09fbd77e0710486dfc6/README.md)
lists the extension proxy, uBlock mirrors, dictionaries, bangs, crash processing,
and update/download utilities. [Compose](https://github.com/imputnet/helium-services/blob/dc1a6e9038df1898598ea09fbd77e0710486dfc6/compose.yml)
and the [environment template](https://github.com/imputnet/helium-services/blob/dc1a6e9038df1898598ea09fbd77e0710486dfc6/.env.example)
provide a direct deployment starting point.

The [nginx template](https://github.com/imputnet/helium-services/blob/dc1a6e9038df1898598ea09fbd77e0710486dfc6/svc/nginx/nginx.conf.j2)
shows concrete endpoint paths, disabled access logging, TLS, and a root redirect
that needs Lune customization. The [sparkler configuration](https://github.com/imputnet/helium-services/blob/dc1a6e9038df1898598ea09fbd77e0710486dfc6/util/sparkler/.env.example)
accepts a GitHub repository, signing key, and output paths. Services code is
identified upstream as AGPL-3.0; preserve its license and attribution on import.

### 6. Git and scheduling have relevant operational limits

[Git worktree documentation](https://git-scm.com/docs/git-worktree) supports
parallel branch checkouts and detached build worktrees, but documents incomplete
multiple-worktree submodule support. Use ordinary clones for platform packaging
with submodules, and worktrees for suitable component topic work.

[GitHub schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
describes default-branch execution, possible delays/dropped jobs, and inactivity
disabling for public repositories. Treat scheduling as a trigger with monitoring.

[Sparkle documentation](https://sparkle-project.org/documentation/) is the primary
reference for updater integration, key generation, signing, and appcast setup.
Verify the exact version pinned by Lune before implementing those steps.

## Remaining research before implementation

- Validate shared ancestry and the precise metadata changes needed for the first
  ungoogled-to-Helium forward-port with real Git history.
- Test same-remote component branches and nested core submodule checkout from a
  clean clone; no such proof has been run in this documentation task.
- Inspect candidate PR diffs/dependencies before choosing any for Lune.
- Audit all browser-side service endpoints and updater identity changes.
- Measure both target builds and select supported macOS/SDK versions.
- Exercise signing, notarization, two successive updates, and service deployment.
