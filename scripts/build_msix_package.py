#!/usr/bin/env python3
"""
Windows MSIX Package Build Script for EnBraille

This script creates an MSIX package for Microsoft Store submission.
Uses PyInstaller for executable creation and Windows SDK tools for MSIX packaging.

Prerequisites:
- Python 3.8+
- PyInstaller: pip install pyinstaller
- Windows 10 SDK (for makeappx.exe and signtool.exe)
- All EnBraille dependencies installed

Usage:
    python scripts/build_msix_package.py

Output:
    dist/EnBraille_v{version}.msix
    dist/EnBraille_Store_Assets/ (app icons and screenshots)
"""

import os
import sys
import shutil
import subprocess
import json
import uuid
from pathlib import Path


def check_prerequisites():
    """Check if required tools are available"""
    missing = []
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ Found PyInstaller {PyInstaller.__version__}")
    except ImportError:
        missing.append("PyInstaller (pip install pyinstaller)")
    
    # Check Windows SDK tools
    sdk_tools = ['makeappx', 'signtool']
    for tool in sdk_tools:
        try:
            result = subprocess.run([tool, '/?'], capture_output=True, shell=True)
            if result.returncode == 0:
                print(f"✅ Found {tool}")
            else:
                missing.append(f"Windows SDK ({tool})")
        except FileNotFoundError:
            missing.append(f"Windows SDK ({tool})")
    
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


def create_app_manifest(version, package_dir):
    """Create AppxManifest.xml for MSIX package"""
    
    manifest_content = f'''<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
         xmlns:desktop="http://schemas.microsoft.com/appx/manifest/desktop/windows10">
  
  <Identity Name="slohmaier.EnBraille"
            Publisher="CN=Stefan Lohmaier"
            Version="{version}.0"
            ProcessorArchitecture="x64" />
  
  <Properties>
    <DisplayName>EnBraille</DisplayName>
    <PublisherDisplayName>Stefan Lohmaier</PublisherDisplayName>
    <Logo>Assets\\StoreLogo.png</Logo>
    <Description>Professional Braille conversion tool for Windows. Convert text and documents to braille format with accessibility features.</Description>
    <PackageIntegrityLevel>mediumIL</PackageIntegrityLevel>
    <PackageIntegrityPolicy>optional</PackageIntegrityPolicy>
  </Properties>
  
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.22621.0" />
    <PackageDependency Name="Microsoft.VCLibs.140.00" MinVersion="14.0.24217.0" Publisher="CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US" />
  </Dependencies>
  
  <Resources>
    <Resource Language="en-US" />
    <Resource Language="de-DE" />
  </Resources>
  
  <Applications>
    <Application Id="EnBraille" Executable="EnBraille.exe" EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="EnBraille"
                         Description="Professional Braille conversion tool"
                         BackgroundColor="transparent"
                         Square150x150Logo="Assets\\Square150x150Logo.png"
                         Square44x44Logo="Assets\\Square44x44Logo.png">
        <uap:DefaultTile Wide310x150Logo="Assets\\Wide310x150Logo.png"
                        Square310x310Logo="Assets\\LargeTile.png"
                        Square71x71Logo="Assets\\SmallTile.png"
                        ShortName="EnBraille">
          <uap:ShowNameOnTiles>
            <uap:ShowOn Tile="square150x150Logo"/>
            <uap:ShowOn Tile="wide310x150Logo"/>
            <uap:ShowOn Tile="square310x310Logo"/>
          </uap:ShowNameOnTiles>
        </uap:DefaultTile>
        <uap:SplashScreen Image="Assets\\SplashScreen.png" />
      </uap:VisualElements>
      
      <Extensions>
        <uap:Extension Category="windows.fileTypeAssociation">
          <uap:FileTypeAssociation Name="braille">
            <uap:DisplayName>Braille Files</uap:DisplayName>
            <uap:SupportedFileTypes>
              <uap:FileType ContentType="text/plain">.brf</uap:FileType>
              <uap:FileType ContentType="text/plain">.txt</uap:FileType>
              <uap:FileType ContentType="application/epub+zip">.epub</uap:FileType>
              <uap:FileType ContentType="text/markdown">.md</uap:FileType>
            </uap:SupportedFileTypes>
          </uap:FileTypeAssociation>
        </uap:Extension>
      </Extensions>
    </Application>
  </Applications>
  
  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
    <uap:Capability Name="documentsLibrary" />
  </Capabilities>
</Package>'''
    
    manifest_file = package_dir / "AppxManifest.xml"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    print(f"📝 Created AppxManifest.xml")


def create_store_assets(assets_dir):
    """Create Microsoft Store assets from existing icons"""
    
    # Asset sizes needed for Store
    store_assets = {
        'Square44x44Logo.png': 44,
        'Square71x71Logo.png': 71, 
        'Square150x150Logo.png': 150,
        'Square310x310Logo.png': 310,
        'Wide310x150Logo.png': (310, 150),
        'StoreLogo.png': 50,
        'SplashScreen.png': (620, 300),
        'LargeTile.png': 310
    }
    
    source_icon = Path("resources/assets/Icon_Simple.svg")
    
    print("🎨 Creating Microsoft Store assets...")
    
    for asset_name, size in store_assets.items():
        output_file = assets_dir / asset_name
        
        if isinstance(size, tuple):
            width, height = size
            cmd = [
                'inkscape',
                '--export-type=png',
                f'--export-filename={output_file}',
                f'--export-width={width}',
                f'--export-height={height}',
                str(source_icon)
            ]
        else:
            cmd = [
                'inkscape', 
                '--export-type=png',
                f'--export-filename={output_file}',
                f'--export-width={size}',
                f'--export-height={size}',
                str(source_icon)
            ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"  ✅ Created {asset_name}")
        except subprocess.CalledProcessError:
            print(f"  ⚠️  Failed to create {asset_name}, using placeholder")
            # Create a simple placeholder
            from PIL import Image, ImageDraw
            if isinstance(size, tuple):
                img = Image.new('RGBA', size, (255, 215, 0, 255))  # Gold background
            else:
                img = Image.new('RGBA', (size, size), (255, 215, 0, 255))
            img.save(output_file)


def build_executable(temp_dir):
    """Build executable using PyInstaller"""
    print("🔨 Building executable with PyInstaller...")
    
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "EnBraille",
        "--onefile",  # Single executable for MSIX
        "--windowed",
        "--noconfirm",
        "--distpath", str(temp_dir),
        
        # Add data files
        "--add-data", "resources;resources",
        "--add-data", "translations;translations", 
        "--add-data", "tools;tools",
        
        # Hidden imports
        "--hidden-import", "enbraille_resources_rc",
        "--hidden-import", "tools.translation_helper",
        "--hidden-import", "translations.enbraille_de",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "louis",
        "--hidden-import", "ebooklib", 
        "--hidden-import", "markdown",
        
        "enbraille_main.py"
    ]
    
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ PyInstaller failed:")
        print("STDERR:", result.stderr)
        return False
    
    print("✅ Executable created successfully")
    return True


def create_msix_package():
    """Create MSIX package"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    version = get_version()
    print(f"📦 Building EnBraille MSIX Package v{version}")
    
    # Clean previous builds
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Create temporary package directory
    package_dir = dist_dir / "MSIXPackage"
    package_dir.mkdir()
    
    # Create Assets directory
    assets_dir = package_dir / "Assets"
    assets_dir.mkdir()
    
    # Build executable
    if not build_executable(package_dir):
        return False
    
    # Create app manifest
    create_app_manifest(version, package_dir)
    
    # Create store assets
    create_store_assets(assets_dir)
    
    # Create MSIX package
    msix_file = dist_dir / f"EnBraille_v{version}.msix"
    
    print("📦 Creating MSIX package...")
    makeappx_cmd = [
        'makeappx',
        'pack',
        '/d', str(package_dir),
        '/p', str(msix_file),
        '/overwrite'
    ]
    
    result = subprocess.run(makeappx_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ MSIX packaging failed:")
        print("STDERR:", result.stderr)
        return False
    
    print(f"✅ MSIX package created: {msix_file}")
    
    # Create Store submission assets
    store_assets_dir = dist_dir / "EnBraille_Store_Assets"
    if store_assets_dir.exists():
        shutil.rmtree(store_assets_dir)
    shutil.copytree(assets_dir, store_assets_dir)
    
    # Create Store listing info
    create_store_listing_info(store_assets_dir, version)
    
    file_size = msix_file.stat().st_size / (1024 * 1024)
    print(f"📊 MSIX size: {file_size:.1f} MB")
    
    return True


def create_store_listing_info(assets_dir, version):
    """Create Store listing information file"""
    
    listing_info = {
        "packageInfo": {
            "name": "EnBraille",
            "version": version,
            "publisher": "Stefan Lohmaier",
            "description": "Professional Braille conversion tool for Windows"
        },
        "storeListingSuggestions": {
            "title": "EnBraille - Braille Converter",
            "subtitle": "Convert text and documents to braille",
            "description": "EnBraille is a powerful, accessible application for converting text and documents into braille format. Perfect for educators, students, and accessibility professionals.\n\nKEY FEATURES:\n• Convert plain text to braille (BRF format)\n• Process EPUB and Markdown documents\n• Reformat existing braille files\n• Support for multiple braille tables and languages\n• Grade 1 and Grade 2 braille translation\n• Fully accessible interface with screen reader support\n• Clean, intuitive design\n\nACCESSIBILITY FIRST:\nEnBraille is designed with accessibility in mind, featuring complete screen reader support, keyboard navigation, and clear visual design.\n\nSUPPORTED FORMATS:\n• Input: Plain text, EPUB, Markdown, existing BRF files\n• Output: Braille Ready Format (BRF)\n• Multiple braille translation tables",
            "keywords": [
                "braille",
                "accessibility", 
                "text conversion",
                "education",
                "screen reader",
                "BRF",
                "EPUB", 
                "markdown",
                "visual impairment",
                "assistive technology"
            ],
            "category": "Productivity",
            "age_rating": "3+",
            "website": "https://github.com/slohmaier/EnBraille",
            "support_website": "https://github.com/slohmaier/EnBraille/issues",
            "privacy_policy": "https://github.com/slohmaier/EnBraille/blob/main/PRIVACY.md"
        },
        "assets": {
            "app_icon": "Square150x150Logo.png",
            "store_logo": "StoreLogo.png",
            "splash_screen": "SplashScreen.png",
            "tiles": {
                "small": "Square71x71Logo.png",
                "medium": "Square150x150Logo.png", 
                "wide": "Wide310x150Logo.png",
                "large": "LargeTile.png"
            }
        },
        "screenshots_needed": [
            "Main welcome screen",
            "Text conversion interface", 
            "Document processing view",
            "Settings/preferences",
            "Accessibility features demonstration"
        ]
    }
    
    info_file = assets_dir / "store_listing_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(listing_info, f, indent=2)
    
    print(f"📄 Created store listing info: {info_file}")


def main():
    """Main function"""
    print("EnBraille Windows MSIX Package Builder")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    if not create_msix_package():
        sys.exit(1)
    
    print("\n🎉 MSIX package build completed successfully!")
    print("\nNext steps:")
    print("1. Test the MSIX package installation")
    print("2. Sign the package with a trusted certificate for Store submission")
    print("3. Submit to Microsoft Store via Partner Center")
    print("4. Use assets in dist/EnBraille_Store_Assets/ for Store listing")


if __name__ == "__main__":
    main()