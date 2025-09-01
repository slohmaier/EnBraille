#!/usr/bin/env python3
"""
Build script for creating macOS app bundle for EnBraille
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_macos_app():
    """Build macOS app bundle using py2app"""
    print("=== EnBraille macOS App Builder ===\n")
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    print(f"Building from: {project_root}")
    
    # Clean previous builds
    if os.path.exists("build"):
        print("Cleaning previous build...")
        shutil.rmtree("build")
    if os.path.exists("dist"):
        print("Cleaning previous dist...")
        shutil.rmtree("dist")
    
    # Create setup_app.py for py2app
    setup_app_content = '''
from setuptools import setup
import os

# Get absolute path to assets - hardcode the path since relative paths are problematic
icon_path = 'resources/assets/Icon_Enhanced.icns'

APP = ['enbraille_main.py']
DATA_FILES = []

OPTIONS = {
    'iconfile': icon_path if os.path.exists(icon_path) else None,
    'plist': {
        'CFBundleName': 'EnBraille',
        'CFBundleDisplayName': 'EnBraille', 
        'CFBundleIdentifier': 'com.slohmaier.enbraille',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSHumanReadableCopyright': 'Copyright © 2024 Stefan Lohmaier',
        'NSSupportsVoiceOver': True,
        'NSSupportsScreenReader': True,
    },
    'packages': ['PySide6', 'markdown', 'ebooklib'],
    'includes': [
        'enbraille_gui', 'enbraille_data', 'enbraille_resources_rc', 
        'enbraille_tools', 'enbraille_widgets', 'libbrl'
    ],
    'excludes': ['tkinter'],
    'strip': False,
    'optimize': 1,
}

setup(
    name='EnBraille',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
'''
    
    with open("setup_app.py", "w") as f:
        f.write(setup_app_content)
    
    print("Created setup_app.py for py2app")
    
    # Install py2app if needed
    try:
        import py2app
        print("py2app is available")
    except ImportError:
        print("Installing py2app...")
        subprocess.run([sys.executable, "-m", "pip", "install", "py2app"], check=True)
    
    # Build the app
    print("Building app bundle...")
    try:
        subprocess.run([
            sys.executable, "setup_app.py", "py2app",
            "--arch", "universal2",  # Support both Intel and Apple Silicon
        ], check=True)
        
        print("✅ App bundle created successfully!")
        
        # Copy entitlements and Info.plist to the bundle
        app_path = Path("dist/EnBraille.app")
        if app_path.exists():
            # Copy custom Info.plist
            custom_plist = Path("deployment/macos/Info.plist")
            app_plist = app_path / "Contents/Info.plist"
            if custom_plist.exists():
                shutil.copy2(custom_plist, app_plist)
                print("✅ Custom Info.plist copied to app bundle")
            
            print(f"\n📦 App bundle location: {app_path.absolute()}")
            print(f"📏 Bundle size: {get_folder_size(app_path):.1f} MB")
            
            # Verify bundle structure
            verify_bundle_structure(app_path)
            
        else:
            print("❌ App bundle was not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    # Clean up
    os.remove("setup_app.py")
    
    return True

def get_folder_size(folder_path):
    """Get folder size in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)

def verify_bundle_structure(app_path):
    """Verify the app bundle has correct structure"""
    print("\n🔍 Verifying bundle structure:")
    
    required_paths = [
        "Contents/MacOS/EnBraille",
        "Contents/Info.plist", 
        "Contents/Resources",
    ]
    
    for rel_path in required_paths:
        full_path = app_path / rel_path
        if full_path.exists():
            print(f"   ✅ {rel_path}")
        else:
            print(f"   ❌ {rel_path} - Missing!")
    
    # Check for icon
    icon_paths = [
        "Contents/Resources/Icon.icns",
        "Contents/Resources/Icon_Enhanced.icns", 
    ]
    
    icon_found = False
    for icon_path in icon_paths:
        if (app_path / icon_path).exists():
            print(f"   ✅ {icon_path}")
            icon_found = True
            break
    
    if not icon_found:
        print(f"   ⚠️  No icon found (looked for: {', '.join(icon_paths)})")

if __name__ == "__main__":
    success = build_macos_app()
    sys.exit(0 if success else 1)