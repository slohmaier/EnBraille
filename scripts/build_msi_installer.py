#!/usr/bin/env python3
"""
Windows MSI Installer Build Script for EnBraille

This script creates an MSI installer for Windows Package Manager (winget).
Uses cx_Freeze to create the executable and WiX Toolset to create the MSI.

Prerequisites:
- Python 3.8+
- cx_Freeze: pip install cx_freeze
- WiX Toolset v3: https://wixtoolset.org/releases/
- All EnBraille dependencies installed

Usage:
    python scripts/build_msi_installer.py

Output:
    dist/EnBraille_v{version}.msi
    dist/EnBraille_winget_manifest.yaml (for winget submission)
"""

import os
import sys
import shutil
import subprocess
import uuid
from pathlib import Path
import xml.etree.ElementTree as ET


def check_prerequisites():
    """Check if required tools are available"""
    missing = []
    
    # Check cx_Freeze
    try:
        import cx_Freeze
        print(f"✅ Found cx_Freeze {cx_Freeze.__version__}")
    except ImportError:
        missing.append("cx_Freeze (pip install cx_freeze)")
    
    # cx_Freeze creates MSI files directly, no WiX needed
    print("✅ cx_Freeze handles MSI creation directly")
    
    if missing:
        print("❌ Missing prerequisites:")
        for item in missing:
            print(f"   - {item}")
        return False
    
    return True


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



def create_setup_py():
    """Create setup.py for cx_Freeze"""
    version = get_version()
    
    setup_content = f'''#!/usr/bin/env python3
"""
cx_Freeze setup script for EnBraille MSI installer
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {{
    "packages": [
        "PySide6.QtCore",
        "PySide6.QtGui", 
        "PySide6.QtWidgets",
        "louis",
        "ebooklib",
        "markdown",
        "tools.translation_helper",
        "translations.enbraille_de"
    ],
    "include_files": [
        ("resources/", "resources/"),
        ("translations/", "translations/"),
        ("tools/", "tools/"),
        ("enbraille_resources_rc.py", "enbraille_resources_rc.py"),
    ],
    "excludes": [
        "tkinter",
        "matplotlib", 
        "numpy",
        "PIL",
        "unittest",
        "test"
    ]
}}

# MSI options
bdist_msi_options = {{
    "upgrade_code": "{{{str(uuid.uuid4()).upper()}}}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\\EnBraille",
    "install_icon": "resources/assets/Icon_Simple.ico"
}}

# Executable
base = "Win32GUI"  # Use Win32GUI to hide console
executables = [
    Executable(
        "enbraille_main.py",
        base=base,
        target_name="EnBraille.exe",
        icon="resources/assets/Icon_Simple.ico",
        shortcut_name="EnBraille",
        shortcut_dir="DesktopFolder"
    )
]

setup(
    name="EnBraille",
    version="{version}",
    description="Professional Braille Conversion Tool",
    long_description="Convert text and documents to braille format with support for multiple languages and document types.",
    author="Stefan Lohmaier",
    author_email="info@slohmaier.de",
    url="https://github.com/slohmaier/EnBraille",
    license="GPL-3.0",
    options={{
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    }},
    executables=executables
)
'''
    
    with open('setup_msi.py', 'w') as f:
        f.write(setup_content)
    
    print("📝 Created setup_msi.py")


def build_msi():
    """Build MSI installer"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    version = get_version()
    print(f"🔨 Building EnBraille MSI Installer v{version}")
    
    # Clean previous builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    if dist_dir.exists():
        print("🧹 Cleaning previous dist...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        print("🧹 Cleaning previous build...")
        shutil.rmtree(build_dir)
    
    # Create setup.py
    create_setup_py()
    
    # Build MSI
    print("🚀 Building MSI with cx_Freeze...")
    result = subprocess.run([
        sys.executable, "setup_msi.py", "bdist_msi"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ MSI build failed:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("✅ MSI build completed")
    
    # Find the generated MSI file
    msi_files = list((project_root / "dist").glob("*.msi"))
    if not msi_files:
        print("❌ No MSI file found in dist/")
        return False
    
    original_msi = msi_files[0]
    target_msi = project_root / "dist" / f"EnBraille_v{version}.msi"
    
    # Rename MSI file
    original_msi.rename(target_msi)
    print(f"✅ MSI created: {target_msi}")
    
    # Get file size and hash for winget manifest
    file_size = target_msi.stat().st_size
    
    # Calculate SHA256 hash
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(target_msi, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()
    
    print(f"📊 File size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
    print(f"🔒 SHA256: {file_hash}")
    
    # Create winget manifest
    create_winget_manifest(version, file_size, file_hash)
    
    # Clean up
    setup_file = project_root / "setup_msi.py"
    if setup_file.exists():
        setup_file.unlink()
    
    return True


def create_winget_manifest(version, file_size, file_hash):
    """Create winget package manifest"""
    manifest_content = f'''# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.1.4.0.schema.json

PackageIdentifier: slohmaier.EnBraille
PackageVersion: {version}
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.4.0

---
# yaml-language-server: $schema=https://aka.ms/winget-manifest.defaultLocale.1.4.0.schema.json

PackageIdentifier: slohmaier.EnBraille
PackageVersion: {version}
PackageLocale: en-US
Publisher: Stefan Lohmaier
PublisherUrl: https://slohmaier.de
PublisherSupportUrl: https://github.com/slohmaier/EnBraille/issues
Author: Stefan Lohmaier
PackageName: EnBraille
PackageUrl: https://github.com/slohmaier/EnBraille
License: GPL-3.0
LicenseUrl: https://github.com/slohmaier/EnBraille/blob/main/LICENSE
Copyright: Copyright (c) 2024 Stefan Lohmaier
ShortDescription: Professional Braille conversion tool for Windows
Description: |
  EnBraille is a powerful, accessible application for converting text and documents 
  into braille format. Features include:
  
  • Convert plain text to braille (BRF format)
  • Process EPUB and Markdown documents  
  • Reformat existing braille files
  • Support for multiple braille tables and languages
  • Grade 1 and Grade 2 braille translation
  • Fully accessible interface with screen reader support
  • Clean, intuitive design
  
  Perfect for educators, students, and accessibility professionals.
Moniker: enbraille
Tags:
- accessibility
- braille
- conversion
- education
- screen-reader
- text-to-braille
- brf
- epub
- markdown
ReleaseDate: 2024-08-29
ManifestType: defaultLocale
ManifestVersion: 1.4.0

---
# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.1.4.0.schema.json

PackageIdentifier: slohmaier.EnBraille
PackageVersion: {version}
Platform:
- Windows.Desktop
MinimumOSVersion: 10.0.0.0
InstallerType: wix
Scope: machine
InstallModes:
- interactive
- silent
- silentWithProgress
UpgradeBehavior: install
FileExtensions:
- brf
- txt
- epub
- md
Installers:
- Architecture: x64
  InstallerUrl: https://github.com/slohmaier/EnBraille/releases/download/v{version}/EnBraille_v{version}.msi
  InstallerSha256: {file_hash.upper()}
  InstallerSizeInBytes: {file_size}
ManifestType: installer
ManifestVersion: 1.4.0
'''
    
    manifest_file = Path("dist") / "EnBraille_winget_manifest.yaml"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    print(f"📄 Created winget manifest: {manifest_file}")


def main():
    """Main function"""
    print("EnBraille Windows MSI Installer Builder")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    if not build_msi():
        sys.exit(1)
    
    print("\n🎉 MSI installer build completed successfully!")
    print("\nNext steps:")
    print("1. Test the MSI installer")
    print("2. Upload MSI to GitHub releases")
    print("3. Submit winget manifest to microsoft/winget-pkgs repository")
    print("4. Update the InstallerUrl in the manifest with the actual GitHub release URL")


if __name__ == "__main__":
    main()