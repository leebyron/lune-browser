"""Shared release identity, immutable asset URLs, and frozen-input validation."""
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = 'leebyron/lune-browser'
DOWNLOADS = f'https://github.com/{REPOSITORY}/releases/download'
LATEST = f'https://github.com/{REPOSITORY}/releases/latest/download'
RAW = f'https://raw.githubusercontent.com/{REPOSITORY}/main/updates'
ARCHES = ('arm64', 'x86_64')


def version_parts(version):
    if not isinstance(version, str) or not re.fullmatch(r'[0-9]{2}\.[0-9]{4}\.[1-9][0-9]*', version):
        raise ValueError('Release version must be YY.MMDD.N')
    year, mmdd, sequence = version.split('.')
    day = date(2000 + int(year), int(mmdd[:2]), int(mmdd[2:]))
    return day, int(sequence)


def version_key(version):
    # Legacy builds 1/2 remain valid update baselines.
    if re.fullmatch(r'[1-9][0-9]*', str(version)):
        return (int(version), 0, 0)
    version_parts(version)
    return tuple(map(int, version.split('.')))


def filename(version, arch):
    version_parts(version)
    if arch not in ARCHES:
        raise ValueError('Unsupported architecture')
    # The release tag versions the URL; latest resolves to the same asset.
    return f'Lune-macos-{arch}.dmg'


def feed_url(arch, channel='stable'):
    if arch not in ARCHES or channel not in ('stable', 'staging'):
        raise ValueError('Invalid feed architecture or channel')
    return f'{RAW}/{channel}/mac/appcast-{arch}.xml'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def load_record(version, root=ROOT, require_clean=True):
    day, counter = version_parts(version)
    path = root / 'manifests/releases' / f'{version}.json'
    record = json.loads(path.read_text())
    if (record.get('schema_version') != 1 or record.get('version') != version
            or record.get('date') != day.isoformat() or record.get('sequence') != counter
            or record.get('timezone') != 'America/Los_Angeles'
            or record.get('architectures') != list(ARCHES) or record.get('tag') != 'v' + version):
        raise ValueError('Invalid frozen release identity')
    required = {'manifests/browser.lock.json', 'config/product.json', 'config/release-recipe.json'}
    if not required.issubset(record['files']):
        raise ValueError('Incomplete release inputs')
    for name, digest in record['files'].items():
        target = (root / name).resolve()
        if not target.is_relative_to(root.resolve()) or target == path.resolve() or not target.is_file() or sha(target) != digest:
            raise ValueError(f'Release input changed: {name}')
        git(root, 'ls-files', '--error-unmatch', name)
    if require_clean:
        if git(root, 'status', '--porcelain', '--untracked-files=normal'):
            raise ValueError('Release checkout must be clean')
        git(root, 'ls-files', '--error-unmatch', str(path.relative_to(root)))
    return record


def validate_acceptance(data, acceptance, channel):
    if acceptance.get('version')!=data['version'] or acceptance.get('source_commit')!=data['source_commit']:
        raise ValueError('Acceptance identifies a different release')
    for arch in ARCHES:
        row=acceptance['architectures'][arch]
        if row.get('sha256') != data['downloads'][arch]['sha256']:
            raise ValueError(f'Acceptance identifies different bytes: {arch}')
        if not all(row.get(k) is True for k in ('install','browse','profile_persistence','signed_app','installed_update')):
            raise ValueError(f'Incomplete architecture acceptance: {arch}')
    if channel=='stable':
        intel=acceptance['architectures']['x86_64']
        native_verified = (intel.get('native_hardware') is True and
                           intel.get('devices') and intel.get('owner_confirmation'))
        decision = acceptance.get('native_intel_deferral', {})
        deferred_by_owner = (intel.get('native_hardware') is False and
                             decision.get('owner_approved') is True and
                             decision.get('testing_pending') is True and
                             isinstance(decision.get('owner_instruction'), str) and
                             bool(decision['owner_instruction'].strip()))
        if not native_verified and not deferred_by_owner:
            raise ValueError('Native Intel acceptance or an explicit owner-approved deferral is required before stable promotion')
