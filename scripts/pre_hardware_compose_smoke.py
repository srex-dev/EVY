"""Build, run, smoke-test, and stop the pre-hardware Compose stack."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = "docker-compose.prehardware.yml"
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "pre_hardware_compose_smoke_report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run EVY pre-hardware Compose smoke test")
    parser.add_argument("--base-port", type=int, default=18100, help="Host port for API gateway; other host ports increment from this")
    parser.add_argument("--timeout", type=float, default=60.0, help="Seconds to wait for Compose health and smoke responses")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="JSON report output path")
    parser.add_argument("--no-build", action="store_true", help="Skip docker compose build")
    parser.add_argument("--keep-running", action="store_true", help="Leave the Compose stack running after the smoke test")
    return parser.parse_args()


def compose_env(base_port: int) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "EVY_PREHW_API_PORT": str(base_port),
            "EVY_PREHW_SMS_PORT": str(base_port + 1),
            "EVY_PREHW_ROUTER_PORT": str(base_port + 2),
            "EVY_PREHW_LLM_PORT": str(base_port + 3),
            "EVY_PREHW_RAG_PORT": str(base_port + 4),
            "EVY_PREHW_PRIVACY_PORT": str(base_port + 5),
        }
    )
    return env


def run(command: list[str], env: dict[str, str]) -> None:
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    args = parse_args()
    env = compose_env(args.base_port)
    compose = ["docker", "compose", "-f", COMPOSE_FILE]

    try:
        run(compose + ["config", "--quiet"], env)
        if not args.no_build:
            run(compose + ["build"], env)
        run(compose + ["up", "-d", "--wait"], env)
        run(
            [
                sys.executable,
                "scripts/pre_hardware_smoke.py",
                "--external-api-url",
                f"http://127.0.0.1:{args.base_port}",
                "--timeout",
                str(args.timeout),
                "--report",
                str(args.report),
            ],
            env,
        )
        return 0
    finally:
        if not args.keep_running:
            subprocess.run(compose + ["down", "--remove-orphans"], cwd=ROOT, env=env, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
