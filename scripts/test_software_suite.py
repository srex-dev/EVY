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
            {"name": "bitnet_sms_benchmark_tests", "cmd": pytest + ["backend/tests/test_bitnet_sms_benchmark.py", "-q"]},
            {"name": "bitnet_validation_script_tests", "cmd": pytest + ["backend/tests/test_bitnet_validation_script.py", "-q"]},
            {"name": "hardware_suite_report_tests", "cmd": pytest + ["backend/tests/test_hardware_suite_report.py", "-q"]},
            {"name": "knowledge_pack_tests", "cmd": pytest + ["backend/tests/test_knowledge_pack.py", "-q"]},
            {"name": "knowledge_pack_script_tests", "cmd": pytest + ["backend/tests/test_knowledge_pack_script.py", "-q"]},
            {"name": "llm_inference_tests", "cmd": pytest + ["backend/tests/test_llm_inference.py", "-q"]},
            {"name": "llm_rag_tuning_script_tests", "cmd": pytest + ["backend/tests/test_llm_rag_tuning_script.py", "-q"]},
            {"name": "observability_boot_tests", "cmd": pytest + ["backend/tests/test_observability_and_boot.py", "-q"]},
            {"name": "observability_profile_tests", "cmd": pytest + ["backend/tests/test_observability_profile.py", "-q"]},
            {"name": "router_enhancement_tests", "cmd": pytest + ["backend/tests/test_message_router_enhancements.py", "-q"]},
            {"name": "routing_model_tests", "cmd": pytest + ["backend/tests/test_routing_and_models.py", "-q"]},
            {"name": "sms_gateway_tests", "cmd": pytest + ["backend/tests/test_sms_gateway.py", "-q"]},
            {"name": "sqlite_rag_store_tests", "cmd": pytest + ["backend/tests/test_sqlite_rag_store.py", "-q"]},
        ],
        "integration": [
            {"name": "integration_tests", "cmd": pytest + ["backend/tests/test_integration.py", "-q"]},
            {"name": "pre_hardware_smoke", "cmd": [sys.executable, "scripts/pre_hardware_smoke.py", "--timeout", "30"]},
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


def evaluate_release_gates(results: List[Dict]) -> Dict:
    """Evaluate release gates from suite results."""
    by_name = {item["name"]: item for item in results}
    gates = []

    def add_gate(gate_id: str, passed: bool, detail: str) -> None:
        gates.append({"gate": gate_id, "pass": passed, "detail": detail})

    required = [
        "bitnet_sms_benchmark_tests",
        "bitnet_validation_script_tests",
        "hardware_suite_report_tests",
        "knowledge_pack_tests",
        "knowledge_pack_script_tests",
        "llm_inference_tests",
        "llm_rag_tuning_script_tests",
        "observability_boot_tests",
        "observability_profile_tests",
        "router_enhancement_tests",
        "routing_model_tests",
        "sms_gateway_tests",
        "sqlite_rag_store_tests",
        "integration_tests",
        "pre_hardware_smoke",
    ]
    for name in required:
        item = by_name.get(name)
        add_gate(
            f"required_{name}",
            bool(item and item["pass"]),
            f"{name} must pass",
        )

    perf = by_name.get("integration_performance_subset")
    add_gate(
        "performance_subset_under_30s",
        bool(perf and perf["pass"] and perf["elapsed_seconds"] <= 30),
        "integration performance subset must pass within 30s",
    )

    resilience = by_name.get("message_queue_retries")
    add_gate(
        "retry_path_passes",
        bool(resilience and resilience["pass"]),
        "retry and dead-letter behavior test must pass",
    )

    return {"pass": all(g["pass"] for g in gates), "gates": gates}


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
    summary["release_gates"] = evaluate_release_gates(results)

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps({"stage": args.stage, "pass": passed, "report": str(report_path)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
