#!/usr/bin/env python3
"""Run all knowledge builders and generate a checksum manifest."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_json_files(root: Path) -> set[Path]:
    return set(root.rglob("*.json"))


def run_builder(script: Path, region: str) -> int:
    cmd = [sys.executable, str(script)]
    if "wichita" in script.name:
        # Keep legacy builder executable but allow region override via env in future.
        cmd.extend(["--city", "Regional", "--state", region.upper()])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[FAIL] {script.name}\n{proc.stderr}")
    else:
        print(f"[ OK ] {script.name}")
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap lilEVY knowledge base.")
    parser.add_argument("--region", default="us", help="Deployment region identifier")
    parser.add_argument("--scripts-dir", default="scripts", help="Directory containing build_*.py")
    parser.add_argument("--output-dir", default="data/lilevy/knowledge", help="Knowledge output directory")
    args = parser.parse_args()

    scripts_dir = Path(args.scripts_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    build_scripts = sorted(scripts_dir.glob("build_*.py"))
    if not build_scripts:
        print("No build_*.py scripts found.")
        return 1

    before = list_json_files(Path("."))
    failures = 0
    for script in build_scripts:
        failures += run_builder(script, args.region)

    after = list_json_files(Path("."))
    generated = sorted(after - before)

    manifest: Dict[str, Dict[str, str]] = {}
    for json_file in generated:
        manifest[str(json_file)] = {
            "sha256": sha256_file(json_file),
            "region": args.region,
        }

    manifest_path = output_dir / "knowledge_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "region": args.region,
                "generated_files": manifest,
                "script_count": len(build_scripts),
                "failure_count": failures,
            },
            f,
            indent=2,
        )

    print(f"Manifest written: {manifest_path}")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
