# First browser build

Status: development bootstrap, 2026-11-05. No Lune binary has been compiled,
signed, notarized, or released. Preparation/build commands below are implemented
but still need their first end-to-end run on a ready Mac.

## Tracked inputs

`manifests/browser.lock.json` pins Chromium 157.0.8103.38, ungoogled release
157.0.8103.38-1, Helium core, macOS packaging, and the services snapshot. It hashes
product configuration, patch selections, Homebrew/Python requirements, and both
host download manifests. Every source download has a fixed SHA-256 or SHA-512;
we resolved upstream's mutable hash-file URLs when creating this lock.

The complete Helium stack is selected; no additional PRs or feature topics are
selected. The ungoogled commit is already an ancestor of the selected core, and
the macOS gitlink matches that core. No duplicate ungoogled series is applied.

Published histories are `component/helium`, `component/macos`, and
`component/services`. Permanent `inputs/bootstrap-1/{helium,macos,services,ungoogled}`
tags retain the original inputs. The current macOS fix is pinned separately at
`inputs/bootstrap-2/macos`; original tags are never rewritten. Core and services are unchanged imports. Lune changes
are a separate macOS commit descended from upstream:

- Same-repository core submodule URL, preserving its exact gitlink.
- `Lune` product name, `computer.lune.browser` bundle/profile identity,
  `Lune Storage Key`, and team `RBC9EP7948`.
- GRIT-aware display-name substitution after upstream localization, keeping
  `helium://` and internal identifiers compatible.
- Lune service origin `https://services.lune.computer`, currently **not deployed**.
- Hash-locked source download override and strict patch application without fuzz.
- Removal of the upstream asset-catalog icon name so the bundle uses its `.icns`.
  Original Lune artwork and a complete branding/link audit remain outstanding.

The first development build explicitly disables Sparkle and special branded
entitlements. Product metadata records a dedicated Sparkle public key, but the
updater is not yet configured or enabled in a browser. Do not publish this input
set as a finished distribution. The browser still inherits upstream versioning;
Lune build numbering, artwork, help/onboarding URLs, service behavior, packaging,
and both architectures' runtime checks remain release blockers.

## Prepare this Mac

The owner selected this Mac mini (M4 Pro, 64 GB RAM). At the latest check it has
about 245 GiB free after installing Xcode and Metal. Storage and toolchain now
pass preflight. The wrapper requires at
least 200 GiB free before preparation, a conservative local policy rather than a
measured guarantee. Two source/output trees and peak build usage may require more.
Free space manually; the tooling never removes personal data or old workspaces.

The installed development toolchain is pinned to Xcode **27.2 (27B52)**, SDK
**27.2**, and Metal **27B47**. Helium CI uses Xcode 26.5; we reviewed the pinned
[Chromium SDK configuration](https://github.com/chromium/chromium/blob/157.0.8103.38/build/config/mac/mac_sdk.gni),
which includes Xcode 27 support, and its SDK minimum of 15. This permits an
experimental development attempt, not a claim of tested toolchain compatibility.
Compilation and runtime checks remain required. Future Xcode/SDK changes fail
preflight until reviewed and repinned. The check executes the Metal compiler,
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
Intel host. Both target architectures can be built on this Mac, but Intel runtime
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

This GitHub repository currently requires authentication. Local HTTPS clones use
the owner's existing Git credential helper. CI supplies the job's read-only
`GITHUB_TOKEN` through `gh` only for fetching/checkout; credentials are not stored
in the source tree, and browser signing credentials are never supplied to checks.

Prepared/built state is saved under `.work/<arch>/`; build outputs are inside the
platform's `build/src/out/Default/`. A successful compile must produce `Lune.app`.
`built.json` records `validated_for_release: false`. Nothing publishes automatically.

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
PR/topic replay is not implemented yet; nonempty selections fail validation.

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
preparation with the new locked patch is required; no successful browser yet.

[GitHub documents self-hosted runner compute as free](https://docs.github.com/en/actions/concepts/billing-and-usage).
The private repository's hosted compute and artifact/cache storage still have
allowances and possible overage charges. Keep large source trees, compiler caches,
and initial browser outputs on local disk; do not upload multi-gigabyte checkpoints
to Actions artifacts by default. Do not provision paid runners, purchase storage,
or assume an unverified account billing cap. Existing lightweight checks remain
subject to the account's included allowance.

The workflow is manual-only, restricted to the owner on `main` while the repo
remains private. Runner `lune-mac-mini` is scoped to this repository. The official
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
keep the Mac awake while jobs run, and retain local compilation caches. Establish
one successful arm64 build before scheduling recurring jobs or running the Intel
target. The owner can keep using the GitHub Actions UI for triggering and reading
logs, but the Mac must remain online for jobs to execute.

Stock GitHub-hosted macOS builds remain a possible future experiment. The pinned
[Helium workflow](https://github.com/imputnet/helium-macos/blob/37efe2c65dccc21aaf1d8ea66fd35d1348c386a8/.github/workflows/building.yml)
chains up to ten build phases with source/build artifacts to cross job time limits.
That is source evidence of its strategy, not proof that Lune will fit the private
repository's free compute/storage allowances. Do not copy its artifact-heavy
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

Notarization credentials are still needed. Create an app-specific password at
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

## Validation and remaining work

Validated locally: 14 guardrail tests, locked file/archive hash structure,
component ancestry and tree IDs, core gitlink, numeric upstream discovery, and
a fresh recursive clone from GitHub without local object reuse. Upstream
download parsing accepts both flattened manifests; text-level name substitution
checks preserve the Web Store, Root Program, and internal URL scheme.
The Lune identity patch applied without fuzz to targeted files reconstructed from
Chromium plus their preceding upstream patches. Full-stack source preparation and GN generation subsequently passed in the first
CI run; compilation failed as documented above. This is not proof of a working
browser. Python requirements match the
installed environment. A GitHub Actions check validates the lock, ancestry, and
fresh recursive checkout without signing credentials or Chromium downloads.

Before the first usable browser: run the new CI workflow to prepare and compile
arm64, inspect identity/branding and service behavior, run smoke tests, repeat for
x86_64, then implement and validate signing/packaging. Before public updates:
provision services, finish versioning/branding, and test two signed/notarized
releases through architecture-specific staging feeds. See [roadmap](roadmap.md).
