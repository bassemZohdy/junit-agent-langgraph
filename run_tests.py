#!/usr/bin/env python3
"""Test runner script for the project."""

import sys
import subprocess
from pathlib import Path


def run_tests(test_pattern: str = "tests/test_*.py"):
    """Run all tests in the tests directory."""
    tests_dir = Path(__file__).parent / "tests"
    
    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return 1
    
    test_files = list(tests_dir.glob(test_pattern))
    
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
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file)],
            cwd=tests_dir.parent,
            capture_output=True,
            text=True
        timeout=60
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"✗ {test_file.name} - FAILED")
            failed += 1
        else:
            print(f"✓ {test_file.name} - PASSED")
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed out of {passed + failed} tests")
    
    return 0 if failed > 0 else 0


def run_specific_test(test_file: str):
    """Run a specific test file."""
    test_file_path = Path(__file__).parent / test_file
    
    if not test_file_path.exists():
        print(f"Test file not found: {test_file_path}")
        return 1
    
    print(f"Running {test_file_path.name}...")
    print("-" * 40)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file_path)],
        cwd=test_file_path.parent.parent,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print(result.stdout)
    
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_arg = sys.argv[1]
        
        if test_arg == "--all" or test_arg == "-a":
            sys.exit(run_tests())
        elif test_arg == "--file" or test_arg == "-f" and len(sys.argv) > 2:
            sys.exit(run_specific_test(sys.argv[2]))
        else:
            print("Usage:")
            print("  python run_tests.py [--all|-a] [--file|-f] <test_file>")
            print("  python run_tests.py")
            print("\nOptions:")
            print("  --all, -a    Run all tests")
            print("  --file, -f   Run specific test file")
            sys.exit(1)
    else:
        sys.exit(run_tests())
