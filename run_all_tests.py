#!/usr/bin/env python3
"""Test runner script for the project."""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def run_tests(test_pattern: str = "tests/test_*.py"):
    """Run all tests in the tests directory."""
    tests_dir = project_root / "tests"

    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return 1

    test_files = [f for f in tests_dir.glob(test_pattern) if f.is_file()]

    if not test_files:
        print("No test files found matching pattern")
        return 1

    print(f"Running {len(test_files)} test files...")
    print("=" * 60)

    failed = 0
    passed = 0

    for test_file in test_files:
        print(f"\n{test_file.name}:")
        print("-" * 40)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file)],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            print(f"X {test_file.name} - TIMEOUT")
            failed += 1
            continue

        print(result.stdout)

        if result.returncode != 0:
            print(f"X {test_file.name} - FAILED")
            failed += 1
        else:
            print(f"OK {test_file.name} - PASSED")
            passed += 1

    print("\n" + "=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed out of {passed + failed} tests")

    return failed

if __name__ == "__main__":
    import subprocess

    if len(sys.argv) > 1:
        test_arg = sys.argv[1]

        if test_arg == "--all" or test_arg == "-a":
            sys.exit(run_tests())
        elif test_arg == "--file" or test_arg == "-f" and len(sys.argv) > 2:
            test_file = sys.argv[2]
            sys.exit(run_tests(f"tests/{test_file}"))
        else:
            print("Usage:")
            print("  python run_all_tests.py [--all|-a] [--file|-f] <test_file>")
            print("  python run_all_tests.py")
            print("\nOptions:")
            print("  --all, -a    Run all tests")
            print("  --file, -f   Run specific test file")
            sys.exit(1)
    else:
        sys.exit(run_tests())