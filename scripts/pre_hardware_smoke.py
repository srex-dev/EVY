"""Run a deterministic pre-hardware EVY smoke test.

This launches the real API gateway, SMS gateway, message router, and privacy
filter as local processes. LLM and RAG are served by deterministic local stubs
so the smoke test does not require hardware, Redis, Ollama, OpenAI, or a
populated vector database.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "pre_hardware_smoke_report.json"


@dataclass
class ServiceProcess:
    name: str
    module: str
    port: int
    env: dict[str, str]
    process: subprocess.Popen[str] | None = None

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run EVY pre-hardware smoke flow")
    parser.add_argument("--base-port", type=int, default=18100, help="Base local port for the temporary stack")
    parser.add_argument(
        "--external-api-url",
        help="Use an already-running API gateway instead of launching temporary local services",
    )
    parser.add_argument("--timeout", type=float, default=60.0, help="Seconds to wait for readiness and responses")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="JSON report output path")
    parser.add_argument("--verbose", action="store_true", help="Print service process output while running")
    return parser.parse_args()


def merged_env(extra: dict[str, str]) -> dict[str, str]:
    env = os.environ.copy()
    env.update(extra)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(ROOT) if not existing_pythonpath else f"{ROOT}{os.pathsep}{existing_pythonpath}"
    env["PYTHONUNBUFFERED"] = "1"
    return env


def build_services(base_port: int) -> list[ServiceProcess]:
    api = base_port
    sms = base_port + 1
    router = base_port + 2
    llm = base_port + 3
    rag = base_port + 4
    privacy = base_port + 5

    common_urls = {
        "SMS_GATEWAY_URL": f"http://127.0.0.1:{sms}",
        "MESSAGE_ROUTER_URL": f"http://127.0.0.1:{router}",
        "LLM_INFERENCE_URL": f"http://127.0.0.1:{llm}",
        "RAG_SERVICE_URL": f"http://127.0.0.1:{rag}",
        "PRIVACY_FILTER_URL": f"http://127.0.0.1:{privacy}",
    }

    return [
        ServiceProcess(
            name="stub-llm",
            module="scripts.pre_hardware_stub_services:app",
            port=llm,
            env={"STUB_SERVICE_NAME": "stub-llm"},
        ),
        ServiceProcess(
            name="stub-rag",
            module="scripts.pre_hardware_stub_services:app",
            port=rag,
            env={"STUB_SERVICE_NAME": "stub-rag"},
        ),
        ServiceProcess(
            name="privacy-filter",
            module="backend.services.privacy_filter.main:app",
            port=privacy,
            env={"PRIVACY_FILTER_PORT": str(privacy)},
        ),
        ServiceProcess(
            name="sms-gateway",
            module="backend.services.sms_gateway.main:app",
            port=sms,
            env={
                "SMS_GATEWAY_PORT": str(sms),
                "MESSAGE_ROUTER_URL": common_urls["MESSAGE_ROUTER_URL"],
                "SMS_FORWARD_MAX_RETRIES": "2",
                "SMS_ROUTER_TIMEOUT_SECONDS": "10",
            },
        ),
        ServiceProcess(
            name="message-router",
            module="backend.services.message_router.main:app",
            port=router,
            env={
                "MESSAGE_ROUTER_PORT": str(router),
                "LLM_SERVICE_URL": common_urls["LLM_INFERENCE_URL"],
                "RAG_SERVICE_URL": common_urls["RAG_SERVICE_URL"],
                "SMS_GATEWAY_URL": common_urls["SMS_GATEWAY_URL"],
                "PRIVACY_FILTER_URL": common_urls["PRIVACY_FILTER_URL"],
            },
        ),
        ServiceProcess(
            name="api-gateway",
            module="backend.api_gateway.main:app",
            port=api,
            env={
                "API_GATEWAY_PORT": str(api),
                **common_urls,
            },
        ),
    ]


def start_service(service: ServiceProcess, verbose: bool) -> None:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        service.module,
        "--host",
        "127.0.0.1",
        "--port",
        str(service.port),
        "--log-level",
        "warning",
    ]
    service.process = subprocess.Popen(
        cmd,
        cwd=ROOT,
        env=merged_env(service.env),
        text=True,
        stdout=stdout,
        stderr=stderr,
    )


def stop_services(services: list[ServiceProcess]) -> None:
    for service in reversed(services):
        process = service.process
        if not process or process.poll() is not None:
            continue
        process.terminate()

    deadline = time.monotonic() + 10
    for service in reversed(services):
        process = service.process
        if not process:
            continue
        remaining = max(0.1, deadline - time.monotonic())
        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def wait_for_health(services: list[ServiceProcess], timeout: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    health: dict[str, Any] = {}
    with httpx.Client(timeout=2.0) as client:
        while time.monotonic() < deadline:
            all_ready = True
            for service in services:
                if service.name in health:
                    continue
                process = service.process
                if process and process.poll() is not None:
                    raise RuntimeError(f"{service.name} exited early with code {process.returncode}")
                try:
                    response = client.get(f"{service.url}/health")
                    if response.status_code == 200:
                        health[service.name] = response.json()
                    else:
                        all_ready = False
                except httpx.HTTPError:
                    all_ready = False
            if all_ready and len(health) == len(services):
                return health
            time.sleep(0.25)
    missing = sorted({service.name for service in services} - set(health))
    raise TimeoutError(f"Timed out waiting for services: {', '.join(missing)}")


def smoke_messages(run_id: int) -> list[dict[str, Any]]:
    prefix = f"+1555{run_id:07d}"
    return [
        {
            "label": "normal_query",
            "sender": f"{prefix}1",
            "receiver": "+15559990000",
            "content": "Where is the nearest shelter?",
            "priority": "normal",
        },
        {
            "label": "command",
            "sender": f"{prefix}2",
            "receiver": "+15559990000",
            "content": "/status",
            "priority": "normal",
        },
        {
            "label": "emergency",
            "sender": f"{prefix}3",
            "receiver": "+15559990000",
            "content": "EMERGENCY fire in building",
            "priority": "emergency",
        },
    ]


def wait_for_responses(api_url: str, expected_receivers: set[str], timeout: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    with httpx.Client(timeout=5.0) as client:
        while time.monotonic() < deadline:
            history = client.get(f"{api_url}/sms/history", params={"limit": 50}).json()
            sent = history.get("sent", [])
            receivers = {message.get("receiver") for message in sent}
            if expected_receivers.issubset(receivers):
                return history
            time.sleep(0.5)
    raise TimeoutError("Timed out waiting for SMS responses to appear in history")


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    services = build_services(args.base_port)
    api_url = (args.external_api_url or f"http://127.0.0.1:{args.base_port}").rstrip("/")
    started_at = time.time()
    run_id = int(started_at * 1000) % 10_000_000

    try:
        if args.external_api_url:
            health = {}
        else:
            for service in services:
                start_service(service, args.verbose)

            health = wait_for_health(services, args.timeout)

        messages = smoke_messages(run_id)
        receive_results: list[dict[str, Any]] = []
        with httpx.Client(timeout=10.0) as client:
            aggregate_health = client.get(f"{api_url}/services/health").json()
            for message in messages:
                payload = {key: value for key, value in message.items() if key != "label"}
                response = client.post(f"{api_url}/sms/receive", json=payload)
                receive_results.append(
                    {
                        "label": message["label"],
                        "status_code": response.status_code,
                        "response": response.json(),
                    }
                )
                response.raise_for_status()

        history = wait_for_responses(
            api_url,
            expected_receivers={message["sender"] for message in messages},
            timeout=args.timeout,
        )

        sent_by_receiver = {
            message.get("receiver"): message
            for message in history.get("sent", [])
        }
        assertions = {
            "all_messages_accepted": all(result["status_code"] == 200 for result in receive_results),
            "all_responses_visible": all(message["sender"] in sent_by_receiver for message in messages),
            "responses_sms_sized": all(
                len(sent_by_receiver[message["sender"]].get("content", "")) <= 160
                for message in messages
                if message["sender"] in sent_by_receiver
            ),
            "received_history_visible": len(history.get("received", [])) >= len(messages),
        }

        passed = all(assertions.values())
        return {
            "pass": passed,
            "started_at": started_at,
            "finished_at": time.time(),
            "duration_seconds": round(time.time() - started_at, 3),
            "base_port": args.base_port,
            "mode": "external" if args.external_api_url else "managed-local",
            "api_url": api_url,
            "service_health": health,
            "aggregate_health": aggregate_health,
            "receive_results": receive_results,
            "sent_responses": [
                {
                    "label": message["label"],
                    "receiver": message["sender"],
                    "response": sent_by_receiver.get(message["sender"], {}).get("content"),
                }
                for message in messages
            ],
            "assertions": assertions,
        }
    finally:
        if not args.external_api_url:
            stop_services(services)


def main() -> int:
    args = parse_args()
    report = run_smoke(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "report": str(args.report)}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
