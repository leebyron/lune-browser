# GitHub download and update delivery

Use [release policy](releases.md) for gates and [release commit boundaries](release-commits.md) for freezing and promotion. Build and package from the frozen checkout. Use the normal configured shell for `python3 scripts/release/run_publisher.py`, with `--source-checkout` identifying the exact frozen commit. The launcher prioritizes macOS tools and retains GitHub, GPG and SSH authentication. A missing `GNUPGHOME` can hide the configured key. Compilation uses the clean build environment.

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

Constrain every publication push explicitly, including pushes inside the publisher. Use `git -c push.followTags=false push origin HEAD:refs/heads/main` for the feed commit. Publish each selected input/source tag with `-c push.followTags=false` and its exact `refs/tags/NAME:refs/tags/NAME` refspec, in core, platform, then source-tag order. A configured `push.followTags=true` can otherwise publish historical annotated local tags reachable through the new main history. Inspect the remote-ref delta after publication and record any unexpected refs; preserve published source and input tag targets.

Versions 26.1109.1 and 26.1109.2 retain the retired distribution URL in their signed apps. Install a current release manually to regain updates. The project uses the canonical URLs above for all new delivery.

## Preflight before a long build

Use an input-named workspace and keep the generated checks and logs together. Run these read-only checks before expensive preparation. Record the selected lock and evidence paths once.

```sh
python3 scripts/lune.py doctor
python3 scripts/release/check_host.py
python3 scripts/release/freshness.py --chromium CHROMIUM --output EVIDENCE/freshness-selection.json
xcrun notarytool history --keychain-profile lune-notary
```

Run notarytool with the Mac unlocked and retain the authenticated result. Use [Keychain recovery](building.md#signing-readiness) for an unsuccessful lookup. Resolve host toolchain and Python package mismatches against the pinned recipe before preparing. See [storage floors](building.md#prepare-this-mac) for disk space and [cache reuse](building.md#reuse-outputs-after-fresh-release-preparation) for a compatible idle donor.

Use a release checkout with its own `.work/venv` or link that path to an existing environment verified against the same recipe. Provision a fresh environment using the Python version in `config/release-recipe.json` and `pip install --require-hashes -r config/requirements-build.txt`. Keep preview-only dependencies in the development environment.

Isolate ordinary fixtures with `--custom-update-server-url=http://127.0.0.1:1/`. Chromium networking flags leave native Sparkle networking active. Verify app/framework identity before and after testing. Canonical-feed and stock-update checks use production settings. Keep disposable profiles, browser-written logs, loaded extensions and update-test app copies internal using the [build runbook](building.md#host-owned-build-storage). Host helpers retain reports and verified copies in the evidence directory.

## Commands and gates

1. Prepare the reviewed, committed inputs in an isolated tree with `scripts/release/prepare.py --platform PLATFORM_CHECKOUT --report PREPARED_REPORT`. Use its paired `--cache-source IDLE_DONOR_SRC --cache-report CACHE_REPORT` options, or [transfer compatible outputs](building.md#reuse-outputs-after-fresh-release-preparation) after preparation. Retain archive verification, the zero-fuzz log and the full source inventory. Wait for preparation to finish successfully before selecting or reserving the version. Draft notes outside the checkout while preparation runs.
2. Fetch remote branches and tags and serialize allocation. Put the [release notes](releases.md#release-note-style) in `agent-docs/project/releases/VERSION.md` and stage that path. Run `scripts/release/reserve.py --version VERSION --prepared-report PREPARED_REPORT`, then stage `manifests/releases/VERSION.json` and commit both together. The command checks the completed report, component inputs, browser lock and unchanged preparation log. Use the clean frozen commit for both builds.
3. Run `scripts/release/build.py --version VERSION --arch ARCH --source SOURCE
   --prepared-report REPORT --report BUILD_REPORT` for each architecture. It
   verifies clean frozen inputs, source hashes, tools and GN arguments before
   compilation, runs a native cache-preflight dry run that rejects missing
   dependencies in old workspaces, and verifies source hashes again afterward. Include chrome,
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
   The runtime probe explicitly confirms the local blocker through custom setup with the other Services choices off, verifies bundled filters before and after restart, and checks the persisted setup-completion flag. Its default loopback feed override isolates ordinary runtime validation; the separate canonical-feed probe verifies the embedded production feed without an override.
5. Use `scripts/release/check_update.py --baseline-dmg BASELINE --driver DRIVER --feed FIXTURE_URL --arch ARCH --directory EVIDENCE_DIR --expected-build VERSION` to test the latest published version updating through About. Run both architectures sequentially. For the rejection cases use the invalid-signature and unsupported-OS fixture feeds and matching `--expect-rejection signature` or `--expect-rejection unsupported-os`. Retain the generated before/after profile and signature results. Use the [portable fixture](#portable-loopback-fixture) for the native Intel wrong-architecture case when testing on that hardware.
6. Use `scripts/release/delivery.py --arm64 CANDIDATE --x86-64 CANDIDATE --output
   PUBLICATION --evidence ACCEPTANCE_JSON` to create matching feeds, one immutable DMG per architecture,
   release metadata, reviewed validation evidence and checksums. Source is retained
   in the public Git repository; source-kit export is not a release prerequisite.
7. Retain a signed annotated `v<VERSION>` source tag at the exact frozen source
   commit and push it and all permanent component input refs to the public source
   repository. Use `python3 scripts/release/run_publisher.py upload --source-checkout FROZEN
   --directory PUBLICATION`. It reads the notes from the frozen checkout and creates an unpublished, non-prerelease draft after verifying public source refs. Keep `upload-receipt.json` for promotion's asset digest and source checks.
8. Record acceptance on one physical device against the version, source commit and exact DMG hashes. Both architectures must pass the software checks; Intel may run under Rosetta on the accepted Apple silicon Mac. Do not wait for manual Intel testing, another owner confirmation or a deferral. Additional hardware/OS checks are optional follow-up.
9. After acceptance and the technical gates pass, promote and capture anonymous public readback.

   ```sh
   python3 scripts/release/run_publisher.py promote --channel stable --source-checkout FROZEN \
     --directory PUBLICATION --acceptance ACCEPTANCE_JSON --checkout PUBLIC_CHECKOUT
   python3 scripts/release/readback.py --channel stable --directory PUBLICATION \
     --output EVIDENCE/public-readback.json
   ```

   The publisher checks freshness before undrafting, verifies anonymous immutable downloads and rechecks freshness before committing both feeds and marking the release latest. The readback report checks both feeds and both immutable/latest DMG paths against the manifest. Also verify the release page and notes, installed updates over public HTTPS and the website's latest links. Deploy the website when its source changes. For a partial promotion, resume with the same verified bytes and retain failed readbacks.

## Recovering from preparation failures

Stop the failing pipeline and retain its log and rejected hunks. Inspect the upstream change and make a focused, reviewed adaptation in the prepared source with quilt; refresh and unmerge it into the owning component. Preserve each feature's intended behavior and the complete ordered series. Record context/API adaptations and new component identities, run component patch/translation lint, then repeat complete preparation in a new source tree. A repaired partial replay is useful evidence but does not satisfy the fresh-preparation gate or permit version allocation.

Use zero fuzz and the same whitespace matching as upstream preparation (`--fuzz=0 --ignore-whitespace`) when replaying with quilt. Unified-diff blank context lines require their leading space; globally stripping trailing whitespace from patch files can make the inherited parser reject otherwise applicable patches. Use the inherited patch lint for patch-content whitespace and syntax, and ordinary whitespace checks for the other changed files.

Generated files must be available at the phase where a patch expects them. Onboarding's `src/lib/strings.ts` is generated from `helium_onboarding_strings.grdp` after the patch/substitution/resource pipeline. Prefer changing the canonical XML and letting that generation step produce the module. When repairing a patch that also edits generated output, first prove byte-for-byte equivalence between its generated-output edits and regeneration from its canonical inputs; retain that proof before removing redundant generated hunks. Verify another complete clean preparation without a pre-existing generated module.

Once a release is frozen, make operational documentation updates on main rather than editing its hash-locked checkout. Continue builds and packaging from the frozen commit and pass that checkout through `--source-checkout` to the publisher. Changes to frozen build inputs or recipes require a new allocation; later runbook clarification does not rewrite the existing release record.

If a validation helper rejects an intentional, already accepted UI, retain the failure and establish the assertion defect against the owning source and retained baseline. Correct the helper separately on main and run it against the unchanged candidate, recording the supplemental tool commit/hash and exact candidate identity. Preserve the original frozen helper and report; a corrected assertion must still verify the required behavior. A browser defect or changed build input requires the normal repair and new-allocation process.

## Optional manual Intel compatibility checklist

The owner's Intel Macs cover macOS 13.7.8 and 26.6.2. For optional compatibility follow-up, install the exact Intel DMG in Applications through Finder and verify Gatekeeper, About, public browsing, tabs/sidebar/settings and persistence after restart. Record hardware, OS, artifact hash and execution mode. For update testing, use the same baseline and acceptance checks as the [release policy](releases.md#release-gates) with the portable fixture below.

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
lune_update_profile="$(/usr/bin/mktemp -d /private/tmp/lune-update.XXXXXX)"
open -n -a "$PWD/update-test/Lune.app" --args \
  --user-data-dir="$lune_update_profile" \
  --custom-update-server-url=http://127.0.0.1:PRINTED_PORT/
```

Enable browser updates in Settings, save a test bookmark and preference, then
use About to install the update and relaunch. Confirm the candidate version from `release.json`, public browsing,
and the saved data after relaunch. Quit the test app before stopping the server, then remove only the disposable directory named by `lune_update_profile`.
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

Use the [completion process](committing.md) for issue closure and disposable artifact cleanup. Keep the generated reports, receipts and readback together with the release evidence. The publisher's promotion record and GitHub release already record the routine public outcome. Report readback and cleanup in the task.

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

Verify all four notices in the signed app alongside upstream notices and `chrome://credits`. `scripts/release/source.py` is available for an explicit local source export. Publish the [asset set defined in release policy](releases.md#versioning-and-publication) with the signed public tag and permanent component refs.
