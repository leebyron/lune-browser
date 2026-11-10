# Development browser builds

Read [current status](status.md) for active inputs and release progress. The [development lock](../../manifests/browser.lock.json) defines current core/platform commits; a frozen release record and its source tag define release builds. Do not infer inclusion from an older feature report.

Main includes the accepted update menu and canonical Sparkle endpoint, preserving the native close controls, themed sidebar, startup default and older-macOS fallback fixes. Both development builds and smoke checks pass; Intel runtime uses Rosetta. Production signing and update tooling is operational. Physical Intel acceptance remains artifact-specific.

Use this runbook for development builds. For a production release, follow [release delivery](release-delivery.md), run commands from its frozen checkout and retain its preparation/build reports. Never edit an existing frozen source workspace to pick up a main-branch change.

## Tracked inputs

`manifests/browser.lock.json` pins component commits/trees/refs, the Chromium target and ungoogled provenance, product/build requirements, patch selections and host download manifests. Every source download has a fixed hash. `manifests/patches.json` records the reviewed full Helium stack, selected contributions and local adaptations; do not apply ungoogled twice.

The repository retains upstream-derived `component/helium`, `component/macos` and `component/services` histories plus permanent `inputs/*` tags. Bootstrap tags and dated feature tags are historical checkpoints, not aliases for current inputs. The platform gitlink must match the locked core. See [architecture](architecture.md) for the Git/patch boundary and [feature records](features/README.md) for scoped validation.

Lune identity uses bundle/profile `computer.lune.browser`, keychain service `Lune Storage Key` and team `RBC9EP7948`. Browser updates use the canonical GitHub feeds. Optional browser services deliberately use Helium's production endpoint; Lune service hosting is not deployed. Keep these identities and consent paths separate from reusable browser features.

## Prepare this Mac

The owner selected this Mac mini (M4 Pro, 64 GB RAM). Storage and toolchain pass
preflight. The wrapper requires at
least 200 GiB free before preparation, a conservative local policy rather than a
measured guarantee. Two source/output trees and peak build usage may require more.
Free space manually; the tooling never removes personal data or old workspaces.

The installed development toolchain is pinned to Xcode **27.2 (27B52)**, SDK
**27.2**, and Metal **27B47**. Helium CI uses Xcode 26.5; we reviewed the pinned
[Chromium SDK configuration](https://github.com/chromium/chromium/blob/157.0.8103.38/build/config/mac/mac_sdk.gni),
which includes Xcode 27 support, and its SDK minimum of 15. This permits a
development build. Arm64 compilation and headless smoke checks subsequently passed
with this exact toolchain. Both 158 builds and their smoke checks subsequently
passed; Intel runtime used Rosetta. Native Intel hardware and release validation remain open.
Future Xcode/SDK changes fail preflight until reviewed and repinned. The check executes the Metal compiler,
rather than merely locating the shim supplied by Xcode.

On a new host, install the pinned Xcode, complete first-launch setup, then:

```sh
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
xcodebuild -downloadComponent MetalToolchain
```

The 200 GiB threshold applies before source preparation; compilation/resume
requires 80 GiB free after sources are present. Both are conservative safeguards,
not measured peak usage. The two architectures are built sequentially.

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

## Discover upstream changes

```sh
python3 scripts/lune.py fetch
python3 scripts/lune.py discover
```

Fetch updates namespaced upstream refs, preserves unrelated local refs despite
global prune settings, and rejects moved tags. Discovery compares numeric stable
versions and checks ungoogled ancestry in Helium. It reports whether the locked
release is current; it does not change the lock or compose a new candidate.
A newer ungoogled release absent from Helium requires reviewed integration.
Reviewed PR ports are composed into the pinned macOS component. Validation checks
selection provenance, patch hashes, and series order. Arbitrary automatic PR
replay remains unimplemented. Discovery also reports independent Chromium stable
lag; having the newest ungoogled release is not sufficient.

Always push core inputs before platform inputs, then publish exact input tags
and the main lock. Use explicit push refspecs with `-c push.followTags=false` so
local global Git settings do not publish unrelated tags. Never force-push
published input tags or replace release artifacts.

## CI without additional spending

Owner decision, 2026-11-05: keep CI free; use this Mac when required. Target
GitHub Actions orchestration with a repository-scoped self-hosted macOS runner
on this Mac. The manual `Development browser` workflow is implemented in
`.github/workflows/browser.yml`; it targets the `lune-build` runner label.
Xcode and Metal preflight pass. Runner registration and job pickup are verified.
The [first arm64 CI run](https://github.com/leebyron/lune-browser/actions/runs/42138206769)
passed full source preparation (strict patching, substitutions, resources) and GN
generation. Compilation stopped at the onboarding string generator: Lune name
substitution emits an XML declaration, but the parser assumed the first node was
the document element. Platform commit `2300b549` adds `ignoreDeclaration: true`.
The exact failed command now passes, and `scripts/check-onboarding.py` verifies
all 79 messages generate identical header/TypeScript output with and without the
declaration. CI runs that regression check before compiling. A fresh source
preparation with the new locked patch was used for the
[successful retry](https://github.com/leebyron/lune-browser/actions/runs/42140697247).
It completed 57,716 actions in 2h21m29s and produced `Lune.app` and ChromeDriver.
The app's identity, arm64 architecture, headless page loading, JavaScript, and
local-storage persistence across relaunch passed; see [evidence](builds/2026-11-05-arm64.md).

[GitHub documents self-hosted runner compute as free](https://docs.github.com/en/actions/concepts/billing-and-usage).
GitHub-hosted compute and storage policies depend on repository/account settings;
the owner still requires this Mac and no additional CI spend. Keep large source trees, compiler caches,
and initial browser outputs on local disk; do not upload multi-gigabyte checkpoints
to Actions artifacts by default. Do not provision paid runners, purchase storage,
or assume an unverified account billing cap. Setup checks and website deployments now use this same Mac, without hosted
compute or Actions cache uploads. They run only for owner-triggered main-branch
pushes or manual dispatch in the canonical `leebyron/lune-browser` repository. PR events do not
run on the persistent signing host. All three workflows share the
`lune-browser-local` concurrency group. Setup/website checkout subdirectories are
cleaned independently; browser build caches are preserved. The runner must be
started for each job with `run.sh --once` or kept running for a reviewed batch.

The browser workflow is manual-only, restricted to the owner on `main` in the
canonical public repository. No fork or PR code runs on this signing host. Runner `lune-mac-mini` is scoped to this repository. The official
GitHub runner v2.338.2 archive was verified with SHA-256
`25a065af409ffa317ab4d5a3b614dd15fc9c40f2172bc1b35a1b1258e919a388`.
Runner credentials stay under ignored `.work/ci-runner/`; no service is installed
to start it automatically at login. Start it for one job with:

```sh
./.work/ci-runner/run.sh --once
```

Builds use the runner's separate checkout under `.work/ci-runner/_work/` and preserve
its ignored source/compiler cache between runs. Checkout uses the job's read-only
GitHub token through temporary credential-helper environment variables; build
steps do not receive that token. The workflow serializes builds, uses caffeinate
to prevent idle sleep, and limits each run to six hours. A timed-out compilation
can resume from the validated preparation record on the next dispatch. A failed
partial source preparation requires inspection and is never automatically deleted.
No pull-request workflow targets this Mac. For future unattended operation,
keep the Mac awake while jobs run, and retain local compilation caches. Use the
successful arm64 baseline for comparison when running the Intel target. Recurring
jobs still require explicit activation and the release gates described below.
The owner can keep using the GitHub Actions UI for triggering and reading logs,
but the Mac must remain online for jobs to execute.

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

Automatic setup checks now run the inherited core/platform patch-series lint and
translation-file lint on the exact recursively checked-out lock. They also audit
GitHub's repository-wide workflow registry with `scripts/check-actions-policy.py`.
Only `browser.yml`, `checks.yml`, and `website.yml` may be active. Unknown active
workflows fail the audit, as do missing/disabled local workflows. The audit is
detection, not a repository-wide hosted-runner prohibition.

The inherited `ci.yml`, `lint.yml`, and `sanity.yml` are disabled in GitHub for all
branches/tags. Keep them disabled: input tags are immutable, and imported ancestry
retains the original YAML. Merely changing `main` cannot change those snapshots.
Before publishing new component/integration/input refs, inspect their workflow
paths. A newly introduced path needs review and must be disabled in Actions as
soon as registered, before further pushes. Recheck with:

```sh
python3 scripts/check-actions-policy.py
gh workflow disable sanity.yml --repo leebyron/lune-browser
```

Use the disable command only for an identified inherited path. Do not re-enable
the old workflows or rerun their hosted failures. Their hosted setup changes
Spotlight, installs/force-links Homebrew packages, and uploads source caches;
the local entry point uses the already provisioned toolchain and local disk.
Patch application, substitutions, and GN are covered by local preparation. The
upstream Linux utility formatting/tests and generated pruning/domain-list audits
have not been ported; local validation does not claim equivalent coverage of
every job in upstream `ci.yml`.

The upstream i18n generator fetches moving Windows/Linux/macOS branches. Local
manual validation instead audits extracted additions from the pinned core/macOS
patches against the committed translation registry, retaining the last occurrence
of each resource/message pair. It does not regenerate Windows/Linux/onboarding
strings, model conditional variants, or remove stale entries.
The initial audit incorrectly blocked on **32 missing/different extracted entries**.
Review established 31 distinct IDs, one intermediate frame-label version, and the
integration's explicitly accepted English fallbacks. Source coverage is now
advisory and links to [issue #4](https://github.com/leebyron/lune-browser/issues/4);
patch lint and translation-file validation remain blocking. The clearer frame
label is restored in a new immutable input. See [the string review](features/string-review.md)
for the wording decision, provenance, validation, and remaining localization work.

Migration verification: all 42 orchestrator tests pass; core/platform patch lint,
translation-file lint, lock/ancestry checks, and the live Actions registry audit
pass. The queued [setup run](https://github.com/leebyron/lune-browser/actions/runs/42279065148)
was executed successfully on `lune-mac-mini` with the existing workflow. The new
workflow then [passed on the same Mac](https://github.com/leebyron/lune-browser/actions/runs/42281035175)
at commit `acda24dab34ca6b6bbcf8de3abd073ee6cb50388`, including the live registry
audit, all 42 tests, fresh recursive checkout, and core/platform input lint. The
manual validation path was checked through its early input failure; no fresh
Chromium preparation or build was run for this CI change.

On 2026-11-06 the hosted [setup-check run for the final 158 inputs](https://github.com/leebyron/lune-browser/actions/runs/42230439397)
did not start. GitHub reported that recent account payments failed or the spending
limit needs to be increased; no test step ran and no job log exists. This is an
account/hosted-runner limitation, not a repository test failure. The same setup
checks passed locally: all 33 tests, locked configuration, permanent refs,
ancestry/tree/gitlink validation, and a fresh recursive GitHub checkout. No billing
setting or paid capacity was changed. The completed local browser builds and
runtime checks are recorded separately in the 158 evidence document. Do not keep
retrying this hosted run as though it were a source failure; account resolution is
needed if hosted checks are to resume.

Stock GitHub-hosted macOS builds remain a possible future experiment. The pinned
[Helium workflow](https://github.com/imputnet/helium-macos/blob/37efe2c65dccc21aaf1d8ea66fd35d1348c386a8/.github/workflows/building.yml)
chains up to ten build phases with source/build artifacts to cross job time limits.
That is source evidence of its strategy, not proof that Lune will fit the repository's free compute/storage allowances. Do not copy its artifact-heavy
approach without measuring storage and runtime first.

## Signing readiness

The login Keychain contains a valid Developer ID Application identity:
`Developer ID Application: Judy Byron (RBC9EP7948)`; SHA-1 fingerprint
`A9233B3FC55405B87765E25A454F7D42187E61F2`. The owner approved this display name
for now. The Apple Developer ID G2 intermediate was imported from Apple's
certificate authority. The private key has not been exported to GitHub.

A dedicated Sparkle Ed25519 key was generated in Keychain under account
`computer.lune.browser`. Its public key is in `config/product.json`; never rotate
it casually or commit/export its private key as part of routine builds.
The downloaded Sparkle 2.10.1 tools archive has SHA-256
`1a856d2a9edb8e628de88121d7be04cf0e2167f8641650b78fca00b14244cf27`, verified
against its GitHub release asset digest. Tools/cache are ignored by Git.

Notarization uses Keychain profile `lune-notary`; verify access with `xcrun notarytool history --keychain-profile lune-notary` before signing. Provision or restore the profile when it is missing by creating an app-specific password at
[Apple Account](https://account.apple.com/), then run this in an interactive terminal:

```sh
./scripts/setup-notary.sh
```

It prompts for the Apple Account email, delegates the secure password prompt to
`notarytool`, validates with Apple, and saves Keychain profile `lune-notary`. Do not
paste the password into chat or put it in a command-line flag, repository file,
or shell history. The ordinary Apple Account password is not the app-specific
password. No browser is submitted by this setup command.

Using a restricted environment for compilation prevents accidental token env
inheritance, but does not isolate the login Keychain from arbitrary local code.
This bootstrap is for reviewed, trusted sources on the owner's Mac. A future CI
signing pipeline needs separate credentials/access controls and untrusted-PR
isolation, as described in [releases](releases.md).

## Validation scope

Use [current status](status.md), the relevant [feature record](features/README.md), and the frozen release's validation reports for results. Historical bootstrap/port evidence does not establish acceptance of newer combined inputs. Both-target development builds and production signing/update tooling are operational; physical Intel and older-macOS checks remain artifact-specific.

Setup validation checks file/archive hashes, component ancestry/trees, core gitlink, selected patch hashes/order, tool identities and a recursive checkout. Fresh source preparation additionally validates the complete patch/substitution/resource pipeline. Browser tests establish their explicitly reported runtime scope. Release packaging and installed-update tests are separate gates; follow [release delivery](release-delivery.md).
