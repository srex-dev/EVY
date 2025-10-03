#!/usr/bin/env python3
"""Test runner for EVY backend services."""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run EVY backend tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--services", nargs="+", choices=["sms", "llm", "router"], 
                       help="Run tests for specific services only")
    
    args = parser.parse_args()
    
    # Set up environment
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Default to running all tests if no specific option is given
    if not any([args.unit, args.integration, args.all]):
        args.all = True
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.coverage:
        pytest_cmd.extend(["--cov=backend", "--cov-report=html", "--cov-report=term"])
    
    # Select test files based on arguments
    test_files = []
    
    if args.unit or args.all:
        if args.services:
            for service in args.services:
                if service == "sms":
                    test_files.append("tests/test_sms_gateway.py")
                elif service == "llm":
                    test_files.append("tests/test_llm_inference.py")
                elif service == "router":
                    test_files.append("tests/test_message_router.py")
        else:
            test_files.extend([
                "tests/test_sms_gateway.py",
                "tests/test_llm_inference.py",
                "tests/test_message_router.py"
            ])
    
    if args.integration or args.all:
        test_files.append("tests/test_integration.py")
    
    if not test_files:
        print("No tests selected. Use --unit, --integration, or --all")
        return 1
    
    pytest_cmd.extend(test_files)
    
    # Run tests
    success = run_command(pytest_cmd, "Running tests")
    
    if args.coverage and success:
        print(f"\nCoverage report generated in: {backend_dir}/htmlcov/index.html")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
