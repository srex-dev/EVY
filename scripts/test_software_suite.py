#!/usr/bin/env python3
"""Run EVY software validation stages and write a JSON report."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List


def run_command(name: str, command: List[str], cwd: str) -> Dict:
    start = time.time()
    proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    elapsed = round(time.time() - start, 3)
    return {
        "name": name,
        "command": " ".join(command),
        "exit_code": proc.returncode,
        "elapsed_seconds": elapsed,
        "pass": proc.returncode == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def build_stage_commands(stage: str) -> List[Dict[str, List[str]]]:
    pytest = [sys.executable, "-m", "pytest"]
    commands = {
        "premerge": [
            {"name": "imports_smoke", "cmd": [sys.executable, "-c", "import backend.shared.config; print('ok')"]},
            {"name": "router_import_smoke", "cmd": [sys.executable, "-c", "import backend.services.message_router.main; print('ok')"]},
        ],
        "regression": [
            {"name": "llm_inference_tests", "cmd": pytest + ["backend/tests/test_llm_inference.py", "-q"]},
            {"name": "router_enhancement_tests", "cmd": pytest + ["backend/tests/test_message_router_enhancements.py", "-q"]},
            {"name": "routing_model_tests", "cmd": pytest + ["backend/tests/test_routing_and_models.py", "-q"]},
            {"name": "sms_gateway_tests", "cmd": pytest + ["backend/tests/test_sms_gateway.py", "-q"]},
        ],
        "integration": [
            {"name": "integration_tests", "cmd": pytest + ["backend/tests/test_integration.py", "-q"]},
        ],
        "performance": [
            {"name": "integration_performance_subset", "cmd": pytest + ["backend/tests/test_integration.py::TestPerformanceIntegration", "-q"]},
        ],
        "resilience": [
            {"name": "redis_fallback_regression", "cmd": pytest + ["backend/tests/test_sms_gateway.py::TestSMSGateway::test_gateway_initialization", "-q"]},
            {"name": "message_queue_retries", "cmd": pytest + ["backend/tests/test_sms_gateway.py::TestMessageQueue::test_mark_failed_retry", "-q"]},
        ],
    }

    if stage == "full":
        merged: List[Dict[str, List[str]]] = []
        for key in ["premerge", "regression", "integration", "performance", "resilience"]:
            merged.extend(commands[key])
        return merged

    return commands[stage]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run software validation suite.")
    parser.add_argument(
        "--stage",
        choices=["premerge", "regression", "integration", "performance", "resilience", "full"],
        default="full",
        help="Validation stage to run",
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root path",
    )
    parser.add_argument(
        "--report",
        default="data/lilevy/software_reports/software_suite_report.json",
        help="Output JSON report path",
    )
    args = parser.parse_args()

    workspace = str(Path(args.workspace).resolve())
    stage_commands = build_stage_commands(args.stage)

    results = []
    for item in stage_commands:
        print(f"[RUN] {item['name']}")
        results.append(run_command(item["name"], item["cmd"], cwd=workspace))

    passed = all(r["pass"] for r in results)
    summary = {
        "test": "software_validation_suite",
        "stage": args.stage,
        "pass": passed,
        "total": len(results),
        "passed": sum(1 for r in results if r["pass"]),
        "failed": sum(1 for r in results if not r["pass"]),
        "results": results,
    }

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps({"stage": args.stage, "pass": passed, "report": str(report_path)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
