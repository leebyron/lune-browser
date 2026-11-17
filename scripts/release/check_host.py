#!/usr/bin/env python3
"""Check the exact release host toolchain before preparing Chromium sources."""
import argparse
import json
import subprocess
import sys

from model import ROOT


def check_host(recipe, env):
    def output(*command):
        return subprocess.check_output(command, text=True, env=env).strip()

    xcode = output('xcodebuild', '-version')
    expected_xcode = f"Xcode {recipe['xcode_version']}\nBuild version {recipe['xcode_build']}"
    if xcode != expected_xcode:
        raise ValueError(f'Xcode differs from release recipe: expected {expected_xcode!r}, got {xcode!r}')
    checks = (
        (('sw_vers', '-productVersion'), recipe['host_macos_version'], 'macOS version'),
        (('sw_vers', '-buildVersion'), recipe['host_macos_build'], 'macOS build'),
        (('uname', '-m'), recipe['host_architecture'], 'host architecture'),
        (('xcrun', '--sdk', 'macosx', '--show-sdk-version'), recipe['sdk_version'], 'macOS SDK'),
        (('python', '--version'), recipe['python_version'], 'build Python'),
        (('sccache', '--version'), recipe['sccache_version'], 'sccache'),
    )
    for command, expected, tool in checks:
        actual = output(*command)
        if actual != expected:
            raise ValueError(f'{tool} differs from release recipe: expected {expected!r}, got {actual!r}')

    metal = output('xcrun', 'metal', '--version').partition('\n')[0]
    if metal != recipe['metal_version']:
        raise ValueError(f"Metal differs from release recipe: expected {recipe['metal_version']!r}, got {metal!r}")
    packages = set(output('python', '-m', 'pip', 'freeze').splitlines())
    expected_packages = set(recipe['python_packages'])
    if packages != expected_packages:
        raise ValueError('Build Python packages differ from release recipe: '
                         f'missing {sorted(expected_packages - packages)!r}, extra {sorted(packages - expected_packages)!r}')
    return xcode


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    sys.path.insert(0, str(ROOT / 'scripts'))
    import lune

    recipe = lune.read_json(ROOT / 'config/release-recipe.json')
    check_host(recipe, lune.build_env())
    print(json.dumps({'host_toolchain': 'verified', 'recipe': 'config/release-recipe.json'}))


if __name__ == '__main__':
    main()
