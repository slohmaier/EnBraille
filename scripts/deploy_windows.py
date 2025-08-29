#!/usr/bin/env python3
"""
Windows Deployment Master Script for EnBraille

This script orchestrates the creation of all Windows deployment packages:
- Portable ZIP distribution
- MSI installer for winget
- MSIX package for Microsoft Store

Prerequisites:
- Python 3.8+ with all EnBraille dependencies
- PyInstaller: pip install pyinstaller
- cx_Freeze: pip install cx_freeze (for MSI)
- WiX Toolset v3 (for MSI)
- Windows 10 SDK (for MSIX)
- Inkscape (for icon generation)

Usage:
    python scripts/deploy_windows.py [OPTIONS]
    
Options:
    --portable    Build portable ZIP only
    --msi         Build MSI installer only
    --msix        Build MSIX package only
    --all         Build all packages (default)
    --clean       Clean previous builds first
    --test        Test all packages after building

Output:
    dist/EnBraille_Portable_v{version}.zip
    dist/EnBraille_v{version}.msi
    dist/EnBraille_v{version}.msix
    dist/EnBraille_winget_manifest.yaml
    dist/EnBraille_Store_Assets/
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
import time


def get_version():
    """Get version from main script"""
    try:
        with open('enbraille_main.py', 'r') as f:
            content = f.read()
            import re
            match = re.search(r'setApplicationVersion\("([^"]+)"\)', content)
            if match:
                return match.group(1)
    except Exception:
        pass
    return "0.1.0"


def check_global_prerequisites():
    """Check global prerequisites for all builds"""
    missing = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        missing.append("Python 3.8+ (current: {}.{})".format(*sys.version_info[:2]))
    
    # Check EnBraille main file
    if not Path('enbraille_main.py').exists():
        missing.append("enbraille_main.py (run from project root)")
    
    # Check Inkscape for icon generation
    try:
        result = subprocess.run(['inkscape', '--version'], capture_output=True)
        if result.returncode != 0:
            missing.append("Inkscape (for icon generation)")
    except FileNotFoundError:
        missing.append("Inkscape (for icon generation)")
    
    if missing:
        print("❌ Missing global prerequisites:")
        for item in missing:
            print(f"   - {item}")
        return False
    
    print("✅ Global prerequisites satisfied")
    return True


def clean_builds():
    """Clean previous builds"""
    dirs_to_clean = ['dist', 'build']
    files_to_clean = ['setup_msi.py', '*.spec']
    
    print("🧹 Cleaning previous builds...")
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed {dir_name}/")
    
    # Clean PyInstaller spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   Removed {spec_file}")


def run_build_script(script_name, description):
    """Run a build script and return success status"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    script_path = Path('scripts') / script_name
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path)
        ], check=True, text=True)
        
        duration = time.time() - start_time
        print(f"✅ {description} completed in {duration:.1f}s")
        return True
        
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"❌ {description} failed after {duration:.1f}s")
        print(f"Return code: {e.returncode}")
        return False


def test_packages():
    """Test the generated packages"""
    print(f"\n{'='*60}")
    print("🧪 Testing generated packages")
    print(f"{'='*60}")
    
    version = get_version()
    dist_dir = Path('dist')
    
    if not dist_dir.exists():
        print("❌ No dist directory found")
        return False
    
    # Check expected files
    expected_files = [
        f"EnBraille_Portable_v{version}.zip",
        f"EnBraille_v{version}.msi", 
        f"EnBraille_v{version}.msix",
        "EnBraille_winget_manifest.yaml"
    ]
    
    expected_dirs = [
        "EnBraille_Store_Assets"
    ]
    
    all_good = True
    
    for filename in expected_files:
        file_path = dist_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size / (1024 * 1024)
            print(f"✅ {filename} ({size:.1f} MB)")
        else:
            print(f"❌ Missing: {filename}")
            all_good = False
    
    for dirname in expected_dirs:
        dir_path = dist_dir / dirname
        if dir_path.exists():
            file_count = len(list(dir_path.iterdir()))
            print(f"✅ {dirname}/ ({file_count} files)")
        else:
            print(f"❌ Missing: {dirname}/")
            all_good = False
    
    return all_good


def create_deployment_summary():
    """Create a summary of all generated packages"""
    version = get_version()
    dist_dir = Path('dist')
    
    summary_content = f'''# EnBraille Windows Deployment Summary
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Version: {version}

## Generated Packages

### 1. Portable Distribution
- **File**: EnBraille_Portable_v{version}.zip
- **Purpose**: Standalone executable that runs without installation
- **Target**: Direct distribution, USB drives, enterprise deployment
- **Usage**: Extract and run EnBraille.exe

### 2. MSI Installer
- **File**: EnBraille_v{version}.msi
- **Purpose**: Windows installer package for winget
- **Target**: Windows Package Manager (winget)
- **Manifest**: EnBraille_winget_manifest.yaml
- **Usage**: Submit manifest to microsoft/winget-pkgs repository

### 3. MSIX Package
- **File**: EnBraille_v{version}.msix
- **Purpose**: Microsoft Store submission
- **Target**: Microsoft Store / Windows 10+ app installer
- **Assets**: EnBraille_Store_Assets/ (for store listing)
- **Usage**: Submit via Microsoft Partner Center

## Distribution Checklist

### Portable ZIP
- [ ] Test executable on clean Windows system
- [ ] Verify all dependencies are included
- [ ] Upload to GitHub releases
- [ ] Update download links

### MSI for winget
- [ ] Test MSI installation and uninstallation
- [ ] Upload MSI to GitHub releases
- [ ] Update InstallerUrl in winget manifest
- [ ] Submit manifest PR to microsoft/winget-pkgs
- [ ] Wait for approval and merge

### MSIX for Microsoft Store
- [ ] Test MSIX installation via PowerShell
- [ ] Sign package with trusted certificate
- [ ] Create Microsoft Partner Center account
- [ ] Upload MSIX and store assets
- [ ] Fill store listing with provided information
- [ ] Submit for certification
- [ ] Wait for approval (7-14 days typically)

## Support Resources

### winget Submission
- Repository: https://github.com/Microsoft/winget-pkgs
- Guidelines: https://docs.microsoft.com/en-us/windows/package-manager/package/

### Microsoft Store Submission  
- Partner Center: https://partner.microsoft.com/
- Store Policies: https://docs.microsoft.com/en-us/windows/uwp/publish/store-policies
- Certification Requirements: https://docs.microsoft.com/en-us/windows/uwp/publish/the-app-certification-process

### Testing Commands
```powershell
# Test MSI installation
msiexec /i "EnBraille_v{version}.msi" /quiet

# Test MSIX installation  
Add-AppxPackage -Path "EnBraille_v{version}.msix"

# Test winget installation (after publication)
winget install slohmaier.EnBraille
```

## Next Release Process

1. Update version in enbraille_main.py
2. Run: python deployment/update_version.py <new_version>
3. Run: python scripts/deploy_windows.py --all
4. Test all packages
5. Commit and tag: git tag v<new_version>
6. Upload to GitHub releases
7. Update package repositories (winget, Store)
'''
    
    summary_file = dist_dir / "DEPLOYMENT_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"📄 Created deployment summary: {summary_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="EnBraille Windows Deployment Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--portable', action='store_true',
                       help='Build portable ZIP only')
    parser.add_argument('--msi', action='store_true',
                       help='Build MSI installer only')
    parser.add_argument('--msix', action='store_true',
                       help='Build MSIX package only')
    parser.add_argument('--all', action='store_true',
                       help='Build all packages (default)')
    parser.add_argument('--clean', action='store_true',
                       help='Clean previous builds first')
    parser.add_argument('--test', action='store_true',
                       help='Test packages after building')
    
    args = parser.parse_args()
    
    # Default to --all if no specific build type specified
    if not any([args.portable, args.msi, args.msix]):
        args.all = True
    
    print("EnBraille Windows Deployment Builder")
    print("=" * 50)
    print(f"Version: {get_version()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {sys.platform}")
    print()
    
    # Check global prerequisites
    if not check_global_prerequisites():
        sys.exit(1)
    
    # Clean if requested
    if args.clean:
        clean_builds()
    
    # Build packages
    build_results = {}
    
    if args.all or args.portable:
        build_results['portable'] = run_build_script(
            'build_portable_windows.py',
            'Building Portable ZIP Distribution'
        )
    
    if args.all or args.msi:
        build_results['msi'] = run_build_script(
            'build_msi_installer.py', 
            'Building MSI Installer for winget'
        )
    
    if args.all or args.msix:
        build_results['msix'] = run_build_script(
            'build_msix_package.py',
            'Building MSIX Package for Microsoft Store'
        )
    
    # Test packages if requested
    if args.test:
        test_results = test_packages()
    else:
        test_results = True
    
    # Create deployment summary
    if any(build_results.values()):
        create_deployment_summary()
    
    # Print final results
    print(f"\n{'='*60}")
    print("🎯 DEPLOYMENT RESULTS")
    print(f"{'='*60}")
    
    success_count = 0
    total_count = len(build_results)
    
    for package_type, success in build_results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{package_type.upper():>10}: {status}")
        if success:
            success_count += 1
    
    if args.test:
        test_status = "✅ PASSED" if test_results else "❌ FAILED"
        print(f"{'TESTING':>10}: {test_status}")
    
    print(f"\n📊 Summary: {success_count}/{total_count} packages built successfully")
    
    if success_count == total_count and (not args.test or test_results):
        print("🎉 All deployments completed successfully!")
        print("\n📁 Check the dist/ directory for generated packages")
        print("📄 See DEPLOYMENT_SUMMARY.md for next steps")
        sys.exit(0)
    else:
        print("❌ Some deployments failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()