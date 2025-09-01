#!/usr/bin/env python3
"""
EnBraille Test Coverage Runner (Direct Approach)

This script runs each test directly under coverage instead of using the test runner,
to properly capture coverage data from GUI tests.
"""

import os
import sys
import subprocess
import argparse
import shutil
import webbrowser
import time
from pathlib import Path


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="EnBraille Test Coverage Runner (Direct Approach)"
    )
    
    parser.add_argument('--open', action='store_true',
                       help='Automatically open HTML report in browser')
    parser.add_argument('--clean', action='store_true',
                       help='Clean previous coverage data first')
    
    args = parser.parse_args()
    
    print("EnBraille Test Coverage Runner (Direct)")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    coverage_dir = project_root / "coverage_html_report"
    
    # Check prerequisites
    try:
        import coverage
        print(f"✅ Found coverage {coverage.__version__}")
    except ImportError:
        print("❌ Missing prerequisite: coverage (pip install coverage)")
        sys.exit(1)
    
    # Clean previous data if requested
    if args.clean:
        print("🧹 Cleaning previous coverage data...")
        subprocess.run([sys.executable, "-m", "coverage", "erase"], 
                      capture_output=True)
        if coverage_dir.exists():
            shutil.rmtree(coverage_dir)
            print(f"   Removed {coverage_dir.name}/")
        
        # Create a temporary .coveragerc for direct mode (no parallel)
        coveragerc_content = """[run]
source = enbraille_data, enbraille_gui, enbraille_main, enbraille_widgets, enbraille_tools, libbrl, enbraille_functions
omit = *_rc.py, tests/*, scripts/*, deployment/*, .venv/*, build/*, dist/*, pyscript, shibokensupport/*, signature_bootstrap.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\\bProtocol\\):
    @(abc\\.)?abstractmethod
"""
        with open(project_root / ".coveragerc", "w") as f:
            f.write(coveragerc_content)
    
    # Change to project root
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        # Find all test files
        tests_dir = project_root / "tests"
        test_categories = {
            "Welcome Page Tests": tests_dir / "welcome_page",
            "Accessibility Tests": tests_dir / "accessibility", 
            "UI Components Tests": tests_dir / "ui_components",
            "Navigation Tests": tests_dir / "navigation",
            "Text Functions Tests": tests_dir / "text_functions",
            "Data Model Tests": tests_dir / "data_model"
        }
        
        total_tests = 0
        passed_tests = 0
        
        print(f"\\n🧪 Running tests with direct coverage analysis...")
        
        for category_name, category_path in test_categories.items():
            if not category_path.exists():
                continue
                
            print(f"📋 {category_name}:")
            test_files = list(category_path.glob("test_*.py"))
            
            if not test_files:
                print("   No tests found\\n")
                continue
                
            for test_file in sorted(test_files):
                test_name = test_file.stem
                print(f"   Running {test_name}...", end=" ")
                total_tests += 1
                
                try:
                    # Run each test directly under coverage
                    cmd = [
                        sys.executable, "-m", "coverage", "run",
                        "--append",  # Append to existing coverage data
                        "--source=enbraille_data,enbraille_gui,enbraille_main,enbraille_widgets,enbraille_tools,libbrl,enbraille_functions",
                        "--omit=*_rc.py",
                        str(test_file)
                    ]
                    
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        timeout=30,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print("✅")
                        passed_tests += 1
                    else:
                        print("❌")
                        if result.stderr:
                            # Only print first line of error to keep output clean
                            error_line = result.stderr.strip().split('\\n')[0]
                            print(f"      Error: {error_line}")
                            
                except subprocess.TimeoutExpired:
                    print("⏱️ Timeout")
                except Exception as e:
                    print(f"💥 Exception: {e}")
            
            print()  # Empty line between categories
        
        failed_tests = total_tests - passed_tests
        print(f"📊 Test Results:")
        print(f"   Total: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        
        # Generate reports
        print(f"\\n📊 Generating coverage reports...")
        print("\\n" + "="*60)
        print("📋 COVERAGE SUMMARY")
        print("="*60)
        
        # Console report
        try:
            result = subprocess.run([
                sys.executable, "-m", "coverage", "report",
                "--show-missing"
            ], capture_output=True, text=True, check=True)
            
            print(result.stdout)
            
            # Extract total coverage percentage
            total_coverage = 0.0
            lines = result.stdout.split('\\n')
            total_line = [line for line in lines if 'TOTAL' in line]
            if total_line:
                parts = total_line[0].split()
                for part in parts:
                    if '%' in part:
                        try:
                            total_coverage = float(part.replace('%', ''))
                            break
                        except ValueError:
                            continue
                            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate console report: {e}")
            total_coverage = 0.0
        
        # HTML report
        html_success = False
        try:
            subprocess.run([
                sys.executable, "-m", "coverage", "html",
                "--directory=coverage_html_report",
                "--title=EnBraille Test Coverage Report"
            ], check=True, capture_output=True)
            
            if coverage_dir.exists():
                print(f"✅ HTML report: {coverage_dir}/index.html")
                html_success = True
                
                # Count files
                html_files = list(coverage_dir.glob("*.html"))
                print(f"   Generated {len(html_files)} HTML files")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate HTML report: {e}")
        
        # Open report if requested
        if args.open and html_success:
            html_file = coverage_dir / "index.html"
            if html_file.exists():
                print(f"\\n🌐 Opening HTML report in browser...")
                try:
                    webbrowser.open(f"file://{html_file.absolute()}")
                    print("✅ Report opened in browser")
                except Exception as e:
                    print(f"❌ Failed to open browser: {e}")
        
        # Summary
        print(f"\\n{'='*60}")
        print("📊 COVERAGE ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"📈 Total Coverage: {total_coverage:.1f}%")
        print(f"🌐 HTML Report: {coverage_dir}/index.html")
        
        if html_success:
            print("\\n🎉 Coverage analysis completed successfully!")
        else:
            print("\\n⚠️ Coverage analysis completed with some issues")
            
        print("\\nNext steps:")
        print("1. Review HTML report for detailed coverage analysis")
        print("2. Focus testing efforts on uncovered code paths")
        print("3. Consider adding more unit tests for core modules")
        
        return 0 if failed_tests == 0 else 1
        
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())