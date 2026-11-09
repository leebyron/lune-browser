# GitHub download and update delivery

Implemented on the release-download-flow branch, November 9, 2026. Publication
and stable promotion remain gated on the candidate's actual acceptance results.
The requested first date-versioned release is 26.1109.1; do not infer that a tag,
public candidate, or stable offer exists from this document alone.

## Public URL contract

All browser downloads, source kits, and appcasts live in the public
`leebyron/lune-downloads` repository. Browser source development remains private.
The Cloudflare website links to GitHub; it does not store browser binaries.

| Purpose | URL pattern |
| --- | --- |
| Release page | `https://github.com/leebyron/lune-downloads/releases/tag/v<VERSION>` |
| Versioned DMG | `https://github.com/leebyron/lune-downloads/releases/download/v<VERSION>/Lune-<VERSION>-macos-<ARCH>.dmg` |
| Latest stable DMG | `https://github.com/leebyron/lune-downloads/releases/latest/download/Lune-macos-<ARCH>.dmg` |
| Release's appcast | `https://github.com/leebyron/lune-downloads/releases/download/v<VERSION>/appcast-<ARCH>.xml` |
| Stable feed | `https://raw.githubusercontent.com/leebyron/lune-downloads/main/updates/stable/mac/appcast-<ARCH>.xml` |
| Staging feed | `https://raw.githubusercontent.com/leebyron/lune-downloads/main/updates/staging/mac/appcast-<ARCH>.xml` |

ARCH is arm64 or x86_64. Each release uploads a versioned DMG and an identically
hashed alias named Lune-macos-ARCH.dmg. GitHub's latest-release pointer makes the
website links permanent without a redeploy for subsequent releases. Sparkle
entries always reference the versioned DMG, never the latest alias.

Both feeds and their release metadata are promoted in one Git commit in the
public repository. Stable promotion also marks that GitHub release as latest.
Those two services are not a distributed transaction: if the second step fails,
inspect the feed and release pointer and resume promotion of the same verified
bytes. Never overwrite an asset or force-push a feed history. The publisher
rejects regressions and permits resuming the same release only with identical
metadata. GitHub's raw CDN can cache feed responses; verify readback before
announcing completion. Previous release assets remain available.

The existing lune.computer/updates/{stable,staging}/mac URLs redirect to the
GitHub files for compatibility. Keep their redirects when changing the website.
Do not deploy redirects before the corresponding GitHub files are accessible.
Do not deploy enabled download buttons before both stable latest aliases work.

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
   then inventories source files and symlinks. Output and bookkeeping exclusions
   are the root out/ and siso_result.json, Git/quilt metadata, Python bytecode,
   and Vite's node_modules/.vite development cache. Keep its archive verification and
   patch log. Existing output caches may be reused only after source comparison.
2. Finish tools and source validation and commit release notes. Fetch remote
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
5. Exercise the real About-page updater from published build 2 to the candidate
   with `scripts/release/check_update.py --expected-build VERSION`. Run both
   architectures sequentially, including invalid-signature and unsupported-OS
   rejection cases. Retain before/after profile and signature evidence.
6. Use `scripts/release/delivery.py --arm64 CANDIDATE --x86-64 CANDIDATE --output
   PUBLICATION --evidence ACCEPTANCE_JSON` to create matching feeds, immutable DMGs, latest-name aliases,
   release metadata, reviewed validation evidence and checksums. `scripts/release/source.py` exports the union
   of both architectures' pinned archives and exact component histories.
7. From the frozen source commit, `scripts/release/publish.py upload` uploads a
   draft first, verifies GitHub's asset digests, rechecks freshness and publishes
   a prerelease for hardware acceptance. It refuses to replace an existing
   release. A failed draft stays unpromoted for inspection; no --clobber is used.
8. Promote staging with `scripts/release/publish.py promote --channel staging`
   using actual signed install/update evidence for both architectures. Repeat
   the update test using GitHub's public HTTPS staging feeds. The owner tests
   installation, browsing, profile persistence and updates on native Intel.
9. After native Intel acceptance, tag the exact private source commit and use
   `promote --channel stable`. Record the owner's confirmation and tested Intel
   devices in acceptance.json, with the exact DMG hashes. Promotion requires a
   fresh Chromium check and verifies anonymous DMG bytes. Verify both raw feeds,
   both latest aliases and the release page, then deploy the website.

The public repository's release tag identifies its own distribution history.
The source kit and release.json identify the private source commit explicitly.
Never confuse those two histories. Keep builds 1 and 2 and their source unchanged.

## Manual Intel checklist

The owner has two native Intel Macs: one runs macOS 13.7.8; the second version
will be recorded at acceptance. The 13.7.8 machine also exercises the older-system
glass fallback. Use the candidate's Intel DMG on each test Mac. Record model,
macOS version, downloaded filename/hash and whether Rosetta is involved (native
Intel is required here). Drag Lune to Applications and launch normally through
Finder, without bypassing Gatekeeper. Verify About shows the release version and
Chromium version, then visit public HTTPS sites, use tabs/sidebar/settings, quit
and reopen, and confirm saved preferences and a test bookmark survive.

For the update check, start from the published build-2 Intel baseline in a
separate install location/profile, select the staging update server, enable
browser updates, and use About → Check for Updates. Confirm the offered version,
install/relaunch, and preserved test data. Do not run baseline and candidate
updater sessions concurrently. Report any crash, blank window, signing warning,
or failed update before stable promotion.

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

Rosetta may establish the Intel row's local software checks for staging; record
that execution mode explicitly and leave native_hardware false. Stable requires
native Intel results, model/OS entries in devices, and the owner's actual
confirmation. Include report hashes and concise test results as additional fields
so the booleans can be audited. The validation.json uploaded with the candidate
is immutable; later hardware acceptance is recorded separately in the promoted
feed commit. Do not overwrite the original candidate evidence.
