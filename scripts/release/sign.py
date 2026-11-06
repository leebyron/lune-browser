#!/usr/bin/env python3
"""Run Chromium's nested signing/notarization, then assess the stapled result."""
from pathlib import Path
import sys

stage = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(stage / 'input/Lune Packaging'))
from signing import chromium_config, driver

# Gatekeeper rejects a first release before Apple has notarized it. Defer only
# that assessment until after notarization/stapling; package.py requires it then.
# Keep the release signing requirements and hardened runtime entitlements.
chromium_config.ChromiumCodeSignConfig.run_spctl_assess = property(lambda self: False)
driver.main([
    '--input', str(stage / 'input'), '--output', str(stage / 'signed'),
    '--identity', sys.argv[2], '--disable-packaging', '--notarize',
    '--notary-arg=--keychain-profile=' + sys.argv[3],
])
