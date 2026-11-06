#!/usr/bin/env python3
"""Stage, sign/notarize, and package one locked Lune macOS release artifact.

Each stage writes evidence only after all checks succeed. Published files are
never overwritten. This command does not publish or promote an update feed.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def run(*args, capture=False):
    return subprocess.run([str(a) for a in args], check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + '\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plist(path):
    return plistlib.loads(Path(path).read_bytes())


def inspect_app(app, product, arch, build=None):
    info = plist(app / 'Contents/Info.plist')
    require(info['CFBundleIdentifier'] == product['bundle_id'], 'Wrong bundle identity')
    require(run('lipo', '-archs', app / 'Contents/MacOS/Lune', capture=True).strip() == arch,
            'Wrong binary architecture')
    expected = f'https://lune.computer/updates/stable/mac/appcast-{arch}.xml'
    require(info.get('SUFeedURL') == expected, 'Wrong Sparkle feed')
    require(info.get('SUPublicEDKey') == product['sparkle_public_key'], 'Wrong Sparkle key')
    require(info.get('SUEnableAutomaticChecks') is True, 'Automatic checks must be a plist boolean')
    require(info.get('SUVerifyUpdateBeforeExtraction') is True, 'Verify archives before extraction')
    require(info.get('SUScheduledCheckInterval') == 86400, 'Wrong update interval')
    framework = app / 'Contents/Frameworks/Lune Framework.framework/Frameworks/Sparkle.framework'
    require(framework.is_dir(), 'Sparkle framework missing')
    require(plist(framework / 'Resources/Info.plist')['CFBundleShortVersionString'] == '2.10.1',
            'Wrong Sparkle framework version')
    if build is not None:
        require(info['CFBundleVersion'] == str(build), 'Wrong Lune build number')
    return info


def stage(args):
    product = read(ROOT / 'config/product.json')
    lock = read(ROOT / 'manifests/browser.lock.json')
    report = read(args.build_report)
    require(report.get('exit_code') == 0, 'Compilation must pass')
    require(report['arch'] == args.arch, 'Build report architecture differs')
    require(report['platform_commit'] == lock['components']['macos']['commit'], 'Unpinned build input')
    require(report['args_sha256'] == sha(args.output / 'args.gn'), 'Build arguments changed')
    allocated = read(ROOT / 'config/release-builds.json')['builds']
    require(args.build in {row['number'] for row in allocated}, 'Allocate this build number in Git first')
    require(not args.directory.exists(), 'Stage already exists; never overwrite a release candidate')
    app = args.output / 'Lune.app'
    info = inspect_app(app, product, args.arch)
    smoke = read(args.smoke_report)
    require(smoke.get('passed') is True and smoke['chromium_version'] == lock['chromium_version']
            and smoke['architecture'] == args.arch, 'Matching runtime smoke must pass')
    require(smoke.get('artwork_component_commit') == report['platform_commit'], 'Smoke tested different inputs')
    require(smoke['executable_sha256'] == sha(app / 'Contents/MacOS/Lune')
            and smoke['framework_sha256'] == sha(app / 'Contents/Frameworks/Lune Framework.framework/Lune Framework'),
            'App changed after runtime validation')
    require((args.output / 'Lune Packaging/sign_chrome.py').is_file(), 'Build packaging tools first')
    args.directory.mkdir(parents=True)
    run('ditto', app, args.directory / 'input/Lune.app')
    run('ditto', args.output / 'Lune Packaging', args.directory / 'input/Lune Packaging')
    # Sparkle compares the outer app's build number. Keep Chromium's version and
    # versioned framework layout intact, independently of Lune's release counter.
    target = args.directory / 'input/Lune.app/Contents/Info.plist'
    info['CFBundleVersion'] = str(args.build)
    info['CFBundleShortVersionString'] = lock['chromium_version']
    target.write_bytes(plistlib.dumps(info))
    inspect_app(args.directory / 'input/Lune.app', product, args.arch, args.build)
    save(args.directory / 'candidate.json', {
        'build': args.build, 'arch': args.arch, 'chromium_version': lock['chromium_version'],
        'platform_commit': report['platform_commit'], 'core_commit': lock['components']['helium']['commit'],
        'orchestrator_commit': run('git', '-C', ROOT, 'rev-parse', 'HEAD', capture=True).strip(),
        'lock_sha256': sha(ROOT / 'manifests/browser.lock.json'),
        'product': product, 'args_sha256': report['args_sha256'],
        'release_ledger_sha256': sha(ROOT / 'config/release-builds.json'),
        'input_executable_sha256': sha(app / 'Contents/MacOS/Lune'),
        'input_framework_sha256': sha(app / 'Contents/Frameworks/Lune Framework.framework/Lune Framework'),
        'signed': False, 'packaged': False, 'published': False,
    })
    shutil.copyfile(ROOT / 'manifests/browser.lock.json', args.directory / 'browser.lock.json')


def sign(args):
    candidate = read(args.directory / 'candidate.json')
    require(not (args.directory / 'signed').exists(), 'Signing output already exists; inspect before retrying')
    product = candidate['product']
    # This only tests access; the credential remains in Keychain.
    run('xcrun', 'notarytool', 'history', '--keychain-profile', product['notary_profile'], capture=True)
    run(sys.executable, ROOT / 'scripts/release/sign.py', args.directory,
        product['signing_identity'], product['notary_profile'])
    app = args.directory / 'signed/stable/Lune.app'
    inspect_app(app, product, candidate['arch'], candidate['build'])
    run('codesign', '--verify', '--deep', '--strict', app)
    run('xcrun', 'stapler', 'validate', app)
    run('spctl', '--assess', '--type', 'execute', '--verbose=2', app)
    candidate['signed'] = True
    candidate['signed_executable_sha256'] = sha(app / 'Contents/MacOS/Lune')
    save(args.directory / 'candidate.json', candidate)


def package(args):
    candidate = read(args.directory / 'candidate.json')
    require(candidate['signed'], 'Sign and notarize the app first')
    product = candidate['product']
    app = args.directory / 'signed/stable/Lune.app'
    inspect_app(app, product, candidate['arch'], candidate['build'])
    run('codesign', '--verify', '--deep', '--strict', app)
    name = f"Lune-{candidate['chromium_version']}-{candidate['build']}-macos-{candidate['arch']}.dmg"
    dmg = args.directory / name
    require(not dmg.exists(), 'DMG already exists; never overwrite final bytes')
    volume = args.directory / 'volume'
    require(not volume.exists(), 'Packaging volume already exists; inspect before retrying')
    volume.mkdir()
    run('ditto', app, volume / 'Lune.app')
    (volume / 'Applications').symlink_to('/Applications')
    run('hdiutil', 'create', '-volname', 'Lune', '-srcfolder', volume,
        '-format', 'UDZO', '-imagekey', 'zlib-level=9', dmg)
    run('codesign', '--sign', product['signing_identity'], '--timestamp',
        '--identifier', product['bundle_id'], dmg)
    result = json.loads(run('xcrun', 'notarytool', 'submit', dmg, '--wait',
                            '--keychain-profile', product['notary_profile'],
                            '--output-format', 'json', capture=True))
    save(args.directory / 'dmg-notarization.json', result)
    require(result.get('status') == 'Accepted', 'Apple rejected the DMG')
    run('xcrun', 'stapler', 'staple', dmg)
    run('xcrun', 'stapler', 'validate', dmg)
    run('codesign', '--verify', '--strict', dmg)
    run('spctl', '--assess', '--type', 'open', '--context', 'context:primary-signature', '--verbose=2', dmg)
    signer = ROOT / '.cache/tools/sparkle-2.10.1/bin/sign_update'
    signature = run(signer, '--account', product['sparkle_account'], '-p', dmg, capture=True).strip()
    require(len(base64.b64decode(signature, validate=True)) == 64, 'Invalid Ed25519 signature')
    run(signer, '--account', product['sparkle_account'], '--verify', dmg, signature)
    candidate.update(packaged=True, filename=name, sha256=sha(dmg), size=dmg.stat().st_size,
                     ed_signature=signature, minimum_system_version=plist(app / 'Contents/Info.plist')['LSMinimumSystemVersion'])
    save(args.directory / 'candidate.json', candidate)
    (args.directory / 'SHA256SUMS').write_text(f"{candidate['sha256']}  {name}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('stage')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--build-report', type=Path, required=True)
    p.add_argument('--smoke-report', type=Path, required=True)
    p.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    p.add_argument('--build', type=int, required=True)
    p.add_argument('--directory', type=Path, required=True)
    for command in ('sign', 'package'):
        p = sub.add_parser(command)
        p.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    args.directory = args.directory.resolve()
    if args.command == 'stage':
        args.output = args.output.resolve()
    globals()[args.command](args)


if __name__ == '__main__':
    main()
