#!/usr/bin/env python3
# ChillBuddy Backend - Test Runner
# Comprehensive test execution and reporting script

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(command: List[str], cwd: Optional[str] = None) -> tuple:
    """
    Run a command and return the result.
    
    Args:
        command: Command to run as list of strings
        cwd: Working directory for the command
    
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 5 minutes"
    except Exception as e:
        return 1, "", str(e)

def check_dependencies() -> bool:
    """
    Check if required testing dependencies are installed.
    
    Returns:
        True if all dependencies are available
    """
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required testing dependencies are installed")
    return True

def run_linting() -> bool:
    """
    Run code linting checks.
    
    Returns:
        True if linting passes
    """
    print("\n🔍 Running code linting...")
    
    # Run flake8
    print("Running flake8...")
    returncode, stdout, stderr = run_command(['flake8', '.', '--max-line-length=100', '--exclude=venv,__pycache__'])
    
    if returncode != 0:
        print(f"❌ Flake8 linting failed:")
        print(stderr)
        return False
    
    print("✅ Flake8 linting passed")
    return True

def run_type_checking() -> bool:
    """
    Run type checking with mypy.
    
    Returns:
        True if type checking passes
    """
    print("\n🔍 Running type checking...")
    
    # Check if mypy is available
    try:
        import mypy
    except ImportError:
        print("⚠️  MyPy not installed, skipping type checking")
        return True
    
    print("Running mypy...")
    returncode, stdout, stderr = run_command(['mypy', '.', '--ignore-missing-imports'])
    
    if returncode != 0:
        print(f"❌ Type checking failed:")
        print(stdout)
        print(stderr)
        return False
    
    print("✅ Type checking passed")
    return True

def run_unit_tests(test_file: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Run unit tests with pytest.
    
    Args:
        test_file: Specific test file to run (optional)
        verbose: Enable verbose output
    
    Returns:
        True if all tests pass
    """
    print("\n🧪 Running unit tests...")
    
    # Build pytest command
    cmd = ['pytest']
    
    if verbose:
        cmd.append('-v')
    
    if test_file:
        cmd.append(f"tests/{test_file}")
    else:
        cmd.append('tests/')
    
    # Add coverage reporting
    cmd.extend([
        '--cov=.',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        '--cov-fail-under=80'  # Require 80% coverage
    ])
    
    print(f"Running: {' '.join(cmd)}")
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print(stderr)
    
    if returncode != 0:
        print("❌ Unit tests failed")
        return False
    
    print("✅ All unit tests passed")
    return True

def run_integration_tests() -> bool:
    """
    Run integration tests.
    
    Returns:
        True if integration tests pass
    """
    print("\n🔗 Running integration tests...")
    
    # Run integration tests with specific marker
    cmd = ['pytest', 'tests/', '-m', 'integration', '-v']
    
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print(stderr)
    
    if returncode != 0:
        print("❌ Integration tests failed")
        return False
    
    print("✅ Integration tests passed")
    return True

def run_performance_tests() -> bool:
    """
    Run performance tests.
    
    Returns:
        True if performance tests pass
    """
    print("\n⚡ Running performance tests...")
    
    # Run performance tests with specific marker
    cmd = ['pytest', 'tests/', '-m', 'performance', '-v']
    
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print(stderr)
    
    if returncode != 0:
        print("❌ Performance tests failed")
        return False
    
    print("✅ Performance tests passed")
    return True

def generate_test_report() -> None:
    """
    Generate a comprehensive test report.
    """
    print("\n📊 Generating test report...")
    
    # Run pytest with XML output for CI/CD
    cmd = [
        'pytest',
        'tests/',
        '--junitxml=test-results.xml',
        '--cov=.',
        '--cov-report=xml:coverage.xml',
        '--cov-report=html:htmlcov'
    ]
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        print("✅ Test report generated successfully")
        print("📁 HTML coverage report: htmlcov/index.html")
        print("📁 XML coverage report: coverage.xml")
        print("📁 JUnit test results: test-results.xml")
    else:
        print("❌ Failed to generate test report")

def run_security_checks() -> bool:
    """
    Run security checks on the codebase.
    
    Returns:
        True if security checks pass
    """
    print("\n🔒 Running security checks...")
    
    # Check if bandit is available
    try:
        import bandit
    except ImportError:
        print("⚠️  Bandit not installed, skipping security checks")
        return True
    
    # Run bandit security linter
    cmd = ['bandit', '-r', '.', '-f', 'json', '-o', 'security-report.json']
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print("❌ Security checks found issues")
        print(stderr)
        return False
    
    print("✅ Security checks passed")
    return True

def cleanup_test_artifacts() -> None:
    """
    Clean up test artifacts and temporary files.
    """
    print("\n🧹 Cleaning up test artifacts...")
    
    artifacts_to_remove = [
        '.pytest_cache',
        '__pycache__',
        '*.pyc',
        '.coverage',
        'htmlcov',
        'test-results.xml',
        'coverage.xml',
        'security-report.json'
    ]
    
    for artifact in artifacts_to_remove:
        if '*' in artifact:
            # Use glob for wildcard patterns
            import glob
            for file in glob.glob(artifact, recursive=True):
                try:
                    os.remove(file)
                except (OSError, FileNotFoundError):
                    pass
        else:
            # Remove directories and files
            import shutil
            if os.path.exists(artifact):
                try:
                    if os.path.isdir(artifact):
                        shutil.rmtree(artifact)
                    else:
                        os.remove(artifact)
                except (OSError, FileNotFoundError):
                    pass
    
    print("✅ Test artifacts cleaned up")

def main():
    """
    Main test runner function.
    """
    parser = argparse.ArgumentParser(description='ChillBuddy Backend Test Runner')
    parser.add_argument('--test-file', help='Specific test file to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-lint', action='store_true', help='Skip linting')
    parser.add_argument('--no-type-check', action='store_true', help='Skip type checking')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--security', action='store_true', help='Run security checks')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--cleanup', action='store_true', help='Clean up test artifacts')
    parser.add_argument('--all', action='store_true', help='Run all checks and tests')
    
    args = parser.parse_args()
    
    print("🚀 ChillBuddy Backend Test Runner")
    print("=" * 50)
    
    start_time = time.time()
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    success = True
    
    # Clean up if requested
    if args.cleanup:
        cleanup_test_artifacts()
        return
    
    # Run linting
    if not args.no_lint and (args.all or not any([args.integration, args.performance, args.security, args.report])):
        if not run_linting():
            success = False
    
    # Run type checking
    if not args.no_type_check and (args.all or not any([args.integration, args.performance, args.security, args.report])):
        if not run_type_checking():
            success = False
    
    # Run unit tests
    if args.all or not any([args.integration, args.performance, args.security, args.report]):
        if not run_unit_tests(args.test_file, args.verbose):
            success = False
    
    # Run integration tests
    if args.integration or args.all:
        if not run_integration_tests():
            success = False
    
    # Run performance tests
    if args.performance or args.all:
        if not run_performance_tests():
            success = False
    
    # Run security checks
    if args.security or args.all:
        if not run_security_checks():
            success = False
    
    # Generate report
    if args.report or args.all:
        generate_test_report()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    if success:
        print(f"✅ All tests completed successfully in {duration:.2f} seconds")
        sys.exit(0)
    else:
        print(f"❌ Some tests failed after {duration:.2f} seconds")
        sys.exit(1)

if __name__ == '__main__':
    main()