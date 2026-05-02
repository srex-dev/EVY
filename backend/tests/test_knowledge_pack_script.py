"""Tests for the knowledge-pack validation CLI."""
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "validate_knowledge_pack.py"
SPEC = importlib.util.spec_from_file_location("validate_knowledge_pack_script", SCRIPT_PATH)
validate_pack_script = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validate_pack_script)


def test_default_sample_pack_validates_with_required_signature(tmp_path):
    args = validate_pack_script.parse_args(
        [
            "--require-signature",
            "--report",
            str(tmp_path / "report.json"),
        ]
    )

    report = validate_pack_script.build_report(args)

    assert report["pass"] is True
    assert report["validation"]["valid"] is True
    assert report["validation"]["document_count"] == 7


def test_script_imports_sample_pack_and_searches_sqlite(tmp_path):
    args = validate_pack_script.parse_args(
        [
            "--require-signature",
            "--import-sqlite",
            "--sqlite-db",
            str(tmp_path / "rag.db"),
            "--search",
            "boil water",
            "--report",
            str(tmp_path / "report.json"),
        ]
    )

    report = validate_pack_script.build_report(args)

    assert report["pass"] is True
    assert report["import"]["imported"] is True
    assert report["search"]["pass"] is True
    assert any("Water safety guidance" in doc for doc in report["search"]["documents"])
