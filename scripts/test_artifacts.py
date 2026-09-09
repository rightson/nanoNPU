"""Reject incomplete, stale or pointer-only physical evidence."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import v0


class ArtifactAcceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.build = self.root / "build"
        self.snapshot = self.build / "attempts/test"
        self.run = self.snapshot / "runs/test"
        inputs = self.snapshot / "RTL/top.sv"
        inputs.parent.mkdir(parents=True)
        inputs.write_text("module top; endmodule\n")
        self.gds = self.run / "final/gds/top.gds"
        self.spefs = [self.run / f"final/spef/{c}/top.spef" for c in ["min", "nom", "max"]]
        summary = self.run / "54-openroad-stapostpnr/summary.rpt"
        for file in [self.gds, *self.spefs, summary]:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b"test fixture content")
        (self.build / "pnr-success.json").write_text(json.dumps({
            "run_dir": str(self.run.relative_to(self.root)),
            "input_manifest": {"RTL/top.sv": hashlib.sha256(inputs.read_bytes()).hexdigest()}}))

    def check(self):
        with patch.object(v0, "ROOT", self.root), patch.object(v0, "BUILD", self.build):
            with contextlib.redirect_stdout(io.StringIO()):
                v0.artifacts()

    def test_complete_file_inventory(self):
        self.check()
        manifest = json.loads((self.build / "artifacts.json").read_text())
        self.assertEqual(len(manifest["spef"]), 3)
        self.assertTrue(manifest["sta"][0]["path"].endswith("/summary.rpt"))

    def test_missing_extraction_corner(self):
        self.spefs[0].unlink()
        with self.assertRaisesRegex(RuntimeError, "three extracted"):
            self.check()

    def test_modified_input_snapshot(self):
        (self.snapshot / "RTL/top.sv").write_text("changed RTL")
        with self.assertRaisesRegex(RuntimeError, "input changed"):
            self.check()

    def test_lfs_pointer_is_not_gds(self):
        self.gds.write_text("version https://git-lfs.github.com/spec/v1\n")
        with self.assertRaisesRegex(RuntimeError, "LFS pointer"):
            self.check()


if __name__ == "__main__":
    unittest.main()
