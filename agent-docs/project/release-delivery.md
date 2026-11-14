# GitHub download and update delivery

Read [current status](status.md) for published releases, active preparation and validation limits. This is the executable manual-release runbook; [release policy](releases.md) and [release commits](release-commits.md) define its gates and frozen-input contract. Rosetta checks never establish native Intel results.

Use production/stable delivery only. Preparation uses an unpublished GitHub draft
and loopback fixtures, not a public staging channel or prerelease. Frozen source
commits and existing release records remain immutable. Run build/package commands
from the frozen checkout. The current publication tool accepts `--source-checkout`
pointing to that checkout and records its own distinct publisher commit.

Launch upload and promotion with `python3 scripts/release/run_publisher.py`,
followed by the publisher arguments below. Run it from the normal configured
shell, not through the compilation environment wrapper. The launcher keeps
macOS utilities first, resolves only the GitHub CLI and OpenPGP tool directories,
and preserves `GNUPGHOME`, `GPG_TTY`, SSH agent and GitHub authentication settings.
It checks tool availability before publication. Compilation continues to exclude
these credentials. Git signing uses the existing configured key; an omitted
`GNUPGHOME` must not be mistaken for a missing key or trigger key recreation.

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

## Preflight before a long build

Check Chromium freshness, available disk space, the frozen Python/toolchain requirements and access to the existing signing/notarization credentials before starting hours of compilation. A changed PGO profile can require extensive recompilation even when compiler bytes and most source files match the cache. Follow the [build environment and storage policy](building.md#prepare-this-mac); an explicitly approved lower preparation floor is scoped to that preparation and must be recorded with its measured free space and selected inputs. It does not change the normal policy or the pre-build floor.

Keep ordinary browser fixtures off public update delivery with `--custom-update-server-url=http://127.0.0.1:1/`; use the intended fixture feed only for explicit updater checks. Chromium's `--disable-background-networking` and host-resolver rules do not isolate Sparkle's native networking. Record app/framework identities before and after tests so a public update cannot silently replace the development app being validated. Signed canonical-feed checks deliberately omit the override and verify the exact app identity separately.

Test notarization access with `xcrun notarytool history --keychain-profile lune-notary`. If it reports that the item cannot be found, follow [Keychain recovery](building.md#signing-readiness) before requesting credential re-entry. The default profile lives in the data-protection Keychain, shown as iCloud or Local Items in Keychain Access. An unlocked file-based login Keychain, a failed `security find-generic-password` lookup or an explicit `--keychain login.keychain-db` query does not establish that this profile is absent. Inspect the existing `com.apple.gke.notary.tool` item and retry the default profile; keep passwords hidden and credentials in Keychain.

## Commands and gates

1. Integrate source changes, review and retain component input tags, verify the
   complete patch series without fuzz using `scripts/release/prepare.py
   --platform PLATFORM_CHECKOUT --report PREPARED_REPORT`. It refuses an existing
   source tree, uses the locked host archive manifest and upstream preparation,
   generates onboarding's deterministic strings module, then inventories source
   files and symlinks. Output and bookkeeping exclusions
   are the root out/ and siso_result.json, Git/quilt metadata, Python bytecode,
   and Vite's node_modules/.vite development cache. Keep its archive verification and
   patch log. Wait for successful completion and the final inventory report before
   selecting or reserving a release version; do not overlap allocation with preparation.
   Use an input-named preflight workspace until preparation passes. Existing output
   caches may be reused only after source comparison.
2. Finish tools and source validation and commit release notes following the
   [release-note style](releases.md#release-note-style): terse and factual, with
   new features first, then bug fixes and security changes. Keep each paragraph
   and list item on one source line; allow natural line wrapping. Fetch remote
   branches and tags, then run `scripts/release/reserve.py --version VERSION
   --prepared-report PREPARED_REPORT`. The command requires completed zero-fuzz
   preparation, matching component inputs and browser-lock hash, and the unchanged
   preparation log before it can write a version record.
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
5. Exercise the real About-page updater from the latest published release to the candidate
   with `scripts/release/check_update.py --expected-build VERSION`. Run both
   architectures sequentially, including invalid-signature and unsupported-OS
   rejection cases. Retain before/after profile and signature evidence. The legacy
   integer-version build-2 migration is no longer a recurring release requirement.
6. Use `scripts/release/delivery.py --arm64 CANDIDATE --x86-64 CANDIDATE --output
   PUBLICATION --evidence ACCEPTANCE_JSON` to create matching feeds, one immutable DMG per architecture,
   release metadata, reviewed validation evidence and checksums. Source is retained
   in the public Git repository; source-kit export is not a release prerequisite.
7. Retain a signed annotated `v<VERSION>` source tag at the exact frozen source
   commit and push it and all permanent component input refs to the public source
   repository. Use `python3 scripts/release/run_publisher.py upload --source-checkout FROZEN
   --directory PUBLICATION --notes-file NOTES`. It checks anonymous source access
   and exact ref targets, then creates an unpublished, non-prerelease draft and
   uploads only browser delivery files and compact metadata. GitHub asset digests
   must match. Keep upload-receipt.json; promotion rechecks every uploaded asset
   and the public source refs. No asset is overwritten or dependency archive copied.
8. Record acceptance on one physical device against the version, source commit and exact DMG hashes. Both architectures must pass the software checks; Intel may run under Rosetta on the accepted Apple silicon Mac. Do not wait for manual Intel testing, another owner confirmation or a deferral. Additional hardware/OS checks are optional follow-up.
9. After single-device acceptance and all technical gates pass, publish the authorized release using `python3 scripts/release/run_publisher.py promote --channel stable --source-checkout FROZEN` with the publication directory, acceptance JSON and public checkout. Acceptance and a fresh Chromium lookup pass before it undrafts the final release. It verifies anonymous immutable downloads, rechecks freshness, commits
   both stable feeds, then marks the release latest. Verify both raw feeds,
   both latest download links, the release page and public HTTPS installed updates,
   then verify the website resolves through those latest links. Deploy the website only when its source changes. If a step fails, preserve existing feeds and resume
   the same verified bytes; do not create a prerelease as a workaround.

Release tags now belong to the source repository and identify the frozen source
commit directly; release.json records its full SHA. Keep builds 1 and 2 and their source unchanged.

## Recovering from preparation failures

Stop the failing pipeline and retain its log and rejected hunks. Inspect the upstream change and make a focused, reviewed adaptation in the prepared source with quilt; refresh and unmerge it into the owning component. Preserve each feature's intended behavior and the complete ordered series. Record context/API adaptations and new component identities, run component patch/translation lint, then repeat complete preparation in a new source tree. A repaired partial replay is useful evidence but does not satisfy the fresh-preparation gate or permit version allocation.

Use zero fuzz and the same whitespace matching as upstream preparation (`--fuzz=0 --ignore-whitespace`) when replaying with quilt. Unified-diff blank context lines require their leading space; globally stripping trailing whitespace from patch files can make the inherited parser reject otherwise applicable patches. Use the inherited patch lint for patch-content whitespace and syntax, and ordinary whitespace checks for the other changed files.

Generated files must be available at the phase where a patch expects them. Onboarding's `src/lib/strings.ts` is generated from `helium_onboarding_strings.grdp` after the patch/substitution/resource pipeline. Prefer changing the canonical XML and letting that generation step produce the module. When repairing a patch that also edits generated output, first prove byte-for-byte equivalence between its generated-output edits and regeneration from its canonical inputs; retain that proof before removing redundant generated hunks. Verify another complete clean preparation without a pre-existing generated module.

Once a release is frozen, make operational documentation updates on main rather than editing its hash-locked checkout. Continue builds and packaging from the frozen commit and pass that checkout through `--source-checkout` to the publisher. Changes to frozen build inputs or recipes require a new allocation; later runbook clarification does not rewrite the existing release record.

If a validation helper rejects an intentional, already accepted UI, retain the failure and establish the assertion defect against the owning source and retained baseline. Correct the helper separately on main and run it against the unchanged candidate, recording the supplemental tool commit/hash and exact candidate identity. Preserve the original frozen helper and report; a corrected assertion must still verify the required behavior. A browser defect or changed build input requires the normal repair and new-allocation process.

## Optional manual Intel compatibility checklist

The owner has two native Intel Macs running macOS 13.7.8 and 26.6.2, confirmed
on November 9. The 13.7.8 machine exercises the older-system glass fallback;
26.6.2 exercises the native glass path. These are optional follow-up test environments, not publication gates or completed acceptance results. Single-device acceptance is sufficient; do not delay publication for these checks or request a deferral. Use the
candidate's Intel DMG on each test Mac. Record model,
macOS version, downloaded filename/hash and whether Rosetta is involved (native
Intel is required here). Drag Lune to Applications and launch normally through
Finder, without bypassing Gatekeeper. Verify About shows the release version and
Chromium version, then visit public HTTPS sites, use tabs/sidebar/settings, quit
and reopen, and confirm saved preferences and a test bookmark survive.

For the update check, start from the latest published Intel release in a
separate install location/profile, select the provided loopback test server, enable
browser updates, and use About → Check for Updates. The local fixture serves the
exact final signed DMG, with only its test enclosure URL changed; the production
app and signed archive retain the stable feed configuration. Confirm the offered version,
install/relaunch, and preserved test data. Do not run baseline and candidate
updater sessions concurrently. Report any crash, blank window, signing warning,
or failed update before stable promotion.

### Portable loopback fixture

For an explicit native-update test, prepare a local folder containing `manual_update_fixture.py`, the candidate publication manifest/DMGs/appcasts and an unchanged earlier Intel baseline. Use ordinary release downloads; no separate Intel test release or permanent test-kit upload is required. The helper
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

Keep that terminal open. Copy the earlier baseline from its DMG into a new `update-test`
folder using Finder, keeping the app named Lune.app. Quit other Lune instances.
In another terminal, launch that copy with a new disposable profile and the
local base URL printed by the helper:

```sh
open -n -a "$PWD/update-test/Lune.app" --args \
  --user-data-dir="$PWD/update-profile" \
  --custom-update-server-url=http://127.0.0.1:PRINTED_PORT/
```

Enable browser updates in Settings, save a test bookmark and preference, then
use About to install the update and relaunch. Confirm the candidate version from `release.json`, public browsing,
and the saved data after relaunch. Quit the test app before stopping the server.
Use a second, fresh copy/profile of the baseline for the negative case:

```sh
python3 manual_update_fixture.py --directory publication --arch x86_64 \
  --case wrong-architecture
```

On native Intel, About must decline this Apple silicon offer and retain the baseline.
The feed retains `hardwareRequirements=arm64`; only its test route is named for
Intel so the Intel updater can inspect and reject it. Apple silicon/Rosetta
cannot establish this hardware-rejection result. Record both outcomes and any
error text with the candidate DMG hash. These instructions are prepared;
owner-run native Intel results remain pending.

## Completion after validated delivery

Apply the [commit and completion process](committing.md): close issues resolved by the delivered change, quit temporary test browsers and update-fixture servers, and delete disposable installed-app copies, profiles and packaging intermediates. Retain immutable published assets, frozen inputs and the required release/update/signature evidence. Record cleanup without changing signed release bytes or frozen records.

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
      "native_hardware": false
    }
  }
}
```

Rosetta may establish the Intel row's pre-publication software checks; record
that execution mode explicitly and leave native_hardware false. Stable requires at least one architecture row with native_hardware true and both rows passing all software checks. No manual Intel result, owner_confirmation field or deferral is required. Include report hashes and concise test results as additional fields
so the booleans can be audited. The validation.json uploaded with the draft
is immutable; later hardware acceptance is recorded separately in the promoted
feed commit. Do not overwrite the original candidate evidence.

## Focused release uploads

New release staging includes these files in `Lune.app/Contents/Resources/` before signing:

| Repository source | Packaged filename | Scope |
| --- | --- | --- |
| `LICENSE` | `LICENSE.txt` | Lune's original work, GPL-3.0-or-later as granted in `NOTICE`. |
| `NOTICE` | `NOTICE.txt` | Copyright, license scope, upstream attribution, and source location. |
| `LICENSE.helium` | `LICENSE.helium.txt` | Helium's GPLv3 text, preserved from the locked upstream input. |
| `LICENSE.ungoogled_chromium` | `LICENSE.ungoogled_chromium.txt` | ungoogled-chromium's BSD 3-Clause notice, preserved from the locked Helium upstream input. |

Keep the source filenames consistent with Helium's convention; `.txt` makes app
copies easy to open in Finder. Preserve the original license text and copyright
notices. These files supplement upstream notices and `chrome://credits`; they do
not replace them. Verify all four files in the signed app. The installed app retains
them after the DMG is discarded, and the DMG includes them through that app bundle.
The optional local source export includes the same files under their source names:
`LICENSE`,
`LICENSE.helium`, `LICENSE.ungoogled_chromium`, `NOTICE`, and `README`.
Existing signed releases and frozen source tags remain unchanged.

The source repository is public. Publish one DMG per architecture, architecture appcasts, checksums and compact release/validation metadata. Release-tag and latest download URLs reference the same asset. Link the exact signed public source tag and permanent component refs.
Do not re-upload Git history bundles, source kits, or unchanged source/dependency
archives merely to duplicate what the public repository and recorded immutable
URLs already provide. Verify source reachability and hashes; preserve existing
published assets and licenses. The owner explicitly selected this approach while
publishing 26.1109.2. Redundant source assets were removed from the unpublished draft. On November 10, the owner also requested removal of duplicate version-named DMGs from both published releases, retaining identical signed bytes under stable filenames and updating appcasts/checksums first. The frozen source tags and browser bytes remain unchanged.

The active upload command enforces this focused asset set. `scripts/release/source.py`
remains an optional local export utility for an explicit request, not a routine
production gate. Source availability is required; duplicate archive uploads are not.
