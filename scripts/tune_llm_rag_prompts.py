#!/usr/bin/env python3
"""Evaluate EVY retrieval and prompt templates for SMS-sized LLM answers.

This is a pre-hardware tuning harness. It always runs retrieval checks against a
SQLite knowledge pack. If a local LLM service is running, it also runs prompt
variants through `/inference`; otherwise the report records that LLM tuning is
pending.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.rag_service.sqlite_rag_store import SQLiteRAGStore


DEFAULT_PACK = ROOT / "examples" / "knowledge_packs" / "evy_local_emergency_sample"
DEFAULT_CASES_FILE = ROOT / "examples" / "evaluation" / "llm_rag_tuning_cases.json"
DEFAULT_DB = ROOT / "data" / "lilevy" / "llm_rag_tuning.sqlite"
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "llm_rag_tuning_report.json"

DEFAULT_CASES = [
    {
        "id": "storm_shelter",
        "query": "Where should I go during a storm warning?",
        "retrieval_query": "storm shelter local officials",
        "category": "emergency",
        "expected_terms": ["shelter", "local officials"],
    },
    {
        "id": "boil_water",
        "query": "How do I make water safe after flooding?",
        "retrieval_query": "boil water flooding",
        "category": "health",
        "expected_terms": ["water", "boil"],
    },
    {
        "id": "plus_code",
        "query": "How should EVY handle 86HVCWC8+R9 in an SMS?",
        "retrieval_query": "plus code location",
        "category": "operations",
        "expected_terms": ["plus code", "location"],
    },
]

PROMPT_TEMPLATES = {
    "grounded_sms": (
        "Answer the user's question using only the local context. "
        "Reply in one helpful SMS under 160 characters. If context is not enough, say so safely."
    ),
    "emergency_sms": (
        "You are EVY, an offline emergency SMS assistant. "
        "Give one direct, safety-first answer under 160 characters using the local context."
    ),
}


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune EVY LLM prompts and RAG retrieval")
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK, help="Knowledge pack directory or zip")
    parser.add_argument("--sqlite-db", type=Path, default=DEFAULT_DB, help="SQLite tuning DB path")
    parser.add_argument("--cases-file", type=Path, default=DEFAULT_CASES_FILE, help="JSON list of tuning cases")
    parser.add_argument("--llm-url", default="http://127.0.0.1:18002", help="LLM service base URL")
    parser.add_argument("--require-llm", action="store_true", help="Fail when LLM service is unavailable")
    parser.add_argument("--top-k", type=int, default=2, help="Retrieval result count")
    parser.add_argument("--max-length", type=int, default=160, help="SMS response size limit")
    parser.add_argument("--temperature", type=float, default=0.2, help="LLM temperature")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Output JSON report path")
    return parser.parse_args(argv)


def load_cases(path: Optional[Path]) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return list(DEFAULT_CASES)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError("Cases file must contain a JSON list")
    return loaded


def score_response(response_text: str, case: dict[str, Any], max_length: int) -> dict[str, Any]:
    """Score an LLM answer for SMS size and expected safety/content traits."""
    normalized = response_text.lower()
    should_include = [term.lower() for term in case.get("response_should_include", [])]
    should_avoid = [term.lower() for term in case.get("response_should_avoid", [])]
    matched_required = [term for term in should_include if term in normalized]
    missing_required = [term for term in should_include if term not in normalized]
    found_forbidden = [term for term in should_avoid if term in normalized]
    length_ok = 0 < len(response_text) <= int(case.get("response_max_chars", max_length))
    return {
        "length_ok": length_ok,
        "response_length": len(response_text),
        "max_chars": int(case.get("response_max_chars", max_length)),
        "matched_required_terms": matched_required,
        "missing_required_terms": missing_required,
        "found_forbidden_terms": found_forbidden,
        "pass": length_ok and not missing_required and not found_forbidden,
    }


def check_llm_health(base_url: str, timeout: float) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/health"
    started = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "available": False,
            "url": url,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": str(exc),
        }

    details = payload.get("details") or {}
    service_name = payload.get("service_name")
    provider = details.get("provider")
    return {
        "available": payload.get("status") == "healthy" and (service_name == "llm-inference" or bool(provider)),
        "url": url,
        "elapsed_seconds": round(time.time() - started, 3),
        "service_name": service_name,
        "status": payload.get("status"),
        "provider": provider,
        "model": details.get("model"),
        "bitnet": details.get("bitnet"),
    }


def evaluate_retrieval(store: SQLiteRAGStore, case: dict[str, Any], top_k: int) -> dict[str, Any]:
    retrieval_query = case.get("retrieval_query") or case["query"]
    result = store.search(retrieval_query, top_k=top_k, category=case.get("category"))
    joined_docs = "\n".join(result.documents).lower()
    expected_terms = [term.lower() for term in case.get("expected_terms", [])]
    matched_terms = [term for term in expected_terms if term in joined_docs]
    missing_terms = [term for term in expected_terms if term not in joined_docs]
    return {
        "case_id": case["id"],
        "query": case["query"],
        "retrieval_query": retrieval_query,
        "category": case.get("category"),
        "documents": result.documents,
        "scores": result.scores,
        "metadata": result.metadata,
        "expected_terms": expected_terms,
        "response_should_include": case.get("response_should_include", []),
        "response_should_avoid": case.get("response_should_avoid", []),
        "response_max_chars": case.get("response_max_chars"),
        "matched_terms": matched_terms,
        "missing_terms": missing_terms,
        "pass": bool(result.documents) and not missing_terms,
    }


def post_llm(
    base_url: str,
    prompt: str,
    context: str,
    timeout: float,
    max_length: int,
    temperature: float,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/inference"
    payload = {
        "prompt": prompt,
        "context": context,
        "max_length": max_length,
        "temperature": temperature,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            status_code = response.status
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "pass": False,
            "status_code": None,
            "latency_seconds": round(time.time() - started, 3),
            "error": str(exc),
        }

    response_text = str(parsed.get("response", "")).strip()
    return {
        "pass": status_code == 200 and 0 < len(response_text) <= max_length,
        "status_code": status_code,
        "latency_seconds": round(time.time() - started, 3),
        "response": response_text,
        "response_length": len(response_text),
        "model_used": parsed.get("model_used"),
        "tokens_used": parsed.get("tokens_used"),
        "processing_time": parsed.get("processing_time"),
        "metadata": parsed.get("metadata"),
    }


def evaluate_prompts(
    args: argparse.Namespace,
    retrieval_results: list[dict[str, Any]],
    llm_health: dict[str, Any],
) -> list[dict[str, Any]]:
    if not llm_health["available"]:
        return []

    prompt_results = []
    for item in retrieval_results:
        context = "\n\n".join(item["documents"])
        for template_name, instruction in PROMPT_TEMPLATES.items():
            prompt = f"{instruction}\n\nQuestion: {item['query']}"
            response = post_llm(
                args.llm_url,
                prompt,
                context,
                args.timeout,
                args.max_length,
                args.temperature,
            )
            if response.get("response"):
                response_score = score_response(response["response"], item, args.max_length)
                response["scoring"] = response_score
                response["pass"] = bool(response.get("pass")) and response_score["pass"]
            prompt_results.append(
                {
                    "case_id": item["case_id"],
                    "template": template_name,
                    "prompt": prompt,
                    "context_length": len(context),
                    **response,
                }
            )
    return prompt_results


def summarize_retrieval(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(results),
        "passed": sum(1 for item in results if item["pass"]),
        "failed": sum(1 for item in results if not item["pass"]),
        "pass": all(item["pass"] for item in results),
    }


def summarize_prompts(results: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [item["latency_seconds"] for item in results if item.get("status_code") == 200]
    return {
        "total": len(results),
        "passed": sum(1 for item in results if item.get("pass")),
        "failed": sum(1 for item in results if not item.get("pass")),
        "latency_seconds": {
            "mean": round(statistics.mean(latencies), 3) if latencies else 0.0,
            "max": round(max(latencies), 3) if latencies else 0.0,
        },
        "pass": bool(results) and all(item.get("pass") for item in results),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    store = SQLiteRAGStore(args.sqlite_db)
    import_result = store.import_pack(args.pack, require_signature=False)
    cases = load_cases(args.cases_file)
    retrieval_results = [evaluate_retrieval(store, case, args.top_k) for case in cases]
    retrieval_summary = summarize_retrieval(retrieval_results)
    llm_health = check_llm_health(args.llm_url, args.timeout)
    prompt_results = evaluate_prompts(args, retrieval_results, llm_health)
    prompt_summary = summarize_prompts(prompt_results)

    if prompt_results:
        llm_gate = prompt_summary["pass"]
    elif args.require_llm:
        llm_gate = False
    else:
        llm_gate = True

    report_pass = import_result["imported"] and retrieval_summary["pass"] and llm_gate
    return {
        "test": "llm_rag_prompt_tuning",
        "started_at": started,
        "finished_at": time.time(),
        "duration_seconds": round(time.time() - started, 3),
        "configuration": {
            "pack": str(args.pack),
            "sqlite_db": str(args.sqlite_db),
            "llm_url": args.llm_url,
            "top_k": args.top_k,
            "max_length": args.max_length,
            "temperature": args.temperature,
            "require_llm": args.require_llm,
        },
        "import": import_result,
        "retrieval_summary": retrieval_summary,
        "retrieval_results": retrieval_results,
        "llm_health": llm_health,
        "prompt_summary": prompt_summary,
        "prompt_results": prompt_results,
        "pass": report_pass,
    }


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "report": str(args.report)}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
