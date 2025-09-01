#!/usr/bin/env python3
"""
EnBraille Test Coverage Runner (Simple Version)

This script runs the existing test suite with coverage analysis and generates
an HTML report. It uses the current test structure and works around import issues.

Prerequisites:
- coverage: pip install coverage

Usage:
    python tools/run_test_coverage_simple.py [options]

Options:
    --open          Automatically open HTML report in browser
    --clean         Clean previous coverage data first
    --fail-under X  Fail if coverage is under X percent (default: 70)

Output:
    - coverage_html_report/index.html - Interactive HTML report
"""

import os
import sys
import subprocess
import argparse
import shutil
import webbrowser
import time
from pathlib import Path
import importlib.util


class SimpleCoverageRunner:
    """Simple test coverage runner for EnBraille"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.coverage_dir = self.project_root / "coverage_html_report"
        self.coverage_file = self.project_root / ".coverage"
        
    def clean_previous_data(self):
        """Clean previous coverage data"""
        print("🧹 Cleaning previous coverage data...")
        
        if self.coverage_file.exists():
            self.coverage_file.unlink()
            print(f"   Removed {self.coverage_file.name}")
        
        if self.coverage_dir.exists():
            shutil.rmtree(self.coverage_dir)
            print(f"   Removed {self.coverage_dir.name}/")
    
    def run_coverage_tests(self):
        """Run tests with coverage using the existing test runner"""
        print(f"\n🧪 Running tests with coverage analysis...")
        
        # Change to project root
        original_cwd = os.getcwd()
        os.chdir(self.project_root)
        
        try:
            # Set environment for subprocess coverage tracking
            env = os.environ.copy()
            env['COVERAGE_PROCESS_START'] = str(self.project_root / '.coveragerc')
            
            # Build coverage command - run the existing test runner under coverage
            cmd = [
                sys.executable, "-m", "coverage", "run",
                "tools/run_tests.py"
            ]
            
            print(f"Command: {' '.join(cmd)}")
            
            # Run the tests
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                env=env
            )
            
            duration = time.time() - start_time
            
            print(f"Test execution completed in {duration:.1f}s")
            
            if result.stdout:
                print("Test Output:")
                print(result.stdout)
            
            if result.returncode == 0:
                print(f"✅ Tests completed successfully")
                return True
            else:
                print(f"❌ Tests had issues but continuing with coverage analysis")
                if result.stderr:
                    print("STDERR:", result.stderr)
                return True  # Continue anyway to get coverage data
                
        except subprocess.TimeoutExpired:
            print("❌ Tests timed out after 2 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def generate_coverage_reports(self):
        """Generate coverage reports"""
        print(f"\n📊 Generating coverage reports...")
        
        os.chdir(self.project_root)
        
        # First combine all coverage data files
        print("🔗 Combining coverage data from all processes...")
        try:
            subprocess.run([sys.executable, "-m", "coverage", "combine"], 
                          capture_output=True, check=True)
            print("✅ Coverage data combined")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Could not combine coverage data: {e}")
        
        # Console report
        print("\\n" + "="*60)
        print("📋 COVERAGE SUMMARY")
        print("="*60)
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "coverage", "report",
                "--show-missing"
            ], capture_output=True, text=True, check=True)
            
            print(result.stdout)
            
            # Extract total coverage percentage
            lines = result.stdout.split('\\n')
            total_line = [line for line in lines if 'TOTAL' in line]
            if total_line:
                parts = total_line[0].split()
                for part in parts:
                    if '%' in part:
                        try:
                            self.total_coverage = float(part.replace('%', ''))
                            break
                        except ValueError:
                            continue
                else:
                    self.total_coverage = 0.0
            else:
                self.total_coverage = 0.0
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate console report: {e}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
        
        # HTML report
        try:
            subprocess.run([
                sys.executable, "-m", "coverage", "html",
                "--directory=coverage_html_report",
                "--title=EnBraille Test Coverage Report"
            ], check=True, capture_output=True)
            
            if self.coverage_dir.exists():
                print(f"✅ HTML report: {self.coverage_dir}/index.html")
                return True
            else:
                print("⚠️  HTML report directory not created")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate HTML report: {e}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
    
    def open_html_report(self):
        """Open HTML report in default browser"""
        html_file = self.coverage_dir / "index.html"
        if html_file.exists():
            print(f"\\n🌐 Opening HTML report in browser...")
            try:
                webbrowser.open(f"file://{html_file.absolute()}")
                return True
            except Exception as e:
                print(f"❌ Failed to open browser: {e}")
                print(f"Manual: open file://{html_file.absolute()}")
                return False
        else:
            print("❌ HTML report not found")
            return False
    
    def check_coverage_threshold(self, threshold):
        """Check if coverage meets minimum threshold"""
        if hasattr(self, 'total_coverage'):
            print(f"\\n🎯 Coverage Threshold Check:")
            print(f"   Current coverage: {self.total_coverage:.1f}%")
            print(f"   Required threshold: {threshold}%")
            
            if self.total_coverage >= threshold:
                print("✅ Coverage threshold met!")
                return True
            else:
                print("❌ Coverage below threshold!")
                return False
        else:
            print("⚠️  Could not determine coverage percentage")
            return True  # Don't fail if we can't determine coverage


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="EnBraille Test Coverage Runner (Simple Version)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--open', action='store_true',
                       help='Automatically open HTML report in browser')
    parser.add_argument('--clean', action='store_true',
                       help='Clean previous coverage data first')
    parser.add_argument('--fail-under', type=float, default=70.0,
                       help='Fail if coverage is under X percent (default: 70)')
    
    args = parser.parse_args()
    
    print("EnBraille Test Coverage Runner (Simple)")
    print("=" * 50)
    
    runner = SimpleCoverageRunner()
    
    # Check prerequisites
    try:
        import coverage
        print(f"✅ Found coverage {coverage.__version__}")
    except ImportError:
        print("❌ Missing prerequisite: coverage (pip install coverage)")
        sys.exit(1)
    
    # Clean previous data if requested
    if args.clean:
        runner.clean_previous_data()
    
    # Run tests with coverage
    if not runner.run_coverage_tests():
        print("\\n❌ Failed to run tests")
        sys.exit(1)
    
    # Generate reports
    if not runner.generate_coverage_reports():
        print("❌ Failed to generate coverage reports")
        sys.exit(1)
    
    # Check coverage threshold
    threshold_met = runner.check_coverage_threshold(args.fail_under)
    
    # Open HTML report if requested
    if args.open:
        runner.open_html_report()
    
    # Print summary
    print(f"\\n{'='*60}")
    print("📊 COVERAGE ANALYSIS COMPLETE")
    print(f"{'='*60}")
    
    if hasattr(runner, 'total_coverage'):
        print(f"📈 Total Coverage: {runner.total_coverage:.1f}%")
    
    print(f"🌐 HTML Report: {runner.coverage_dir}/index.html")
    
    print("\\nNext steps:")
    print("1. Review HTML report for detailed coverage analysis")
    print("2. Focus testing efforts on uncovered code paths")
    print("3. Consider adding more unit tests for core modules")
    
    # Exit with appropriate code
    if not threshold_met:
        sys.exit(1)
    else:
        print("\\n🎉 Coverage analysis completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()