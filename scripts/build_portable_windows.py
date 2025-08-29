#!/usr/bin/env python3
"""
Windows Portable Build Script for EnBraille

This script creates a portable Windows distribution using PyInstaller.
The resulting executable can run without installation on Windows systems.

Prerequisites:
- Python 3.8+
- PyInstaller: pip install pyinstaller
- All EnBraille dependencies installed

Usage:
    python scripts/build_portable_windows.py

Output:
    dist/EnBraille_Portable/EnBraille.exe (and supporting files)
    dist/EnBraille_Portable_v{version}.zip
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path


def check_prerequisites():
    """Check if PyInstaller is available"""
    try:
        import PyInstaller
        print(f"✅ Found PyInstaller {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False


def get_version():
    """Get version from main script"""
    try:
        with open('enbraille_main.py', 'r') as f:
            content = f.read()
            # Look for setApplicationVersion call
            import re
            match = re.search(r'setApplicationVersion\("([^"]+)"\)', content)
            if match:
                return match.group(1)
    except Exception:
        pass
    return "0.1.0"


def build_portable():
    """Build portable Windows executable"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    version = get_version()
    print(f"🔨 Building EnBraille Portable v{version}")
    
    # Clean previous builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    if dist_dir.exists():
        print("🧹 Cleaning previous builds...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # PyInstaller command
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "EnBraille",
        "--onedir",  # Create directory with dependencies
        "--windowed",  # No console window
        "--noconfirm",  # Overwrite without asking
        
        # Icon
        "--icon", "resources/assets/Icon_Simple_256px.png",
        
        # Add data files
        "--add-data", "resources;resources",
        "--add-data", "translations;translations",
        "--add-data", "tools;tools",
        
        # Hidden imports for dynamic imports
        "--hidden-import", "enbraille_resources_rc",
        "--hidden-import", "tools.translation_helper",
        "--hidden-import", "translations.enbraille_de",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui", 
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "louis",
        "--hidden-import", "ebooklib",
        "--hidden-import", "markdown",
        
        # Exclude unnecessary modules
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "PIL",
        
        # Entry point
        "enbraille_main.py"
    ]
    
    print("🚀 Running PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")
    
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ PyInstaller failed:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("✅ PyInstaller completed successfully")
    
    # Rename output directory
    original_dist = dist_dir / "EnBraille"
    portable_dist = dist_dir / "EnBraille_Portable"
    
    if original_dist.exists():
        original_dist.rename(portable_dist)
    
    # Copy additional files
    additional_files = [
        "LICENSE",
        "README.md",
        "docs/TRANSLATIONS.md"
    ]
    
    for file in additional_files:
        src = project_root / file
        if src.exists():
            shutil.copy2(src, portable_dist / src.name)
            print(f"📄 Copied {file}")
    
    # Create version info file
    version_info = portable_dist / "version.txt"
    with open(version_info, 'w') as f:
        f.write(f"EnBraille Portable v{version}\n")
        f.write(f"Build date: {subprocess.check_output(['date', '/t'], shell=True, text=True).strip()}\n")
        f.write("For support: https://github.com/slohmaier/EnBraille\n")
    
    print(f"✅ Portable build created: {portable_dist}")
    
    # Create ZIP archive
    zip_path = dist_dir / f"EnBraille_Portable_v{version}.zip"
    print(f"📦 Creating ZIP archive: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in portable_dist.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(portable_dist)
                zipf.write(file_path, arcname)
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)
    print(f"✅ ZIP created: {zip_path} ({zip_size:.1f} MB)")
    
    return True


def main():
    """Main function"""
    print("EnBraille Windows Portable Builder")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    if not build_portable():
        sys.exit(1)
    
    print("\n🎉 Portable Windows build completed successfully!")
    print("\nNext steps:")
    print("1. Test the executable in dist/EnBraille_Portable/EnBraille.exe")
    print("2. Share the ZIP file for distribution")
    print("3. Upload to GitHub releases")


if __name__ == "__main__":
    main()