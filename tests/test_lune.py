"""Fail-closed checks for the development input lock and checkout guardrails."""
import argparse
import importlib.util
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

    def test_unimplemented_pr_is_not_silently_ignored(self):
        name = "manifests/patches.json"
        data = lune.read_json(self.root / name)
        data["pull_requests"] = [{"number": 123}]
        lune.write_json(self.root / name, data)
        self.update_hash(name)
        with self.assertRaisesRegex(ValueError, "replay is not implemented"):
            lune.validate_lock(self.lock)

    def test_short_commit_rejected(self):
        self.lock["components"]["macos"]["commit"] = "abcdef0"
        with self.assertRaisesRegex(ValueError, "full commit"):
            lune.validate_lock(self.lock)

    def test_unrelated_source_ref_rejected(self):
        self.lock["components"]["macos"]["ref"] = "refs/heads/main"
        with self.assertRaisesRegex(ValueError, "permanent input tag"):
            lune.validate_lock(self.lock)

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
