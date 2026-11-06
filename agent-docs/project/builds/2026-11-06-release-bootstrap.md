# First signed release and updater bootstrap

Status: in progress. No public browser download or feed has been promoted.

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
  Planned public distribution repository: `leebyron/lune-downloads`, containing
  release assets and corresponding source/provenance. Do not change the private
  repository's visibility or publish unrelated local files.
- Reserve numeric bundle builds 1 and 2 in `config/release-builds.json` for the
  two-version installed-update exercise. Set only the outer app's CFBundleVersion
  during staging, before signing; preserve Chromium version and framework paths.
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
Both architectures are being rebuilt with Sparkle enabled, the Lune public key,
and a daily check interval. Earlier development apps did not include Sparkle.

The name-substitution regression passes, including provider names and the
existing 162 protected upstream-credit translations. Repository tests currently
include rejection of incomplete/mismatched artifacts and altered DMG bytes before
appcast generation. Runtime provider checks are added to `scripts/smoke-browser.py`.

## Packaging commands

`scripts/release/package.py` has independent `stage`, `sign`, and `package`
commands. Stage requires a successful matching build report, locked platform,
matching GN arguments, correct architecture, Lune identity/key/feed, and a
reserved release number. It creates a new directory and never replaces one.

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

- Finish both release builds and rerun runtime/provider/artwork checks.
- Provision `lune-notary` using `scripts/setup-notary.sh`; the profile was absent
  when checked. A 30-minute reminder was requested and created.
- Sign/notarize/package both build numbers for both architectures.
- Install build 1, update to build 2 through staging feeds, relaunch, and verify
  profile persistence. Exercise bad signatures, OS constraints, and architecture
  routing. Perform native Intel acceptance manually on the owner's Intel Mac.
- Verify Helium services and extension/uBlock behavior with explicit disposable
  test-profile consent.
- Publish source/provenance and immutable downloads, read back anonymously,
  recheck Chromium stable freshness, then promote both feeds and website links.

No recurring browser build or automatic public promotion is enabled by this work.
