# First signed release and updater bootstrap

Status: public prereleases and staging feeds are live. Stable promotion awaits acceptance.

## Decisions

- Setup validation and website deployment now run on `lune-mac-mini`, alongside
  browser compilation. All jobs use the `lune-browser-local` concurrency group,
  owner/main/private-repository guards, and no PR events. Keep the runner off
  except for reviewed jobs; the Mac holds signing credentials.
- Both jobs passed on the Mac for main commit `b60fdf05087b793bbb52870edb1ac4621a3bfd8f`:
  [setup](https://github.com/leebyron/lune-browser/actions/runs/42241516555) and
  [website](https://github.com/leebyron/lune-browser/actions/runs/42241516446).
- The owner has an Intel Mac for manual acceptance; it will not join CI.
- Use **Helium-hosted services** for this release, per the owner's correction.
  Default origin is `https://services.helium.imput.net`. Onboarding and settings
  identify Helium as the provider. Lune remains responsible for browser updates.
  Do not activate the separate unfinished services deployment merely to release.
- Host appcasts at `https://lune.computer/updates/stable/mac/appcast-arm64.xml`
  and `appcast-x86_64.xml`. Keep staging appcasts under `/updates/staging/`.
  The app embeds its architecture-specific stable feed and uses Helium's
  service-consent preferences and custom-update-server flag.
- The private source repository cannot provide anonymous GitHub downloads.
  Public distribution repository: `leebyron/lune-downloads`, containing
  release assets and corresponding source/provenance. Do not change the private
  repository's visibility or publish unrelated local files.
- Reserve numeric bundle builds 1 and 2 in `config/release-builds.json` for the
  two-version installed-update exercise. Set only the outer app's CFBundleVersion
  during staging, before signing; set its display version to the locked Chromium
  version. Preserve nested framework versions and paths.
  After publication, never reuse a build number or overwrite its artifacts.

## Candidate inputs and checks

Core remains `fd5342cd999dcc9e4d9083cf54182d00e73e7a5d`, Chromium 158.0.8127.18.
Platform candidate `ae265118c1e0c0842b5cc0ce65b92e483e4547ac` adds two separate
branding/distribution commits:

- `d66759424d27b03f71072f69b03e4cdb8f076136`: Lune Sparkle URLs, GN feed setting,
  correct plist boolean types, and accurate Sparkle 2.10.1 metadata.
- `ae265118c1e0c0842b5cc0ce65b92e483e4547ac`: Helium hosted origin, provider
  disclosures, and preservation of service names in translated messages.

Fresh preparation from all pinned archives passed without fuzzy patching. The
prepared tree is `.work/release-bootstrap/platform/build/src`. Source comparison
and refresh evidence lives under `.work/release-bootstrap/`; 165 changed GRIT and
XTB files were copied into the existing build tree to retain its compiler cache.
The remaining source contents match the independently prepared tree. Generated
outputs, quilt metadata, and Python caches are excluded from that comparison.
The arm64 rebuild passed in 6m44s; its full smoke test passes with provider
disclosures, settings, and artwork. Intel rebuilt in 7m05s and passes the same
checks under Rosetta. Both use Sparkle
2.10.1, the Lune public key, and a daily check interval. Earlier development apps did not include Sparkle.

The name-substitution regression passes, including provider names and the
existing 162 protected upstream-credit translations. Repository tests currently
include rejection of incomplete/mismatched artifacts and altered DMG bytes before
appcast generation. Runtime provider checks are added to `scripts/smoke-browser.py`.

The owner provisioned `lune-notary`; Keychain access was verified without
exporting credentials. The setup reminder is paused. Both candidate builds and
runtime checks pass. Both builds (1 and 2), on both architectures, now have
Developer ID signatures, accepted Apple notarization, stapled tickets, Gatekeeper
acceptance, notarized DMGs, and verified Sparkle signatures. Distribution
acceptance remains in progress.

Release GN overrides (in addition to the pinned platform release defaults):

```gn
enable_sparkle=true
include_branded_entitlements=false
sparkle_ed_key="J/aDOySmegpv5t6M/CtfFnlY0VSmVW5kdG7Y++HuJZw="
sparkle_automatic_checks=true
sparkle_check_interval=86400
sparkle_feed_url="https://lune.computer/updates/stable/mac/appcast-arm64.xml"
```

For Intel use `target_cpu="x64"` and `appcast-x86_64.xml`. The build uses
`chrome_pgo_phase=2`, `cc_wrapper="sccache"`, and the pinned Xcode toolchain.

## Packaging commands

`scripts/release/package.py` has independent `stage`, `sign`, and `package`
commands. Stage requires a successful matching build report, locked platform,
matching GN arguments, correct architecture, Lune identity/key/feed, and a
reserved release number. Runtime smoke evidence must match the app executable
and framework hashes. It creates a new directory and never replaces one.

Signing uses the generated Chromium nested-signing machinery and the existing
Developer ID. The pre-notarization Gatekeeper assessment is deferred until the
stapled app exists, when it becomes mandatory; hardened runtime signing and
signature verification stay enabled. The DMG contains Lune.app and an Applications
symlink, uses UDZO, is signed, notarized, stapled, and assessed independently.
Sparkle signs the final bytes only after these steps pass.

`scripts/release/appcast.py` generates a local feed from successful package
metadata and verifies the recorded DMG hash/size. It does not publish or deploy.
An ARM64 item additionally declares Sparkle's arm64 hardware requirement. Separate
feeds remain the primary architecture-routing mechanism.

## Remaining gates

- Perform native Intel acceptance manually on the owner's Intel Mac.
- Before stable promotion, apply the
  [macOS Chromium freshness gate](../releases.md#chromium-freshness-gate), record
  the current comparison and any explicit known-lag exception, and confirm all
  acceptance evidence. Unknown freshness blocks promotion. Promote both stable
  feeds and website links together.

No recurring browser build or automatic public promotion is enabled by this work.

## Signed acceptance progress

The signed arm64 candidate passes runtime/settings/artwork and French/German
attribution checks. The signed Intel candidate passes the main runtime smoke
under Rosetta. Its installed build-1 to build-2 update also passes, including
relaunch, profile persistence, and post-install signature/Gatekeeper checks.
An initial concurrent updater test stalled; the isolated sequential run passed.
Run browser acceptance checks sequentially because Sparkle also uses per-bundle
macOS preferences/cache/installer state outside Chromium profiles. Intel live-service
and French/German signed-app checks also pass.
The arm64 live-service check fetched 10,730 valid bangs and loaded 676,593 uBlock
network filters. The advertising fixture was replaced with uBlock's local stub.
The arm64 signed app installed EFF Privacy Badger 2026.9.15.2 from its official
Web Store listing in a disposable profile with Helium services enabled. The
extension appeared enabled and its first-run page opened; the Extensions page
reported "Extensions updated" after its update check. The same Web Store install and update check also pass on Intel under Rosetta.
A transition between two extension versions has not been exercised.

The actual Lune About-page updater completed a local staged build-1 to build-2
update on arm64, then relaunched with profile data intact. The installed result
passes codesign, stapler, and Gatekeeper again. A deliberately invalid Sparkle
signature was rejected and an item requiring macOS 99 was not offered; both
kept build 1 and its profile intact. These initial checks used loopback test feeds; the later public HTTPS tests
also pass, as recorded below.

The standalone Sparkle CLI was built from the pinned source but required macOS
authorization to replace the test bundle. The acceptance harness therefore uses
Lune's real About-page updater, including its consent and custom-feed behavior.
It is `scripts/release/check_update.py`; `--expect-rejection` runs negative cases.

The public distribution repository now exists at
https://github.com/leebyron/lune-downloads. Builds 1 and 2 are public prereleases.
Build 2 includes the source kit, all six pinned dependency archives, locks, patch
provenance, validation evidence, and checksums. No stable feed has been promoted.

Inherited hosted component workflows (`ci.yml`, `lint.yml`, `sanity.yml`) were
disabled through GitHub's workflow API; their histories remain unchanged. Their
platform-tag runs had been blocked by billing. Main setup validation remains on
the Mac and passed again for commit `7784f488`.

## Publication approval

The source kit and public metadata are prepared under
`.work/releases/public-build-2/`. Automatic approval review rejected uploading
private-repository-derived source/locks/provenance to the public download repo
without explicit authorization for that payload and destination. The owner
explicitly approved publishing that prepared source package to
`leebyron/lune-downloads` build 2. All assets are now published; the private source
repository remains private. Uploaded SHA-256 digests match every recorded asset.
Anonymous downloads of all four DMGs and the source kit also match local hashes.

## Public staging delivery

The staging feeds were deployed from commit `63e747be352c8d0cd6d0fa5731308a90cfe2f055`
by the Mac runner: [successful website job](https://github.com/leebyron/lune-browser/actions/runs/42253353992).
Both HTTPS readbacks exactly match committed XML and use RSS content type,
five-minute cache control, and `nosniff`. They reference immutable build-2 DMGs.

- [Build 2 candidate and sources](https://github.com/leebyron/lune-downloads/releases/tag/build-2)
- [Build 1 update-test baseline and manual instructions](https://github.com/leebyron/lune-downloads/releases/tag/build-1)
- [Apple silicon staging feed](https://lune.computer/updates/staging/mac/appcast-arm64.xml)
- [Intel staging feed](https://lune.computer/updates/staging/mac/appcast-x86_64.xml)

The public About-page update passed build 1 → 2 on both arm64 and Intel under
Rosetta, including relaunch, profile persistence, and post-install
signature/stapling/Gatekeeper verification. The Intel test started from the
anonymously downloaded baseline DMG. Native Intel acceptance is requested from
the owner; Rosetta results do not substitute for that hardware check.

Additional delivery and extension evidence is published as
`public-delivery-evidence.json` with its own checksum file. Previously published
artifacts and evidence remain unchanged. The source kit records orchestrator
commit `c191f0a9e3258584fa41fe7f6eb65fa6c257452c`; later changes only add feed
hosting and acceptance records, not browser binary inputs.
