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
tags retain these inputs. Core and services are unchanged imports. Lune changes
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
about 79 GiB free and only Command Line Tools selected. The wrapper requires at
least 200 GiB free before preparation, a conservative local policy rather than a
measured guarantee. Two source/output trees and peak build usage may require more.
Free space manually; the tooling never removes personal data or old workspaces.

Install full Xcode 26, launch it to complete setup/license acceptance, then:

```sh
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
xcodebuild -downloadComponent MetalToolchain
```

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

Validated locally: 13 guardrail tests, locked file/archive hash structure,
component ancestry and tree IDs, core gitlink, numeric upstream discovery, and
a fresh recursive clone from GitHub without local object reuse. Upstream
download parsing accepts both flattened manifests; text-level name substitution
checks preserve the Web Store, Root Program, and internal URL scheme.
The Lune identity patch applied without fuzz to targeted files reconstructed from
Chromium plus their preceding upstream patches. This is **not** a full-stack
source preparation or proof of a working browser. Python requirements match the
installed environment. A GitHub Actions check validates the lock, ancestry, and
fresh recursive checkout without signing credentials or Chromium downloads.

Before the first usable browser: complete storage/Xcode setup, prepare and compile
arm64, inspect identity/branding and service behavior, run smoke tests, repeat for
x86_64, then implement and validate signing/packaging. Before public updates:
provision services, finish versioning/branding, and test two signed/notarized
releases through architecture-specific staging feeds. See [roadmap](roadmap.md).
