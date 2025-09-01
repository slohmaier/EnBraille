#!/usr/bin/env python3
"""
Simple test runner for EnBraille tests
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run all EnBraille tests"""
    print("=== EnBraille Test Runner ===\n")
    
    # Add current directory to path for imports
    current_dir = Path(__file__).parent.parent  # Go up one level since we're in tools/
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    tests_dir = current_dir / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return 1
    
    # Test categories
    categories = {
        "Core Libraries Tests": tests_dir / "core_libraries",
        "Utilities Tests": tests_dir / "utilities",
        "Business Logic Tests": tests_dir / "business_logic",
        "Welcome Page Tests": tests_dir / "welcome_page",
        "Accessibility Tests": tests_dir / "accessibility", 
        "UI Components Tests": tests_dir / "ui_components",
        "Navigation Tests": tests_dir / "navigation",
        "Text Functions Tests": tests_dir / "text_functions",
        "Data Model Tests": tests_dir / "data_model"
    }
    
    total_tests = 0
    failed_tests = 0
    
    for category_name, category_path in categories.items():
        if not category_path.exists():
            continue
            
        print(f"📋 {category_name}:")
        test_files = list(category_path.glob("test_*.py"))
        
        if not test_files:
            print("   No tests found\n")
            continue
            
        for test_file in sorted(test_files):
            test_name = test_file.stem
            print(f"   Running {test_name}...", end=" ")
            total_tests += 1
            
            try:
                # Run the test
                result = subprocess.run(
                    [sys.executable, str(test_file)], 
                    capture_output=True, 
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("✅")
                else:
                    print("❌")
                    failed_tests += 1
                    if result.stderr:
                        print(f"      Error: {result.stderr.decode().strip()}")
                        
            except subprocess.TimeoutExpired:
                print("⏱️ Timeout")
                failed_tests += 1
            except Exception as e:
                print(f"💥 Exception: {e}")
                failed_tests += 1
        
        print()  # Empty line between categories
    
    # Summary
    passed_tests = total_tests - failed_tests
    print(f"📊 Test Results:")
    print(f"   Total: {total_tests}")
    print(f"   Passed: {passed_tests} ✅")
    print(f"   Failed: {failed_tests} ❌")
    
    if failed_tests == 0:
        print(f"\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())