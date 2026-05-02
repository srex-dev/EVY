"""Tests for the LLM/RAG prompt tuning harness."""
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "tune_llm_rag_prompts.py"
SPEC = importlib.util.spec_from_file_location("tune_llm_rag_prompts", SCRIPT_PATH)
tuning = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(tuning)


def test_tuning_report_passes_retrieval_without_required_llm(tmp_path):
    args = tuning.parse_args(
        [
            "--sqlite-db",
            str(tmp_path / "tuning.sqlite"),
            "--llm-url",
            "http://127.0.0.1:1",
            "--report",
            str(tmp_path / "report.json"),
        ]
    )

    report = tuning.build_report(args)

    assert report["pass"] is True
    assert report["retrieval_summary"]["pass"] is True
    assert report["llm_health"]["available"] is False
    assert report["prompt_summary"]["total"] == 0


def test_tuning_report_can_require_llm(tmp_path):
    args = tuning.parse_args(
        [
            "--sqlite-db",
            str(tmp_path / "tuning.sqlite"),
            "--llm-url",
            "http://127.0.0.1:1",
            "--require-llm",
            "--report",
            str(tmp_path / "report.json"),
        ]
    )

    report = tuning.build_report(args)

    assert report["pass"] is False
    assert report["retrieval_summary"]["pass"] is True
    assert report["llm_health"]["available"] is False


def test_response_scoring_checks_required_and_forbidden_terms():
    case = {
        "response_should_include": ["shelter"],
        "response_should_avoid": ["internet"],
    }

    passing = tuning.score_response("Go to the nearest shelter named by officials.", case, 160)
    failing = tuning.score_response("Search the internet later.", case, 160)

    assert passing["pass"] is True
    assert failing["pass"] is False
    assert failing["missing_required_terms"] == ["shelter"]
    assert failing["found_forbidden_terms"] == ["internet"]
