#!/usr/bin/env python3
"""Locked, resumable entry points for Lune's first macOS build.

No command publishes a browser release or enables unattended builds.
"""
import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'manifests/browser.lock.json'
SHA = re.compile(r'[0-9a-f]{40}')


def run(args, cwd=ROOT, capture=False, env=None):
    return subprocess.run([str(a) for a in args], cwd=cwd, check=True,
                          text=True, stdout=subprocess.PIPE if capture else None,
                          env=env).stdout


def git(*args, cwd=ROOT):
    return run(['git', *args], cwd=cwd, capture=True).strip()


def read_json(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n')
    temp.replace(path)


def version_tuple(tag):
    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)\.(\d+)-(\d+)', tag)
    if not match:
        raise ValueError(f'Not a stable ungoogled tag: {tag}')
    return tuple(map(int, match.groups()))


def ancestors(older, newer):
    result = subprocess.run(['git', 'merge-base', '--is-ancestor', older, newer], cwd=ROOT)
    if result.returncode not in (0, 1):
        raise RuntimeError('Cannot check ancestry; fetch the locked inputs first.')
    return result.returncode == 0


def fetch(_args):
    for name, source in read_json(ROOT / 'manifests/upstreams.json').items():
        if name == 'schema_version':
            continue
        run(['git', '-c', 'fetch.prune=false', 'fetch', '--no-prune', '--no-tags',
             source['url'],
             f'+refs/heads/{source["branch"]}:refs/remotes/upstream-{name}/{source["branch"]}',
             f'refs/tags/*:refs/tags/upstream/{name}/*'])


def discover(_args):
    prefix = 'upstream/ungoogled/'
    candidates = []
    for tag in git('tag', '--list', prefix + '*').splitlines():
        try:
            candidates.append((version_tuple(tag[len(prefix):]), tag))
        except ValueError:
            continue
    if not candidates:
        raise ValueError('No upstream tags. Run fetch first.')
    tag = max(candidates)[1]
    commit = git('rev-parse', tag + '^{commit}')
    core = git('rev-parse', 'upstream-helium/main')
    result = {'ungoogled_tag': tag[len(prefix):], 'ungoogled_commit': commit,
              'helium_head': core, 'included_in_helium': ancestors(commit, core),
              'locked_ungoogled_is_current': read_json(LOCK)['ungoogled']['commit'] == commit}
    print(json.dumps(result, indent=2))
    if not result['included_in_helium']:
        raise ValueError('New ungoogled input requires reviewed integration; lock was not changed.')


def validate_lock(lock):
    if lock.get('schema_version') != 1 or lock.get('stage') != 'development':
        raise ValueError('Unsupported lock schema or build stage.')
    if lock.get('targets') != ['arm64', 'x86_64']:
        raise ValueError('Both supported target architectures must be locked.')
    if lock.get('repository') != 'https://github.com/leebyron/lune-browser.git':
        raise ValueError('Unexpected component repository.')
    expected_downloads = ['manifests/downloads-arm64.ini', 'manifests/downloads-x64.ini']
    required_files = {'config/product.json', 'config/Brewfile', 'config/requirements-build.txt',
                      'manifests/upstreams.json', 'manifests/patches.json', *expected_downloads}
    if not required_files.issubset(lock['files']) or lock['download_configs'] != expected_downloads:
        raise ValueError('Lock is missing required configuration hashes or host download manifests.')
    version_tuple(lock['ungoogled']['tag'])
    if lock['ungoogled']['tag'].rsplit('-', 1)[0] != lock['chromium_version']:
        raise ValueError('Chromium and ungoogled versions differ.')
    for name in ('helium', 'macos', 'services'):
        component = lock['components'][name]
        for field in ('commit', 'upstream_commit'):
            if not SHA.fullmatch(component[field]):
                raise ValueError(f'{name}.{field} must be a full commit ID.')
        if not re.fullmatch(r'refs/tags/inputs/[a-z0-9-]+/' + name, component['ref']):
            raise ValueError('Components need a permanent input tag.')
    if not SHA.fullmatch(lock['ungoogled']['commit']):
        raise ValueError('Ungoogled input must be a full commit ID.')
    for name, expected in lock['files'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f'Invalid locked file: {name}')
        if digest(path) != expected:
            raise ValueError(f'Locked input changed: {name}. Review and update the lock.')
    selections = read_json(ROOT / 'manifests/patches.json')
    if selections['pull_requests'] or selections['feature_topics']:
        raise ValueError('PR/topic replay is not implemented for bootstrap; do not silently ignore selections.')
    if selections['helium_stack'] != 'complete':
        raise ValueError('The bootstrap requires the complete Helium stack.')
    for name in lock['download_configs']:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(ROOT / name)
        if set(parser.sections()) != {'chromium', 'chromium-mac', 'sparkle',
                                      'search_engines_data', 'onboarding', 'ublock_origin'}:
            raise ValueError(f'{name} is missing required downloads or adds unreviewed inputs.')
        for section in parser.sections():
            record = parser[section]
            if 'hash_url' in record or not any(
                    re.fullmatch(r'[0-9a-f]{' + str(length) + r'}', record.get(alg, ''))
                    for alg, length in [('sha256', 64), ('sha512', 128)]):
                raise ValueError(f'{name}:{section} must have a pinned SHA-256/512 digest.')
            if not record['url'].startswith('https://'):
                raise ValueError('Download URLs must use HTTPS.')


def validate(args):
    lock = read_json(LOCK)
    validate_lock(lock)
    if args.git_objects:
        for name, component in lock['components'].items():
            if not ancestors(component['upstream_commit'], component['commit']):
                raise ValueError(f'{name} lost upstream ancestry.')
            if git('rev-parse', component['ref'] + '^{commit}') != component['commit']:
                raise ValueError(f'{name} input tag does not match lock.')
        core = lock['components']['helium']['commit']
        macos = lock['components']['macos']['commit']
        if not ancestors(lock['ungoogled']['commit'], core):
            raise ValueError('Selected ungoogled release is not in Helium ancestry.')
        if git('show', core + ':chromium_version.txt') != lock['chromium_version']:
            raise ValueError('Core Chromium version differs from lock.')
        if git('rev-parse', macos + ':helium-chromium') != core:
            raise ValueError('Platform gitlink differs from locked core.')
        for name, component in lock['components'].items():
            actual = git('rev-parse', component['commit'] + '^{tree}')
            if actual != component['tree']:
                raise ValueError(f'{name} tree hash differs from lock.')
    print('Locked configuration valid' + ('; ancestry, tags, trees, and gitlink verified.' if args.git_objects else '.'))


def build_env():
    # Do not pass release tokens or notarization passwords to compilation.
    keep = ('HOME', 'TMPDIR', 'USER', 'LOGNAME', 'DEVELOPER_DIR')
    env = {key: os.environ[key] for key in keep if key in os.environ}
    env.update(PATH=f'{ROOT}/.work/venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
               LC_ALL='en_US.UTF-8', PATCH_BIN='/opt/homebrew/bin/gpatch')
    return env


def check_toolchain(xcode, sdk, product):
    expected = f"Xcode {product['xcode_version']}\nBuild version {product['xcode_build']}"
    if xcode != expected or sdk != product['macos_sdk_version']:
        raise ValueError(f"Toolchain differs from lock: expected {expected!r}, SDK {product['macos_sdk_version']}; got {xcode!r}, SDK {sdk}.")


def doctor(args):
    product = read_json(ROOT / 'config/product.json')
    problems = []
    free = shutil.disk_usage(ROOT).free / 1024**3
    print(f'Platform: {platform.system()} {platform.machine()}; free space: {free:.1f} GiB')
    if platform.system() != 'Darwin':
        problems.append('macOS is required for browser compilation.')
    minimum = product['minimum_build_free_gib'] if getattr(args, 'command', None) == 'build' else product['minimum_free_gib']
    if free < minimum:
        problems.append(f'Free at least {minimum} GiB for this build stage.')
    env = build_env()
    try:
        xcode = run(['xcodebuild', '-version'], capture=True, env=env)
        print(xcode.strip())
        check_toolchain(xcode.strip(), run(['xcrun', '--sdk', 'macosx', '--show-sdk-version'], capture=True, env=env).strip(), product)
        run(['xcodebuild', '-checkFirstLaunchStatus'], capture=True, env=env)
        run(['xcrun', 'metal', '--version'], capture=True, env=env)
    except ValueError as error:
        problems.append(str(error))
    except (subprocess.CalledProcessError, FileNotFoundError):
        problems.append('Complete full Xcode setup and run xcodebuild -downloadComponent MetalToolchain.')
    for command in ('greadlink', 'wget', 'zstd', 'gpatch', 'quilt', 'sccache'):
        if not shutil.which(command, path=env['PATH']):
            problems.append(f'Missing build dependency: {command}')
    python = ROOT / '.work/venv/bin/python'
    if not python.exists():
        problems.append('Create .work/venv with Python 3.13 and install config/requirements-build.txt.')
    else:
        try:
            run([python, '-c', 'import sys,requests,PIL; assert sys.version_info[:2] == (3,13); print(sys.version)'], env=env)
        except subprocess.CalledProcessError:
            problems.append('Python 3.13 build environment is incomplete.')
    for problem in problems:
        print('BLOCKED:', problem)
    if problems:
        raise ValueError('Build prerequisites are not ready; no large downloads were started.')
    print('Build prerequisites ready. This does not verify a Chromium build or signing.')


def workspace(arch):
    return ROOT / '.work' / arch / 'macos'


def check_checkout(path, lock):
    for folder, name in ((path, 'macos'), (path / 'helium-chromium', 'helium')):
        if git('rev-parse', 'HEAD', cwd=folder) != lock['components'][name]['commit']:
            raise ValueError(f'Wrong commit in {folder}; use a new workspace, do not reset local work.')
        if git('status', '--porcelain', '--untracked-files=normal', cwd=folder):
            raise ValueError(f'Dirty component checkout: {folder}')
    url = git('config', '-f', '.gitmodules', '--get', 'submodule.helium-chromium.url', cwd=path)
    if url != lock['repository']:
        raise ValueError('Core submodule URL is not the locked Lune repository.')


def checkout(args):
    lock = read_json(LOCK)
    validate_lock(lock)
    dest = workspace(args.arch)
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', '--no-checkout', '--no-tags', '--single-branch',
             '--branch', lock['components']['macos']['ref'].removeprefix('refs/tags/'),
             lock['repository'], dest])
        run(['git', 'checkout', '--detach', lock['components']['macos']['commit']], cwd=dest)
        run(['git', 'submodule', 'update', '--init', '--recursive'], cwd=dest)
    check_checkout(dest, lock)
    print(f'Exact {args.arch} checkout ready: {dest}')


def prepare(args):
    validate_lock(read_json(LOCK))
    require_clean_orchestrator()
    doctor(args)
    checkout(args)
    dest = workspace(args.arch)
    state_path = dest.parent / 'prepared.json'
    if (dest / 'build/src').exists() or state_path.exists():
        raise ValueError('Preparation has already started here. Inspect/recover it manually; refusing to delete sources.')
    host = 'arm64' if platform.machine() == 'arm64' else 'x64'
    env = build_env()
    env['LUNE_DOWNLOADS_INI'] = str(ROOT / f'manifests/downloads-{host}.ini')
    # Positional arguments avoid interpolating paths or user arguments into shell code.
    shell = '''set -euo pipefail
_root_dir="$1"
source "$_root_dir/devutils/shared.sh"
prepare_sources true
write_gn_args "$2" release
cat >> "$_out_dir/args.gn" <<'GN'
enable_sparkle=false
include_branded_entitlements=false
GN
gn_gen
'''
    run(['/bin/bash', '-c', shell, 'lune-prepare', dest, args.arch], cwd=dest, env=env)
    write_json(state_path, {'lock_sha256': digest(LOCK), 'arch': args.arch,
                           'xcode': run(['xcodebuild', '-version'], capture=True, env=env).strip(),
                           'args_sha256': digest(dest / 'build/src/out/Default/args.gn')})
    print('Source preparation and GN generation succeeded. Compilation has not run.')


def build(args):
    lock = read_json(LOCK)
    validate_lock(lock)
    require_clean_orchestrator()
    doctor(args)
    dest = workspace(args.arch)
    check_checkout(dest, lock)
    state = read_json(dest.parent / 'prepared.json')
    if state['lock_sha256'] != digest(LOCK) or state['arch'] != args.arch:
        raise ValueError('Prepared workspace belongs to different inputs.')
    if state['args_sha256'] != digest(dest / 'build/src/out/Default/args.gn'):
        raise ValueError('GN arguments changed after preparation.')
    env = build_env()
    if state['xcode'] != run(['xcodebuild', '-version'], capture=True, env=env).strip():
        raise ValueError('Xcode changed after preparation; revalidate the workspace.')
    run(['/bin/bash', dest / 'devutils/shared.sh', 'build', '-j', str(args.jobs),
         'chrome/installer/mac'], cwd=dest, env=env)
    app = dest / 'build/src/out/Default/Lune.app'
    if not app.is_dir():
        raise ValueError('Compilation returned successfully but Lune.app was not produced.')
    write_json(dest.parent / 'built.json', {**state, 'app': str(app),
               'orchestrator_commit': git('rev-parse', 'HEAD'), 'validated_for_release': False})
    print(f'Compiled: {app}\nNot signed, notarized, runtime-tested, or ready for release.')


def require_clean_orchestrator():
    if git('status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('Commit the reviewed orchestrator changes before preparing or building.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('fetch', 'discover', 'doctor', 'validate', 'checkout', 'prepare', 'build'):
        command = commands.add_parser(name)
        command.set_defaults(func=globals()[name])
        if name == 'validate':
            command.add_argument('--git-objects', action='store_true')
        if name in ('checkout', 'prepare', 'build'):
            command.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
        if name == 'build':
            command.add_argument('--jobs', type=int, default=10)
    args = parser.parse_args()
    if hasattr(args, 'jobs') and args.jobs < 1:
        parser.error('--jobs must be positive')
    try:
        args.func(args)
    except (ValueError, RuntimeError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'error: {error}\n')


if __name__ == '__main__':
    main()
