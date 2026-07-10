from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from verify_design_pack import validate_workspace
from test_generate_dashboard import make_workspace


class SparseValidatorTests(unittest.TestCase):
    def test_writer_ready_requires_no_blocker_and_output(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d), handoff=True)
            p = ws / "00_DIMENSION_INDEX.md"
            t = p.read_text().replace(
                "| SCOPE-01 | Methods | scoped handoff | writer-ready | M-01 | none | none | none | 04_WRITING_DESIGN_PACK.md#Scoped Handoff |",
                "| SCOPE-01 | Methods | scoped handoff | writer-ready | M-01 | none | blocker | none | none |",
            )
            p.write_text(t)
            self.assertTrue(
                any("writer-ready scope requires" in x for x in validate_workspace(ws))
            )

    def test_legacy_is_one_bounded_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            p = ws / "00_DIMENSION_INDEX.md"
            p.write_text(
                p.read_text().replace(
                    "Workspace schema version: 0.2", "Schema version: 1"
                )
            )
            errs = validate_workspace(ws)
            self.assertEqual(len([e for e in errs if "legacy workspace" in e]), 1)

    def test_active_claim_needs_boundary_fields(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            p = ws / "02_CLAIM_EVIDENCE_BOUNDARY.md"
            t = p.read_text()
            marker = "## Claim Records"
            pos = t.find(marker)
            sep = t.find("\n", t.find("|---", pos))
            t = (
                t[: sep + 1]
                + "| C-01 | a claim | none | none | SCOPE-01 | none | none | none | none | active | model-derived | evidence-supported | confirmed | 00_PROJECT_ROUTE.md#Project Brief |\n"
                + t[sep + 1 :]
            )
            p.write_text(t)
            self.assertTrue(
                any(
                    "active/downgraded claim lacks" in x for x in validate_workspace(ws)
                )
            )

    def test_partial_blank_conditional_row_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(Path(d))
            p = ws / "00_DIMENSION_INDEX.md"
            text = p.read_text()
            pos = text.find("## Active Calibration Lenses")
            sep = text.find("\n", text.find("|---", pos))
            text = (
                text[: sep + 1] + "| venue-template | TODO | none |\n" + text[sep + 1 :]
            )
            p.write_text(text)
            self.assertTrue(
                any(
                    "populated row contains blank/TODO" in x
                    for x in validate_workspace(ws)
                )
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
