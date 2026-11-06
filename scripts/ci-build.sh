#!/usr/bin/env bash
# Run only reviewed inputs in the dedicated self-hosted runner checkout.
set -euo pipefail
cd "$(dirname "$0")/.."
arch="${1:?Usage: ci-build.sh arm64|x86_64}"
case "$arch" in arm64|x86_64) ;; *) echo "Unsupported architecture" >&2; exit 2 ;; esac
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
if [[ ! -x .work/venv/bin/python ]]; then
  /opt/homebrew/bin/python3.13 -m venv .work/venv
fi
.work/venv/bin/python -m pip install --require-hashes -r config/requirements-build.txt
python3 scripts/lune.py validate --git-objects
mkdir -p .work/logs
log=".work/logs/${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}-$arch.log"
if [[ ! -f ".work/$arch/prepared.json" ]]; then
  # prepare refuses a partial existing source tree instead of deleting local work.
  python3 scripts/lune.py prepare --arch "$arch" 2>&1 | tee -a "$log"
fi
python3 scripts/check-onboarding.py ".work/$arch/macos/build/src"
python3 scripts/check-ui-port.py ".work/$arch/macos/build/src"
# build verifies the preparation record, toolchain, and lock before resuming.
python3 scripts/lune.py build --arch "$arch" --jobs 10 2>&1 | tee -a "$log"
