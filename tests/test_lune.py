"""Fail-closed checks for the development input lock and checkout guardrails."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("lune", Path(__file__).parents[1] / "scripts/lune.py")
lune = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lune)


class LockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.lock = lune.read_json(lune.LOCK)
        for name in self.lock["files"]:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(lune.ROOT / name, dest)
        self.root_patch = patch.object(lune, "ROOT", self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.tmp.cleanup()

    def update_hash(self, name):
        self.lock["files"][name] = lune.digest(self.root / name)

    def test_repository_lock_is_valid(self):
        lune.validate_lock(self.lock)

    def forward_port(self, update_archives=True):
        previous = self.lock['chromium_version']
        major = max(int(previous.split('.')[0]),
                    int(self.lock['ungoogled']['tag'].split('.')[0])) + 1
        target = f'{major}.0.9999.1'
        self.lock['chromium_version'] = target
        review = 'agent-docs/project/builds/forward-port-test.md'
        path = self.root / review
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('Reviewed test fixture, not release evidence.\n')
        self.update_hash(review)
        self.lock['chromium_forward_port'] = {
            'review_status': 'reviewed-port',
            'base_core_commit': self.lock['components']['helium']['upstream_commit'],
            'chromium_commit': 'a' * 40,
            'review': review,
        }
        if update_archives:
            for name in self.lock['download_configs']:
                path = self.root / name
                path.write_text(path.read_text().replace(previous, target))
                self.update_hash(name)

    def test_reviewed_forward_port_is_valid(self):
        self.forward_port()
        lune.validate_lock(self.lock)

    def test_unreviewed_version_mismatch_is_rejected(self):
        self.forward_port()
        del self.lock['chromium_forward_port']
        with self.assertRaisesRegex(ValueError, 'reviewed forward-port is required'):
            lune.validate_lock(self.lock)

    def test_forward_port_cannot_reuse_old_archives(self):
        self.forward_port(update_archives=False)
        with self.assertRaisesRegex(ValueError, 'source archive differs'):
            lune.validate_lock(self.lock)

    def test_forward_port_cannot_downgrade(self):
        self.forward_port()
        major = int(self.lock['ungoogled']['tag'].split('.')[0]) - 1
        self.lock['chromium_version'] = f'{major}.0.0.1'
        with self.assertRaisesRegex(ValueError, 'cannot downgrade'):
            lune.validate_lock(self.lock)

    def test_forward_port_metadata_cannot_survive_matching_upstream(self):
        self.forward_port()
        self.lock['chromium_version'] = self.lock['ungoogled']['tag'].rsplit('-', 1)[0]
        with self.assertRaisesRegex(ValueError, 'stale forward-port metadata'):
            lune.validate_lock(self.lock)

    def test_forward_port_requires_immutable_commits_and_review(self):
        self.forward_port()
        port = self.lock['chromium_forward_port']
        for field in ('base_core_commit', 'chromium_commit'):
            original = port[field]
            port[field] = 'main'
            with self.assertRaisesRegex(ValueError, 'full base core and Chromium commit'):
                lune.validate_lock(self.lock)
            port[field] = original
        del self.lock['files'][port['review']]
        with self.assertRaisesRegex(ValueError, 'hash-locked build review'):
            lune.validate_lock(self.lock)

    def test_forward_port_review_edits_require_rehash(self):
        self.forward_port()
        (self.root / self.lock['chromium_forward_port']['review']).write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Locked input changed'):
            lune.validate_lock(self.lock)

    def test_forward_port_cannot_lose_base_ancestry(self):
        self.forward_port()
        with patch.object(lune, 'ancestors', side_effect=[True, False]):
            with self.assertRaisesRegex(ValueError, 'ancestry must retain'):
                lune.validate_chromium_port(self.lock, git_objects=True)

    def test_forward_port_base_must_match_ungoogled_version(self):
        self.forward_port()
        with patch.object(lune, 'ancestors', return_value=True), \
                patch.object(lune, 'git', return_value='156.0.8078.79'):
            with self.assertRaisesRegex(ValueError, 'base version differs'):
                lune.validate_chromium_port(self.lock, git_objects=True)

    def test_modified_product_rejected(self):
        (self.root / "config/product.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "Locked input changed"):
            lune.validate_lock(self.lock)

    def test_omitted_hash_rejected(self):
        del self.lock["files"]["config/product.json"]
        with self.assertRaisesRegex(ValueError, "missing required"):
            lune.validate_lock(self.lock)

    def test_unpinned_download_rejected_even_after_rehash(self):
        name = "manifests/downloads-arm64.ini"
        path = self.root / name
        path.write_text(path.read_text().replace("sha256 =", "hash_url =", 1))
        self.update_hash(name)
        with self.assertRaisesRegex(ValueError, "pinned SHA"):
            lune.validate_lock(self.lock)

    def test_empty_download_manifest_rejected(self):
        name = "manifests/downloads-x64.ini"
        (self.root / name).write_text("")
        self.update_hash(name)
        with self.assertRaisesRegex(ValueError, "missing required downloads"):
            lune.validate_lock(self.lock)

    def test_invalid_pr_is_not_silently_ignored(self):
        name = "manifests/patches.json"
        data = lune.read_json(self.root / name)
        data["pull_requests"] = [{"number": 123}]
        lune.write_json(self.root / name, data)
        self.update_hash(name)
        with self.assertRaisesRegex(ValueError, "unique ID"):
            lune.validate_lock(self.lock)

    def change_selections(self, fn):
        name = "manifests/patches.json"
        data = lune.read_json(self.root / name)
        fn(data)
        lune.write_json(self.root / name, data)
        self.update_hash(name)

    def test_selection_cannot_point_at_another_component_commit(self):
        self.change_selections(lambda d: d["integration"].update(commit="a" * 40))
        with self.assertRaisesRegex(ValueError, "locked integration commit"):
            lune.validate_lock(self.lock)

    def test_unpinned_pr_rejected_after_manifest_rehash(self):
        self.change_selections(lambda d: d["pull_requests"][0].update(head="main"))
        with self.assertRaisesRegex(ValueError, "full base/head"):
            lune.validate_lock(self.lock)

    def test_missing_composed_patch_rejected(self):
        self.change_selections(lambda d: d["integration"]["patches"].pop(0))
        with self.assertRaisesRegex(ValueError, "missing from the composition"):
            lune.validate_lock(self.lock)

    def test_dependency_order_is_enforced(self):
        self.change_selections(lambda d: d["pull_requests"][0].update(depends_on=["missing"]))
        with self.assertRaisesRegex(ValueError, "dependencies must precede"):
            lune.validate_lock(self.lock)

    def test_duplicate_patch_rejected(self):
        self.change_selections(lambda d: d["integration"]["patches"].append(d["integration"]["patches"][0]))
        with self.assertRaisesRegex(ValueError, "nonempty and unique"):
            lune.validate_lock(self.lock)

    def test_short_commit_rejected(self):
        self.lock["components"]["macos"]["commit"] = "abcdef0"
        with self.assertRaisesRegex(ValueError, "full commit"):
            lune.validate_lock(self.lock)

    def test_unrelated_source_ref_rejected(self):
        self.lock["components"]["macos"]["ref"] = "refs/heads/main"
        with self.assertRaisesRegex(ValueError, "permanent input tag"):
            lune.validate_lock(self.lock)

    def test_toolchain_change_requires_review(self):
        product = {"xcode_version": "27.2", "xcode_build": "27B52", "macos_sdk_version": "27.2"}
        lune.check_toolchain("Xcode 27.2\nBuild version 27B52", "27.2", product)
        for version, sdk in [("Xcode 27.3\nBuild version 27C1", "27.2"), ("Xcode 27.2\nBuild version 27B52", "27.3")]:
            with self.assertRaisesRegex(ValueError, "Toolchain differs"):
                lune.check_toolchain(version, sdk, product)

    def test_discovery_detects_chromium_lag_even_with_latest_ungoogled(self):
        self.lock['chromium_version'] = '157.0.8103.38'
        response = io.BytesIO(json.dumps([{"version": "158.0.8127.18"}]).encode())
        with patch.object(lune, "git", side_effect=[
                "upstream/ungoogled/157.0.8103.38-1",
                self.lock["ungoogled"]["commit"],
                self.lock["components"]["helium"]["commit"]]), \
                patch.object(lune, "ancestors", return_value=True), \
                patch.object(lune, "read_json", return_value=self.lock), \
                patch.object(lune.urllib.request, "urlopen", return_value=response), \
                patch("sys.stdout", new_callable=io.StringIO) as output:
            with self.assertRaisesRegex(ValueError, "behind macOS stable"):
                lune.discover(None)
            report = json.loads(output.getvalue())
            self.assertTrue(report["locked_ungoogled_is_current"])
            self.assertFalse(report["locked_chromium_is_current"])

    def test_numeric_release_order(self):
        tags = ["99.0.4844.84-1", "157.0.8103.38-2", "157.0.8103.38-10"]
        self.assertEqual(max(tags, key=lune.version_tuple), tags[-1])
        with self.assertRaises(ValueError):
            lune.version_tuple("157.0.8103.38-beta")

    def test_dirty_checkout_is_preserved(self):
        with patch.object(lune, "git", side_effect=[self.lock["components"]["macos"]["commit"], " M patches/series"]):
            with self.assertRaisesRegex(ValueError, "Dirty component"):
                lune.check_checkout(self.root, self.lock)

    def test_wrong_checkout_is_preserved(self):
        with patch.object(lune, "git", return_value="a" * 40):
            with self.assertRaisesRegex(ValueError, "Wrong commit"):
                lune.check_checkout(self.root, self.lock)

    def test_dirty_orchestrator_blocks_build(self):
        with patch.object(lune, "git", return_value=" M scripts/lune.py"):
            with self.assertRaisesRegex(ValueError, "Commit the reviewed"):
                lune.require_clean_orchestrator()

    def test_preparation_never_deletes_existing_tree(self):
        dest = self.root / ".work/arm64/macos"
        (dest / "build/src").mkdir(parents=True)
        marker = dest / "build/src/local-work.cc"
        marker.write_text("local changes")
        with patch.object(lune, "LOCK", lune.LOCK), patch.object(lune, "doctor"), patch.object(lune, "checkout"), patch.object(lune, "require_clean_orchestrator"):
            with self.assertRaisesRegex(ValueError, "refusing to delete sources"):
                lune.prepare(argparse.Namespace(arch="arm64"))
        self.assertEqual(marker.read_text(), "local changes")


if __name__ == "__main__":
    unittest.main()
