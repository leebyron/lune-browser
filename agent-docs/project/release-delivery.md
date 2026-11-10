# GitHub download and update delivery

Lune 26.1109.2 is the latest production release, with paired stable feeds,
immutable/version-independent downloads, and public source at its signed Git tag.
26.1109.1 remains published and downloadable. See
[26.1109.2 evidence](builds/2026-11-09-release-26.1109.2.md) for exact hashes,
verification and the version-bound owner deferral of physical Intel acceptance.
Rosetta checks never establish native Intel results.

Use production/stable delivery only. Preparation uses an unpublished GitHub draft
and loopback fixtures, not a public staging channel or prerelease. Frozen source
commits and existing release records remain immutable. Run build/package commands
from the frozen checkout. The current publication tool accepts `--source-checkout`
pointing to that checkout and records its own distinct publisher commit.

## Public URL contract

Source, browser releases, appcasts and compact release metadata all live in
`leebyron/lune-browser`. Its signed release tag identifies the exact frozen source;
permanent component input tags retain the imported histories.
The Cloudflare website links to GitHub; it does not store browser binaries.

| Purpose | URL pattern |
| --- | --- |
| Release page | `https://github.com/leebyron/lune-browser/releases/tag/v<VERSION>` |
| Versioned DMG | `https://github.com/leebyron/lune-browser/releases/download/v<VERSION>/Lune-macos-<ARCH>.dmg` |
| Latest stable DMG | `https://github.com/leebyron/lune-browser/releases/latest/download/Lune-macos-<ARCH>.dmg` |
| Release's appcast | `https://github.com/leebyron/lune-browser/releases/download/v<VERSION>/appcast-<ARCH>.xml` |
| Stable feed | `https://raw.githubusercontent.com/leebyron/lune-browser/main/updates/stable/mac/appcast-<ARCH>.xml` |

ARCH is arm64 or x86_64. Upload exactly one DMG per architecture, named `Lune-macos-ARCH.dmg`. The release-tag URL identifies immutable bytes; GitHub's latest-release URL resolves to that same asset in the latest production release. Sparkle enclosures use the release-tag URL, never the moving latest URL. No duplicate version-named DMG or alias upload is needed.

Both feeds and their release metadata are promoted in one Git commit in the
public repository. Stable promotion also marks that GitHub release as latest.
Those two services are not a distributed transaction: if the second step fails,
inspect the feed and release pointer and resume promotion of the same verified
bytes. Never overwrite an asset or force-push a feed history. The publisher
rejects regressions and permits resuming the same release only with identical
metadata. GitHub's raw CDN can cache feed responses; verify readback before
announcing completion. Previous release assets remain available.

The owner retired the separate distribution repository and requested no legacy
URL compatibility. Do not create redirects or maintain its old feeds. Remove
legacy website feed redirects and historical staging assets from the current
website. Do not deploy enabled download links until the canonical release-tag downloads,
latest download links and stable feeds pass anonymous readback.

The moved 26.1109.1/26.1109.2 DMGs retain their signed bytes and embedded old
updater URL. Their stock updater stops when the former repository is deleted;
manual downloads are required until a new browser build embeds the canonical
feed. The owner subsequently requested issue #24 plus a new release to do this.
Do not claim a repository move rewrites an already signed app's updater URL.

## Version and source identity

The signed outer app, Sparkle, and release filenames use YY.MMDD.N. Chromium's
engine version and nested framework identity are unchanged. About and lune://version
read LuneReleaseVersion from the signed outer app; development apps without it
retain the inherited version display. LuneSourceRevision records the project SHA.

`manifests/releases/<VERSION>.json` freezes the date, sequence, both architectures,
input hashes and tag. Do not hash the record into itself. The enclosing Git commit
supplies its SHA. `config/release-recipe.json` records explicit GN arguments,
compiler/build/PGO tool hashes, and Xcode, SDK, Metal, Python and sccache identities.
Signing credentials stay in Keychain. Builds use the existing local Mac at no
additional CI cost; this work does not activate scheduled release jobs.

## Commands and gates

1. Integrate source changes, review and retain component input tags, verify the
   complete patch series without fuzz using `scripts/release/prepare.py
   --platform PLATFORM_CHECKOUT --report PREPARED_REPORT`. It refuses an existing
   source tree, uses the locked host archive manifest and upstream preparation,
   generates onboarding's deterministic strings module, then inventories source
   files and symlinks. Output and bookkeeping exclusions
   are the root out/ and siso_result.json, Git/quilt metadata, Python bytecode,
   and Vite's node_modules/.vite development cache. Keep its archive verification and
   patch log. Existing output caches may be reused only after source comparison.
2. Finish tools and source validation and commit release notes following the
   [release-note style](releases.md#release-note-style): terse and factual, with
   new features first, then bug fixes and security changes. Keep each paragraph
   and list item on one source line; allow natural line wrapping. Fetch remote
   branches and tags, then run `scripts/release/reserve.py --version VERSION`.
   Review and commit the resulting record, serializing against other allocations.
   Check Chromium freshness with `scripts/release/freshness.py`. Its failure or
   known lag blocks publication; no automatic exception path is implemented.
3. Run `scripts/release/build.py --version VERSION --arch ARCH --source SOURCE
   --prepared-report REPORT --report BUILD_REPORT` for each architecture. It
   verifies clean frozen inputs, source hashes, tools and GN arguments before
   compilation, and verifies source hashes again afterward. Include chrome,
   chromedriver and chrome/installer/mac. Run matching smoke/onboarding checks.
4. Run `scripts/release/package.py stage --version VERSION --arch ARCH --output
   OUTPUT --build-report BUILD_REPORT --smoke-report SMOKE_REPORT --directory
   CANDIDATE`, then its `sign` and `package` commands on that directory. Each
   stage refuses existing output. Signing uses nested Chromium signing, Apple
   notarization, stapling, Gatekeeper and Sparkle Ed25519 verification.
   After signing, use the reviewed `scripts/release/check_runtime.py --app APP
   --driver DRIVER --directory REPORT_DIRECTORY --version VERSION
   --chromium-version CHROMIUM --arch ARCH`. It checks signed bundle identity,
   Mach-O minimums, About and lune://version, real public HTTPS navigation and
   restart persistence in a disposable profile. It records native versus Rosetta
   execution and does not count Rosetta as native Intel acceptance.
5. Exercise the real About-page updater from published build 2 to the candidate
   with `scripts/release/check_update.py --expected-build VERSION`. Run both
   architectures sequentially, including invalid-signature and unsupported-OS
   rejection cases. Retain before/after profile and signature evidence.
6. Use `scripts/release/delivery.py --arm64 CANDIDATE --x86-64 CANDIDATE --output
   PUBLICATION --evidence ACCEPTANCE_JSON` to create matching feeds, one immutable DMG per architecture,
   release metadata, reviewed validation evidence and checksums. Source is retained
   in the public Git repository; source-kit export is not a release prerequisite.
7. Retain a signed annotated `v<VERSION>` source tag at the exact frozen source
   commit and push it and all permanent component input refs to the public source
   repository. Use the current publisher with `upload --source-checkout FROZEN
   --directory PUBLICATION --notes-file NOTES`. It checks anonymous source access
   and exact ref targets, then creates an unpublished, non-prerelease draft and
   uploads only browser delivery files and compact metadata. GitHub asset digests
   must match. Keep upload-receipt.json; promotion rechecks every uploaded asset
   and the public source refs. No asset is overwritten or dependency archive copied.
8. Download the draft's signed DMG using the owner's authenticated GitHub access
   for native Intel acceptance. Use a loopback HTTP test fixture to exercise
   build 2's real updater with these exact final DMG bytes; this is a local test,
   not a staging delivery channel. Record hardware results and owner confirmation
   against the DMG hashes. Never label Rosetta checks as native Intel acceptance.
9. After native Intel acceptance or an explicit owner-approved deferral recorded
   in the version/hash-bound acceptance JSON, run
   the reviewed publisher's `promote --channel stable --source-checkout FROZEN`
   with the publication directory, acceptance JSON, and public checkout. All
   acceptance checks (including any recorded native Intel deferral) and a fresh
   Chromium lookup pass before it undrafts the final
   release. It verifies anonymous immutable downloads, rechecks freshness, commits
   both stable feeds, then marks the release latest. Verify both raw feeds,
   both latest download links, the release page and public HTTPS installed updates,
   then deploy the website. If a step fails, preserve existing feeds and resume
   the same verified bytes; do not create a prerelease as a workaround.

Release tags now belong to the source repository and identify the frozen source
commit directly; release.json records its full SHA. Keep builds 1 and 2 and their source unchanged.

## Manual Intel checklist

The owner has two native Intel Macs running macOS 13.7.8 and 26.6.2, confirmed
on November 9. The 13.7.8 machine exercises the older-system glass fallback;
26.6.2 exercises the native glass path. These are planned test environments,
not completed acceptance results. The owner deferred these checks for 26.1109.1;
keep them as post-release follow-up rather than asserting they passed. Use the
candidate's Intel DMG on each test Mac. Record model,
macOS version, downloaded filename/hash and whether Rosetta is involved (native
Intel is required here). Drag Lune to Applications and launch normally through
Finder, without bypassing Gatekeeper. Verify About shows the release version and
Chromium version, then visit public HTTPS sites, use tabs/sidebar/settings, quit
and reopen, and confirm saved preferences and a test bookmark survive.

For the update check, start from the published build-2 Intel baseline in a
separate install location/profile, select the provided loopback test server, enable
browser updates, and use About → Check for Updates. The local fixture serves the
exact final signed DMG, with only its test enclosure URL changed; the production
app and signed archive retain the stable feed configuration. Confirm the offered version,
install/relaunch, and preserved test data. Do not run baseline and candidate
updater sessions concurrently. Report any crash, blank window, signing warning,
or failed update before stable promotion.

### Portable loopback fixture

The handoff includes `manual_update_fixture.py`, the publication manifest and
both signed DMGs/appcasts, plus the unchanged build-2 Intel baseline. The helper
uses Python 3.9 or newer without additional packages; check `python3 --version`
on the test Mac first. It verifies the selected feed and DMG hashes, serves only
those two paths on 127.0.0.1, and changes only the enclosure URL in memory. It
neither launches Lune nor changes the signed app or a public channel. Its server
tests cover exact archive delivery, preserved signatures/hardware requirements,
rejection of changed files, and denial of unrelated file paths. Running the
helper alone does not count as browser acceptance.

From the handoff folder, run:

```sh
python3 manual_update_fixture.py --directory publication --arch x86_64
```

Keep that terminal open. Copy build 2 from its DMG into a new `update-test`
folder using Finder, keeping the app named Lune.app. Quit other Lune instances.
In another terminal, launch that copy with a new disposable profile and the
local base URL printed by the helper:

```sh
open -n -a "$PWD/update-test/Lune.app" --args \
  --user-data-dir="$PWD/update-profile" \
  --custom-update-server-url=http://127.0.0.1:PRINTED_PORT/
```

Enable browser updates in Settings, save a test bookmark and preference, then
use About to install the update and relaunch. Confirm 26.1109.1, public browsing,
and the saved data after relaunch. Quit the test app before stopping the server.
Use a second, fresh copy/profile of build 2 for the negative case:

```sh
python3 manual_update_fixture.py --directory publication --arch x86_64 \
  --case wrong-architecture
```

On native Intel, About must decline this Apple silicon offer and retain build 2.
The feed retains `hardwareRequirements=arm64`; only its test route is named for
Intel so the Intel updater can inspect and reject it. Apple silicon/Rosetta
cannot establish this hardware-rejection result. Record both outcomes and any
error text with the candidate DMG hash. These instructions are prepared;
owner-run native Intel results remain pending.

## Acceptance record

`delivery.py --evidence` and `publish.py promote --acceptance` consume the same
JSON shape. Populate it from completed checks, never from planned work:

```json
{
  "version": "26.1109.1",
  "source_commit": "FULL_FROZEN_PROJECT_SHA",
  "architectures": {
    "arm64": {
      "sha256": "EXACT_SIGNED_DMG_SHA256",
      "install": false,
      "browse": false,
      "profile_persistence": false,
      "signed_app": false,
      "installed_update": false,
      "native_hardware": true
    },
    "x86_64": {
      "sha256": "EXACT_SIGNED_DMG_SHA256",
      "install": false,
      "browse": false,
      "profile_persistence": false,
      "signed_app": false,
      "installed_update": false,
      "native_hardware": false,
      "devices": [],
      "owner_confirmation": ""
    }
  }
}
```

Rosetta may establish the Intel row's pre-publication software checks; record
that execution mode explicitly and leave native_hardware false. Stable requires
native Intel results, model/OS entries in devices, and the owner's actual
confirmation. Include report hashes and concise test results as additional fields
so the booleans can be audited. The validation.json uploaded with the draft
is immutable; later hardware acceptance is recorded separately in the promoted
feed commit. Do not overwrite the original candidate evidence.

## Focused release uploads

The source repository is public. Publish browser DMGs (versioned and permanent
latest links), architecture appcasts, checksums and compact release/validation
metadata. Link the exact signed public source tag and permanent component refs.
Do not re-upload Git history bundles, source kits, or unchanged source/dependency
archives merely to duplicate what the public repository and recorded immutable
URLs already provide. Verify source reachability and hashes; preserve existing
published assets and licenses. The owner explicitly selected this approach while
publishing 26.1109.2. That release removed redundant source assets only from its
unpublished draft; the prior production release remains intact.

The active upload command enforces this focused asset set. `scripts/release/source.py`
remains an optional local export utility for an explicit request, not a routine
production gate. Source availability is required; duplicate archive uploads are not.
