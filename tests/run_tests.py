#!/usr/bin/env python3
"""
Test runner for JarvisX
Executes all tests with proper configuration and reporting
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_tests(test_pattern=None, verbose=False, coverage=False, output_format="text"):
    """Run tests with specified configuration"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    cmd.append("tests/")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.append("--cov=core")
        cmd.append("--cov=ui")
        cmd.append("--cov=skills")
        cmd.append("--cov-report=html")
        cmd.append("--cov-report=term-missing")
    
    # Add output format
    if output_format == "html":
        cmd.append("--html=test_report.html")
        cmd.append("--self-contained-html")
    elif output_format == "xml":
        cmd.append("--junitxml=test_results.xml")
    
    # Add test pattern if specified
    if test_pattern:
        cmd.append(f"-k={test_pattern}")
    
    # Add additional pytest options
    cmd.extend([
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "--disable-warnings",  # Disable warnings during tests
        "--durations=10"  # Show 10 slowest tests
    ])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Project root: {project_root}")
    print("-" * 60)
    
    try:
        # Run tests
        result = subprocess.run(cmd, cwd=project_root, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install pytest first:")
        print("   pip install pytest pytest-cov pytest-html")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run JarvisX tests")
    parser.add_argument(
        "-p", "--pattern",
        help="Test pattern to run (e.g., 'test_router' for router tests only)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "html", "xml"],
        default="text",
        help="Output format for test results"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests/").exists():
        print("❌ Error: tests/ directory not found.")
        print("Please run this script from the project root directory.")
        return 1
    
    # Run tests
    exit_code = run_tests(
        test_pattern=args.pattern,
        verbose=args.verbose,
        coverage=args.coverage,
        output_format=args.format
    )
    
    # Print summary
    if exit_code == 0:
        print("\n🎉 Test execution completed successfully!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/ directory")
        if args.format == "html":
            print("📄 HTML report generated: test_report.html")
        elif args.format == "xml":
            print("📄 XML report generated: test_results.xml")
    else:
        print("\n💥 Test execution failed!")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())