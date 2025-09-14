#!/usr/bin/env python3
"""
Simple test runner for the podcast script generation tests.

This script provides an easy way to run the tests with different options.
"""

import sys
import subprocess
import os


def run_with_unittest():
    """Run tests using unittest."""
    print("Running tests with unittest...")
    try:
        import test_podcast_script

        return test_podcast_script.run_tests()
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def run_with_pytest():
    """Run tests using pytest if available."""
    print("Running tests with pytest...")
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "test_podcast_script.py",
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"Error running pytest: {e}")
        return False


def main():
    """Main test runner function."""
    print("🧪 Podcast Script Generation Test Runner 🧪")
    print("=" * 50)

    # Check if pytest is available
    try:
        import pytest

        pytest_available = True
    except ImportError:
        pytest_available = False

    if pytest_available:
        print("pytest is available. Choose test runner:")
        print("1. pytest (recommended)")
        print("2. unittest")

        choice = input("Enter choice (1 or 2, default: 1): ").strip()

        if choice == "2":
            success = run_with_unittest()
        else:
            success = run_with_pytest()
    else:
        print("pytest not available. Using unittest.")
        success = run_with_unittest()

    if success:
        print("\n✅ All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
