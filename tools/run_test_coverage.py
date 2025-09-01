#!/usr/bin/env python3
"""
EnBraille Test Coverage Runner

This script generates a test coverage report for EnBraille in HTML format.
It runs a simple coverage analysis and creates an interactive HTML report.

Prerequisites:
- coverage: pip install coverage

Usage:
    python tools/run_test_coverage.py [options]

Options:
    --open          Automatically open HTML report in browser

Output:
    - coverage_html_report/index.html - Interactive HTML report
"""

import os
import sys
import subprocess
import argparse
import shutil
import webbrowser
from pathlib import Path


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="EnBraille Test Coverage Runner"
    )
    
    parser.add_argument('--open', action='store_true',
                       help='Automatically open HTML report in browser')
    
    args = parser.parse_args()
    
    print("EnBraille Test Coverage Runner")
    print("=" * 50)
    
    # Check prerequisites
    try:
        import coverage
        print(f"✅ Found coverage {coverage.__version__}")
    except ImportError:
        print("❌ Missing prerequisite: coverage")
        print("Install with: pip install coverage")
        sys.exit(1)
    
    # Clean previous data
    print("\\n🧹 Cleaning previous coverage data...")
    subprocess.run([sys.executable, "-m", "coverage", "erase"], 
                   capture_output=True)
    
    # Run coverage on the main test runner
    print("🧪 Running tests with coverage analysis...")
    
    cmd = [
        sys.executable, "-m", "coverage", "run",
        "--source=enbraille_main,enbraille_gui,enbraille_data,enbraille_widgets,libbrl",
        "--omit=*_rc.py",
        "--concurrency=multiprocessing",
        "tools/run_tests.py"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.stdout:
            print("Test Results:")
            for line in result.stdout.split('\\n'):
                if '✅' in line or '❌' in line or 'passed' in line or 'Test Results:' in line:
                    print(f"  {line}")
        
        print("✅ Coverage data collected")
        
    except subprocess.TimeoutExpired:
        print("⚠️ Tests timed out, but continuing with coverage report")
    except Exception as e:
        print(f"⚠️ Test execution had issues: {e}")
        print("Continuing with coverage report...")
    
    # Generate console report
    print("\\n📊 Generating coverage reports...")
    print("\\n" + "="*60)
    print("📋 COVERAGE SUMMARY")
    print("="*60)
    
    try:
        # First combine coverage data from all processes
        subprocess.run([sys.executable, "-m", "coverage", "combine"], 
                      capture_output=True)
        
        result = subprocess.run([
            sys.executable, "-m", "coverage", "report",
            "--show-missing"
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout)
        
        # Extract coverage percentage
        total_coverage = None
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
        
    except subprocess.CalledProcessError:
        print("⚠️ Console report had issues, trying HTML report anyway...")
    
    # Generate HTML report
    html_success = False
    try:
        subprocess.run([
            sys.executable, "-m", "coverage", "html",
            "--directory=coverage_html_report",
            "--title=EnBraille Test Coverage Report"
        ], check=True, capture_output=True)
        
        coverage_dir = Path("coverage_html_report")
        if coverage_dir.exists():
            print(f"✅ HTML report: {coverage_dir}/index.html")
            html_success = True
            
            # Count files
            html_files = list(coverage_dir.glob("*.html"))
            print(f"   Generated {len(html_files)} HTML files")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ HTML report failed: {e}")
    
    # Generate XML for CI/CD
    try:
        subprocess.run([sys.executable, "-m", "coverage", "xml"], 
                      check=True, capture_output=True)
        if Path("coverage.xml").exists():
            print("✅ XML report: coverage.xml")
    except:
        pass
    
    # Open report if requested
    if args.open and html_success:
        html_file = Path("coverage_html_report/index.html")
        if html_file.exists():
            try:
                webbrowser.open(f"file://{html_file.absolute()}")
                print("🌐 Opened HTML report in browser")
            except Exception as e:
                print(f"⚠️ Could not open browser: {e}")
    
    # Summary
    print(f"\\n{'='*60}")
    print("📊 COVERAGE ANALYSIS COMPLETE")
    print(f"{'='*60}")
    
    if html_success:
        print("🌐 HTML Report: coverage_html_report/index.html")
        print("\\n📝 HTML Report Features:")
        print("• Interactive coverage visualization")
        print("• Line-by-line coverage highlighting") 
        print("• Missing lines highlighted in red")
        print("• File-by-file breakdown")
        print("• Coverage percentages for each module")
        
        print("\\n🎯 How to Use:")
        print("1. Open coverage_html_report/index.html in your browser")
        print("2. Click on any Python file to see detailed coverage")
        print("3. Red lines show code that needs testing")
        print("4. Use this to guide your testing efforts")
        
        print("\\n🎉 Coverage report generated successfully!")
        
    else:
        print("❌ No coverage data available")
        print("\\n💡 This can happen when:")
        print("• Tests don't import the main modules")
        print("• Code is only run as __main__ scripts") 
        print("• Modules are imported dynamically")
        print("\\nConsider adding unit tests that import modules directly.")


if __name__ == "__main__":
    main()