"""Cache transport must preserve dependency invalidation, not just cache hits."""
from array import array
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/release'))
import cache_preflight
import cache_reuse
import ninja_deps


class DependencyLogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'deps'

    def test_round_trip_and_alias_merge_preserve_latest_records(self):
        log = ninja_deps.DepsLog(['obj.o', '/old/header.h', '../../header.h'],
                                {0: (1234567890123456789, array('I', [1, 2]))})
        stats = ninja_deps.write(self.path, log,
            lambda name: '../../header.h' if name == '/old/header.h' else name)
        actual = ninja_deps.read(self.path)
        self.assertEqual(actual.paths, ['obj.o', '../../header.h'])
        self.assertEqual(actual.records[0], (1234567890123456789, array('I', [1, 1])))
        self.assertEqual(stats['relocated_paths'], 1)

    def test_rejects_corruption_instead_of_silently_losing_dependencies(self):
        bad = [b'', b'# ninjadeps\n' + struct.pack('<I', 5),
               ninja_deps.HEADER + b'\x01',
               ninja_deps.HEADER + struct.pack('<I', 8) + b'ab',
               ninja_deps.HEADER + struct.pack('<I', 8) + b'a\0\0\0' + b'xxxx',
               ninja_deps.HEADER + struct.pack('<IIQ', 0x8000000c, 0, 1)]
        for data in bad:
            with self.subTest(data=data):
                self.path.write_bytes(data)
                with self.assertRaises(ValueError):
                    ninja_deps.read(self.path)

    def test_output_alias_collision_leaves_destination_intact(self):
        self.path.write_bytes(b'original')
        log = ninja_deps.DepsLog(['a.o', 'b.o'],
                                {0: (1, array('I')), 1: (2, array('I'))})
        with self.assertRaisesRegex(ValueError, 'distinct output'):
            ninja_deps.write(self.path, log, lambda _: 'same.o')
        self.assertEqual(self.path.read_bytes(), b'original')

    def test_root_boundaries_and_dot_segments(self):
        mapper = lambda name: cache_reuse.relocated(name, ['/old/src'], Path('/new/src'),
                                                     Path('/new/src/out/Default'))
        self.assertEqual(mapper('/old/src/out/Default/../../header.h'), '../../header.h')
        self.assertEqual(mapper('/old/src-other/header.h'), '/old/src-other/header.h')
        self.assertEqual(mapper('../../header.h'), '../../header.h')

    def test_legacy_compiler_alias_requires_cached_digest_proof(self):
        relative = 'third_party/llvm-build/Release+Asserts/lib/clang/24/include/stddef.h'
        state = {'entries': [{'name': '/old/src/' + relative, 'digest': {'hash': 'abc'}}]}
        mapper = cache_reuse.dependency_mapper(['/old/src'], Path('/new/src'),
            Path('/new/src/out/Default'), {relative: 'abc'}, state)
        self.assertEqual(mapper('/deleted/src/' + relative), '../../' + relative)
        with self.assertRaisesRegex(ValueError, 'Unproven dependency'):
            mapper('/deleted/src/project/header.h')
        mapper = cache_reuse.dependency_mapper(['/old/src'], Path('/new/src'),
            Path('/new/src/out/Default'), {relative: 'CHANGED'}, state)
        with self.assertRaisesRegex(ValueError, 'Unproven dependency'):
            mapper('/deleted/src/' + relative)


class PreflightTests(unittest.TestCase):
    def test_missing_foreign_dependency_stops_before_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / 'src'
            out = src / 'out/Default'
            out.mkdir(parents=True)
            def dry_run(*args, **kwargs):
                (Path(directory) / 'plan.explain').write_text(
                    'deps for obj.o missing-inputs: input /deleted/src/header.h: stat missing\n')
            with patch.object(cache_preflight.subprocess, 'run', side_effect=dry_run):
                with self.assertRaisesRegex(ValueError, 'outside this workspace'):
                    cache_preflight.check(src, out, ['chrome'], {}, Path(directory) / 'plan.log')

    def test_interrupted_transfer_cannot_be_built(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            (src / 'out').mkdir()
            (src / 'out' / cache_reuse.PENDING).write_text('{}')
            with patch.object(cache_preflight.subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'Incomplete cache transfer'):
                    cache_preflight.check(src, src / 'out', [], {}, src / 'plan.log')
                run.assert_not_called()


class CacheTransferTests(unittest.TestCase):
    def test_changed_content_cannot_hide_behind_a_preserved_cached_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory).resolve()
            (source / 'header.h').write_text('new content')
            timestamp = (source / 'header.h').stat().st_mtime_ns
            state = {'entries': [{'name': '/donor/header.h', 'digest': {'hash': 'old'},
                                  'id': {'mod_time': timestamp}}]}
            with self.assertRaisesRegex(ValueError, 'identical timestamp'):
                cache_reuse.verify_cached_source_ids(state, ['/donor'], source, {'header.h': 'new'})
            state['entries'][0]['id']['mod_time'] -= 1
            cache_reuse.verify_cached_source_ids(state, ['/donor'], source, {'header.h': 'new'})

    def test_rejects_paths_that_could_write_into_the_donor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            donor, fresh = root / 'donor', root / 'fresh'
            donor.mkdir()
            fresh.mkdir()
            with self.assertRaisesRegex(ValueError, 'outside both source trees'):
                cache_reuse.seed(fresh, donor, root / 'prepared.json', donor / 'report.json',
                                 ['arm64'], {})
            (donor / 'out').mkdir()
            (fresh / 'out').symlink_to(donor / 'out', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'must not be a symlink'):
                cache_reuse.seed(fresh, donor, root / 'prepared.json', root / 'report.json',
                                 ['arm64'], {})
            self.assertEqual(list((donor / 'out').iterdir()), [])

    def test_only_identical_sources_inherit_timestamps_and_donor_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            donor, fresh = root / 'donor', root / 'fresh'
            donor_out = donor / 'out/Default'
            donor_out.mkdir(parents=True)
            fresh.mkdir()
            for folder in (donor, fresh):
                (folder / 'tool').write_text('pinned compiler')
                (folder / 'main.cc').write_text('unchanged source')
            (donor / 'header.h').write_text('old header')
            (fresh / 'header.h').write_text('changed header')
            for name in ('tool', 'main.cc', 'header.h'):
                os.utime(donor / name, ns=(1_000_000_000, 1_000_000_000))
            (root / 'config').mkdir()
            (root / 'config/release-recipe.json').write_text(json.dumps(
                {'source_tools': {'tool': cache_reuse.sha(fresh / 'tool')}}))
            files, links = cache_reuse.inventory(fresh)
            prepared = root / 'prepared.json'
            prepared.write_text(json.dumps(dict(strict_replay_passed=True,
                inventory_version=1, files=files, symlinks=links)))
            for name in ('.siso_lock', '.siso_fs_state', 'build.ninja', 'args.gn', 'obj.o'):
                (donor_out / name).write_text(name)
            (donor_out / 'Lune.app').mkdir()
            ninja_deps.write(donor_out / '.siso_deps', ninja_deps.DepsLog(
                ['obj.o', str(donor / 'header.h')], {0: (42, array('I', [1]))}))
            original = cache_reuse.fingerprint(donor_out)
            state = {'entries': [{'name': str(donor / 'main.cc')}],
                     'build_targets': {'targets': ['chrome']}}
            real_run = subprocess.run
            imported = []
            def run(cmd, **kwargs):
                if 'import' in cmd:
                    imported.append(json.loads(kwargs['input']))
                    return subprocess.CompletedProcess(cmd, 0)
                return real_run(cmd, **kwargs)
            with patch.object(cache_reuse, 'ROOT', root), \
                 patch.object(cache_reuse.subprocess, 'check_output', return_value=json.dumps(state)), \
                 patch.object(cache_reuse.subprocess, 'run', side_effect=run):
                result = cache_reuse.seed(fresh, donor, prepared, root / 'report.json',
                                          ['arm64'], dict(os.environ))
            self.assertEqual(result['changed_sources'], ['header.h'])
            self.assertEqual((fresh / 'main.cc').stat().st_mtime_ns, 1_000_000_000)
            self.assertGreater((fresh / 'header.h').stat().st_mtime_ns, 1_000_000_000)
            self.assertEqual(cache_reuse.fingerprint(donor_out), original)
            self.assertEqual((donor / 'header.h').read_text(), 'old header')
            self.assertFalse((fresh / 'out/Default/Lune.app').exists())
            self.assertFalse((fresh / 'out' / cache_reuse.PENDING).exists())
            self.assertEqual(imported[0]['entries'][0]['name'], str(fresh / 'main.cc'))
            self.assertNotIn('build_targets', imported[0])
            self.assertEqual(ninja_deps.read(fresh / 'out/Default/.siso_deps').paths,
                             ['obj.o', '../../header.h'])


@unittest.skipUnless(os.environ.get('LUNE_TEST_NINJA') and os.environ.get('LUNE_TEST_CLANG'),
                     'Set pinned Ninja and Clang paths for native dependency-log interoperability')
class NativeCompilerTests(unittest.TestCase):
    def test_noop_after_donor_disappears_and_changed_header_rebuilds(self):
        ninja = str(Path(os.environ['LUNE_TEST_NINJA']).resolve())
        clang = str(Path(os.environ['LUNE_TEST_CLANG']).resolve())
        sdk = subprocess.check_output(['xcrun', '--sdk', 'macosx', '--show-sdk-path'], text=True).strip()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            old, fresh = root / 'old', root / 'fresh'
            out = old / 'out/Default'
            out.mkdir(parents=True)
            (old / 'main.cc').write_text('#include "value.h"\nint main() { return VALUE; }\n')
            (old / 'value.h').write_text('#define VALUE 1\n')
            (old / 'compile.py').write_text(
                'import pathlib, subprocess\n'
                'root = pathlib.Path("../..").resolve()\n'
                f'subprocess.run([{clang!r}, "-isysroot", {sdk!r}, "-MMD", "-MF", '
                '"probe.d", "-o", "probe", str(root / "main.cc")], check=True)\n')
            (out / 'build.ninja').write_text(
                f'rule compile\n  command = {sys.executable} ../../compile.py\n'
                '  depfile = probe.d\n  deps = gcc\n'
                'build probe: compile ../../main.cc\ndefault probe\n')
            def build(folder):
                return subprocess.check_output([ninja, '-d', 'explain', '-C', str(folder)],
                                               text=True, stderr=subprocess.STDOUT)
            build(out)
            before = (out / 'probe').read_bytes()
            shutil.copytree(old, fresh, copy_function=shutil.copy2)
            fresh_out = fresh / 'out/Default'
            deps = ninja_deps.read(fresh_out / '.ninja_deps')
            self.assertTrue(any(str(old) in name for name in deps.paths))
            ninja_deps.write(fresh_out / '.ninja_deps', deps,
                lambda name: cache_reuse.relocated(name, [str(old)], fresh, fresh_out))
            self.assertIn('no work to do', build(fresh_out))
            self.assertEqual((fresh_out / 'probe').read_bytes(), before)
            removed = root / 'removed-donor'
            old.rename(removed)
            self.assertIn('no work to do', build(fresh_out))
            self.assertEqual((fresh_out / 'probe').read_bytes(), before)
            removed.rename(old)
            # The donor still exists and is unchanged: dependencies must now
            # follow the fresh header rather than silently reading the donor.
            header = fresh / 'value.h'
            header.write_text('#define VALUE 2\n')
            os.utime(header, ns=(time.time_ns(), time.time_ns()))
            self.assertNotIn('no work to do', build(fresh_out))
            self.assertEqual(subprocess.run([fresh_out / 'probe']).returncode, 2)
            old.rename(root / 'removed-donor')
            self.assertIn('no work to do', build(fresh_out))


if __name__ == '__main__':
    unittest.main()
