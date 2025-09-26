#!/usr/bin/env python3
"""Test runner script for Fortnite integration."""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with return code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run Fortnite integration tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test selection
    if args.unit:
        cmd.extend(["tests/unit/"])
    elif args.integration:
        cmd.extend(["tests/integration/"])
    else:
        cmd.extend(["tests/"])
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=custom_components.fortnite", "--cov-report=html", "--cov-report=term"])
    
    # Add verbosity
    if args.verbose:
        cmd.extend(["-v", "-s"])
    
    # Skip slow tests
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Run tests
    success = run_command(cmd, "Fortnite Integration Tests")
    
    if success:
        print("\n🎉 All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
