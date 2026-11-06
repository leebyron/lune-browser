#!/usr/bin/env bash
set -euo pipefail
if [[ ! -t 0 ]]; then
  echo "Run this script in your terminal; Apple credentials are entered interactively." >&2
  exit 1
fi
read -r -p "Apple Account email for team RBC9EP7948: " apple_id
if [[ -z "$apple_id" ]]; then
  echo "An Apple Account email is required." >&2
  exit 1
fi
# Omitting --password requests a secure prompt, with no password in shell history.
exec xcrun notarytool store-credentials lune-notary \
  --apple-id "$apple_id" --team-id RBC9EP7948
