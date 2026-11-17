# Development browser builds

Use the [development loop](development.md) for feature iteration and adoption. This runbook covers locked-input builds. For production use the [release runbook](release-delivery.md) from the frozen checkout.

`manifests/browser.lock.json` pins the engine, components, toolchain and archive manifests. `manifests/patches.json` pins reviewed patch provenance and order. Keep Lune's bundle/profile identity, Keychain identity, update URLs and Helium service preferences separate from reusable patches. See [architecture](architecture.md).

## Prepare this Mac

Install the Xcode, SDK and Metal versions pinned in `config/product.json`. The prerequisite check runs the Metal compiler. Use the existing Apple silicon Mac for both targets and compile them sequentially.

On a new host, install the pinned Xcode, complete first-launch setup, then:

```sh
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
xcodebuild -downloadComponent MetalToolchain
```

The 200 GiB threshold applies before source preparation; compilation/resume
requires 80 GiB free after sources are present. Both are conservative safeguards,
not measured peak usage. The two architectures are built sequentially.

Measure reclaimed disk space on the actual filesystem because APFS clones share blocks. Follow [cleanup policy](committing.md#quit-temporary-builds-and-remove-their-artifacts) for preserved workspaces and caches. Record any approved preparation-floor exception, measured space and scoped inputs. Keep the pre-build floor and technical gates.

Small build dependencies are already installed on this Mac. On another Mac:

```sh
brew bundle --file=config/Brewfile
/opt/homebrew/bin/python3.13 -m venv .work/venv
.work/venv/bin/python -m pip install --require-hashes -r config/requirements-build.txt
```

The example Python path is for Apple silicon Homebrew; Intel Homebrew normally
uses `/usr/local/bin/python3.13`. The current wrapper's GNU patch path is for
this Apple silicon build host; adapt and validate host tooling before using an
Intel host. Both target architectures can be built on this Mac, but native Intel runtime
validation still needs an Intel machine. Homebrew's formula versions are not a
complete immutable toolchain lock; record exact Xcode/SDK/tools with the first
successful build before calling a release reproducible.

```sh
python3 scripts/lune.py validate --git-objects
python3 scripts/lune.py doctor
python3 scripts/lune.py checkout --arch arm64
python3 scripts/lune.py prepare --arch arm64
python3 scripts/lune.py build --arch arm64 --jobs 10
```

Repeat checkout/prepare/build with `--arch x86_64` for the Intel target. Each uses
an isolated `.work/<arch>/macos` clone. Checkout only downloads patch/config Git
repositories; prepare downloads Chromium and runs upstream pruning, strict patch
application, substitutions, localization, resources, version generation, and GN.
Build invokes upstream compilation, ChromeDriver, and installer tooling.

Start commands from the repository root. Preparation/build require committed
orchestrator changes, clean component checkouts, exact locked commits, and the
prerequisite check. Preparation refuses to reuse/delete an existing source tree.
Build requires its successful preparation record and unchanged lock, GN arguments,
and Xcode version. These checks do not attest to arbitrary manual changes inside
the generated source tree: use a fresh preparation for release validation.

This GitHub repository is public. Public source refs can be cloned anonymously. CI supplies the job's read-only
`GITHUB_TOKEN` through `gh` only for fetching/checkout; credentials are not stored
in the source tree, and browser signing credentials are never supplied to checks.

Prepared/built state is saved under `.work/<arch>/`; build outputs are inside the
platform's `build/src/out/Default/`. A successful compile must produce `Lune.app`.
`built.json` records `validated_for_release: false`. Nothing publishes automatically.

### Host-owned build storage

Disk layout is machine configuration, not a browser input. With no local storage configuration, existing `.work/<arch>` directories and compiler-cache defaults remain unchanged. An external build disk can be selected in `~/Library/Application Support/Lune Build/storage.json`; `LUNE_BUILD_STORAGE` can select another local configuration file. Never commit a host's configuration, UUID, paths or migration records.

The configuration schema is:

```json
{
  "schema_version": 1,
  "mountpoint": "/Volumes/BuildDisk",
  "volume_uuid": "00000000-0000-0000-0000-000000000000",
  "cache_root": "/Volumes/BuildDisk/BuildCache/lune",
  "sccache_dir": "/Volumes/BuildDisk/BuildCache/sccache",
  "sccache_cache_size": "200G"
}
```

Use the actual APFS volume UUID reported by `diskutil info -plist`, not the example UUID or a changing device identifier. Configured commands verify the mount, volume UUID, APFS filesystem, writable status and cache-path containment before creating workspace paths or starting build tools. A missing or renamed disk stops the command; there is no automatic fallback to internal storage. This preflight cannot protect an in-progress build from unplugging its disk.

New architecture workspaces are linked at the existing `.work/<arch>` paths, with separate external destinations derived from each checkout's absolute path. Interactive and CI checkouts never share mutable source/output directories automatically. Existing workspace directories are preserved; tooling does not move or delete them. Preparation/build disk floors are checked on the actual target filesystem, including release preparation and compilation. The clean build environment explicitly selects only the configured compiler-cache directory and capacity, without inheriting arbitrary shell variables or credentials.

Run `python3 scripts/lune.py storage` to inspect the selected storage. Before creating a new feature or release workspace, use `python3 scripts/lune.py storage --workspace <name>` to create its host-configured destination and `.work/<name>` entry path. On an unconfigured host this creates the ordinary local directory. Existing directories are left in place and the command prints their resolved location. Use an isolated name; this command does not establish workspace ownership or authorize sharing an active tree.

Migrate existing work in a coordinated maintenance window: inventory ownership and unpublished changes; stop source/build/cache writers; copy complete workspaces with metadata, Git/quilt bookkeeping, incremental outputs and downloads; verify file contents and metadata; retain internal originals; then replace the old workspace paths with symlinks. Check links and Git state and validate both architecture outputs plus an incremental rebuild before reclaiming any original. Copy the compiler cache with its server stopped and verify cache hits after selecting the new location. A host-local default sccache configuration can also cover frozen checkouts whose tooling predates storage support. Keep Xcode, Keychain, runner credentials and Python environments internal. Preserve frozen source and artifact bytes; storage migration does not waive release gates or make an earlier browser validation cover changed files.

Disposable browser profiles use [the shared profile allocator](../../scripts/browser_test_profiles.py). On macOS it creates private directories in `/private/tmp`, independently of build storage and `TMPDIR`. Sources, compiler caches, outputs, reports, logs and screenshots may remain on the configured external build disk. Browser-written diagnostic logs and browser-loaded extension fixtures also live inside the temporary profile; the host helper retains copies in the evidence directory. Installed-update checks also put their disposable app bundles on internal temporary storage and retain a verified evidence copy externally. Do not pass external `--log-file` or `--load-extension` paths to a disposable browser. Keep one allocated profile through all launches in a persistence test; the allocator removes it when the test process exits normally. Context-managed profiles also clean up on Python exceptions. Interactive checks keep their profiles until the review process ends. New browser checks must use this allocator rather than placing `--user-data-dir` beneath their evidence directory. This avoids removable-volume consent prompts caused by disposable development apps writing profiles to the build disk; it does not grant those apps additional macOS permissions.

The CI build script now runs the isolated headless smoke test after compilation:

```sh
.work/venv/bin/python scripts/smoke-browser.py .work/arm64/macos/build/src/out/Default \
  --arch arm64 --ui --internal-icons --settings --report .work/arm64/smoke.json
```

Use the matching `x86_64` path and `--arch x86_64` for the Intel artifact. The test
checks the Mach-O architecture, ChromeDriver version, and running browser's
Chromium version against the lock, then exercises local page loading, JavaScript,
profile persistence, defaults, onboarding recommendations, credits, and the icon.
For an explicitly reviewed integration workspace whose version differs from the
main lock, pass `--chromium-version` with that candidate's exact version. An
architecture or version mismatch fails. Reports include the test host architecture;
an Intel binary running under Rosetta does not establish native Intel validation.
`--headed` shows the test window but does not by itself test native controls.
`--internal-icons` verifies packaged internal artwork and helper icons against
the exact macOS component; use `--platform-commit` for a reviewed integration
candidate outside the main lock. `--settings` checks preference bindings and
flag filtering after a Chromium port. Both switches require `--ui`.

CI also audits source artwork and protected translations before compilation,
then runs `scripts/branding/check-runtime-credits.py` for French and German after
the smoke test. See [the branding checks](../../branding/README.md) for commands.
These use disposable profiles and process-local language overrides.

Ordinary CLI/CI workspaces use `.work/<arch>/`; frozen release workspaces use their own ignored directories and reports. Older integration workspaces belong to their dated evidence and must not be substituted for current inputs. The guards reject mismatched locks, sources and toolchains. Preserve existing source trees/caches when preparing a new composition.

### Reuse outputs after fresh release preparation

Use `scripts/release/prepare.py --platform PLATFORM --report PREPARED_REPORT --cache-source IDLE_DONOR_SRC --cache-report CACHE_REPORT` to seed both architecture outputs after successful fresh preparation. For an already prepared tree, use `scripts/release/cache_reuse.py --source FRESH_SRC --cache-source IDLE_DONOR_SRC --prepared-report PREPARED_REPORT --report CACHE_REPORT --arch arm64 --arch x86_64`. Select a trusted donor with compatible compiler, Siso, GN, Rust and PGO hashes; keep its workspace idle throughout the operation. The donor is read-only, and existing destination outputs are never overwritten. Never copy an output directory by hand as a substitute.

The transfer compares source bytes and symlinks, restores timestamps only for identical source files, snapshots outputs with APFS clones when available, and relocates both native Siso file state and the separate `.siso_deps` Ninja dependency database. A copied `.siso_fs_state` alone leaves absolute compiler-header paths in the old workspace and can invalidate tens of thousands of objects. Legacy Clang resource-header aliases are recovered only when cached header digests match the fresh source inventory; unknown source roots, malformed dependency logs and incompatible toolchain inputs fail closed. Changed source bytes keep fresh timestamps. The outer `Lune.app` is assembled again.

An interrupted transfer leaves `out/.lune-cache-transfer-pending`; release builds refuse compilation until it is resolved. Preserve the failed workspace and report while investigating. Before every release compile, the build helper runs a native Siso dry run and retains its plan/explanation. Missing absolute dependencies outside the current workspace stop the build before expensive compilation. Inspect the cache-preflight log before choosing a deliberate cold build in a new output workspace. Engine, PGO, toolchain, GN command and real source changes can still require substantial rebuilding; output reuse does not waive source inventories, architecture checks or release acceptance.

## Discover upstream changes

```sh
python3 scripts/lune.py fetch
python3 scripts/lune.py discover
```

Fetch preserves unrelated refs and rejects moved tags. Discovery compares Chromium Stable separately from downstream releases and checks ungoogled ancestry. Reviewed integration updates the lock. See [architecture](architecture.md) for ordering and [completion](committing.md) for push rules.

## CI without additional spending

Use the repository-scoped `lune-mac-mini` runner with the `lune-build` label. `browser.yml` is manual. `checks.yml` and `website.yml` also run for matching main pushes. All use owner/main/canonical-repository guards and the `lune-browser-local` concurrency group. Keep fork and PR code off the signing host and large caches on disk.

Start an approved job with `./.work/ci-runner/run.sh --once`, or keep the runner available for a reviewed batch. Runner credentials and browser/build caches stay under the ignored runner directory. Setup and website use separate checkouts. Browser jobs use caffeinate and a six-hour timeout. A timed-out build can resume from a valid preparation. Inspect partial preparations before retrying.

See the [first arm64 build evidence](builds/2026-11-05-arm64.md) for bootstrap results.

### Local validation and inherited workflows

The `Development browser` dispatch now accepts `operation=validate` or `build`
(default). Both use the same pinned inputs, runner, and concurrency group.
Validation runs patch/translation checks, source preparation, strict patching,
substitutions, resources, GN generation, onboarding/UI checks, and source artwork
checks. It stops before compilation. Build additionally compiles and runs the
existing smoke and attribution checks. A reused preparation must still match the
lock, architecture, GN arguments, and Xcode; mismatches fail without deleting it.

```sh
gh workflow run browser.yml --ref main -f arch=arm64 -f operation=validate
./.work/ci-runner/run.sh --once
```

Repeat deliberately for `x86_64`; neither mode establishes native Intel acceptance.
Validation requires the same preparation disk/toolchain prerequisites as a build.
This does not install a runner service or enable recurring builds.

Setup checks validate the lock and recursive component checkout, run tests and component lint, and audit the live workflow registry. Keep `ci.yml`, `lint.yml` and `sanity.yml` disabled in GitHub, including for immutable component/input refs. Before publishing new component refs, inspect their workflow paths. Review and disable newly registered inherited workflows before further pushes. Check the registry with `python3 scripts/check-actions-policy.py` and use `gh workflow disable WORKFLOW --repo leebyron/lune-browser` for an identified inherited workflow.

The local translation audit checks pinned additions against the registry. Source coverage is advisory per [issue #4](https://github.com/leebyron/lune-browser/issues/4). Patch and translation-file lint remain blocking. See the [string review](features/string-review.md) for the rationale and accepted fallback scope.

## Signing readiness

Use the existing Developer ID Application identity and Sparkle Keychain key for `computer.lune.browser`. Read public identities from `config/product.json` and the pinned recipe. Use `xcrun notarytool history --keychain-profile lune-notary` on the unlocked Mac to verify notarization access. Keep credentials in Keychain.

The setup script omits `--keychain`, so notarytool stores this profile in the data protection Keychain, displayed as iCloud or Local Items in Keychain Access. This is distinct from the file-based login Keychain. Apple documents this [notarytool default](https://developer.apple.com/documentation/technotes/tn3147-migrating-to-the-latest-notarization-tool#Save-credentials-in-the-keychain) and [item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility): the default accessibility requires the device to be unlocked. A failed lookup while the Mac is locked does not establish that a saved profile was deleted. Unlock the Mac and retry the existing profile before requesting credential re-entry. An explicit `--keychain ~/Library/Keychains/login.keychain-db` query searches a different store and cannot confirm the absence of the default profile. The `security` CLI primarily inspects file-based Keychains.

If the Mac is already unlocked and the default lookup still fails, open Keychain Access, select iCloud or Local Items, and search for `com.apple.gke.notary.tool`. The existing profile's Account is `com.apple.gke.notary.tool.saved-creds.lune-notary`. Inspect metadata with the password hidden, then retry `xcrun notarytool history --keychain-profile lune-notary`. Record the actual command's successful authenticated response and exit status before declaring notarization ready; a visible saved item or installed notarytool executable does not satisfy this check. Do not delete, move, duplicate or recreate a visibly existing profile merely to address a failed lookup.

A previous locked-console failure cleared immediately on unlock without credential changes. See the [26.1113.1 release record](builds/2026-11-13-release-26.1113.1.md).

Only if the existing profile remains unavailable after an unlocked retry and inspection of its actual store, confirm the need to provision or restore it using an app-specific password from
[Apple Account](https://account.apple.com/), then run this in an interactive terminal:

```sh
./scripts/setup-notary.sh
```

It prompts for the Apple Account email, delegates the secure password prompt to
`notarytool`, validates with Apple, and saves Keychain profile `lune-notary`. Do not
paste the password into chat or put it in a command-line flag, repository file,
or shell history. The ordinary Apple Account password is not the app-specific
password. No browser is submitted by this setup command.

The clean build environment excludes credential variables. Keep arbitrary untrusted jobs off the host because local code can still reach the login Keychain.

## Validation scope

Lock validation checks pins and Git provenance. Preparation checks the full source pipeline. Runtime results apply to the exact tested build and execution mode. Use [release delivery](release-delivery.md) for packaging, signing and installed-update evidence.
