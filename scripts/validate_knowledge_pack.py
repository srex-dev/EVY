#!/usr/bin/env python3
"""Validate and optionally import an EVY knowledge pack into SQLite RAG."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.rag_service.knowledge_pack import validate_knowledge_pack
from backend.services.rag_service.sqlite_rag_store import SQLiteRAGStore


DEFAULT_PACK = ROOT / "examples" / "knowledge_packs" / "evy_local_emergency_sample"
DEFAULT_DB = ROOT / "data" / "lilevy" / "sqlite_rag.db"
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "knowledge_pack_validation_report.json"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate EVY knowledge pack and optional SQLite import.")
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK, help="Knowledge pack directory or zip file")
    parser.add_argument("--sqlite-db", type=Path, default=DEFAULT_DB, help="SQLite RAG DB path for import/search")
    parser.add_argument("--require-signature", action="store_true", help="Require manifest signature metadata")
    parser.add_argument("--import-sqlite", action="store_true", help="Import the pack into SQLite RAG after validation")
    parser.add_argument("--search", default=None, help="Search query to run after import")
    parser.add_argument("--top-k", type=int, default=3, help="Search result limit")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Output JSON report path")
    return parser.parse_args(argv)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    validation = validate_knowledge_pack(args.pack, require_signature=args.require_signature)
    import_result: Optional[dict[str, Any]] = None
    search_result: Optional[dict[str, Any]] = None
    pass_checks = [validation["valid"]]

    if args.import_sqlite:
        store = SQLiteRAGStore(args.sqlite_db)
        import_result = store.import_pack(args.pack, require_signature=args.require_signature)
        pass_checks.append(import_result["imported"])

        if args.search:
            result = store.search(args.search, top_k=args.top_k)
            search_result = {
                "query": args.search,
                "top_k": args.top_k,
                "documents": result.documents,
                "scores": result.scores,
                "metadata": result.metadata,
                "pass": len(result.documents) > 0,
            }
            pass_checks.append(search_result["pass"])
    elif args.search:
        search_result = {
            "query": args.search,
            "top_k": args.top_k,
            "documents": [],
            "scores": [],
            "metadata": [],
            "pass": False,
            "error": "--search requires --import-sqlite so the pack is searchable",
        }
        pass_checks.append(False)

    return {
        "test": "knowledge_pack_validation",
        "timestamp": time.time(),
        "elapsed_seconds": round(time.time() - started, 3),
        "pack_path": str(args.pack),
        "sqlite_db": str(args.sqlite_db),
        "require_signature": args.require_signature,
        "validation": validation,
        "import": import_result,
        "search": search_result,
        "pass": all(pass_checks),
    }


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "report": str(args.report)}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
