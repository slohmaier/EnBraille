#!/usr/bin/env python3
"""
Validate the built app bundle for App Store submission
"""

import os
import sys
import plistlib
import subprocess
from pathlib import Path

def validate_app_bundle():
    """Validate the app bundle meets App Store requirements"""
    print("=== EnBraille Bundle Validation ===\n")
    
    # Find the app bundle
    project_root = Path(__file__).parent.parent.parent
    app_bundle = project_root / "dist" / "EnBraille.app"
    
    if not app_bundle.exists():
        print("❌ App bundle not found. Run build_app.py first.")
        return False
    
    print(f"📦 Validating: {app_bundle}")
    
    # Check bundle structure
    success = True
    success &= check_bundle_structure(app_bundle)
    success &= check_info_plist(app_bundle)
    success &= check_code_signature(app_bundle)
    success &= check_entitlements(app_bundle)
    success &= check_bundle_identifier(app_bundle)
    success &= check_accessibility_features(app_bundle)
    
    print(f"\n{'✅ Bundle validation passed!' if success else '❌ Bundle validation failed!'}")
    return success

def check_bundle_structure(app_bundle):
    """Check required bundle structure"""
    print("🏗️  Checking bundle structure...")
    
    required_paths = [
        "Contents/MacOS/EnBraille",
        "Contents/Info.plist",
        "Contents/Resources",
        "Contents/Frameworks",  # Should contain Python and dependencies
    ]
    
    all_good = True
    for rel_path in required_paths:
        full_path = app_bundle / rel_path
        if full_path.exists():
            print(f"   ✅ {rel_path}")
        else:
            print(f"   ❌ {rel_path} - Missing!")
            all_good = False
    
    # Check for executable permissions
    executable = app_bundle / "Contents/MacOS/EnBraille"
    if executable.exists():
        if os.access(executable, os.X_OK):
            print("   ✅ Executable has proper permissions")
        else:
            print("   ❌ Executable missing execute permissions")
            all_good = False
    
    return all_good

def check_info_plist(app_bundle):
    """Check Info.plist contents"""
    print("📄 Checking Info.plist...")
    
    plist_path = app_bundle / "Contents/Info.plist"
    if not plist_path.exists():
        print("   ❌ Info.plist not found")
        return False
    
    try:
        with open(plist_path, 'rb') as f:
            plist_data = plistlib.load(f)
        
        required_keys = {
            'CFBundleIdentifier': 'com.slohmaier.enbraille',
            'CFBundleName': 'EnBraille',
            'CFBundleDisplayName': 'EnBraille',
            'CFBundleVersion': None,  # Should exist but any value OK
            'CFBundleShortVersionString': None,
            'LSApplicationCategoryType': 'public.app-category.utilities',
            'NSHighResolutionCapable': True,
            'NSSupportsVoiceOver': True,
        }
        
        all_good = True
        for key, expected_value in required_keys.items():
            if key in plist_data:
                actual_value = plist_data[key]
                if expected_value is None or actual_value == expected_value:
                    print(f"   ✅ {key}: {actual_value}")
                else:
                    print(f"   ❌ {key}: Expected '{expected_value}', got '{actual_value}'")
                    all_good = False
            else:
                print(f"   ❌ {key}: Missing")
                all_good = False
        
        # Check document types
        if 'CFBundleDocumentTypes' in plist_data:
            doc_types = plist_data['CFBundleDocumentTypes']
            print(f"   ✅ CFBundleDocumentTypes: {len(doc_types)} document type(s)")
        else:
            print("   ⚠️  CFBundleDocumentTypes: Missing (optional)")
        
        return all_good
        
    except Exception as e:
        print(f"   ❌ Error reading Info.plist: {e}")
        return False

def check_code_signature(app_bundle):
    """Check code signature"""
    print("🔑 Checking code signature...")
    
    try:
        # Check if bundle is signed
        result = subprocess.run(
            ["codesign", "--verify", "--verbose=4", str(app_bundle)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ Code signature valid")
            
            # Get signature details
            result = subprocess.run(
                ["codesign", "--display", "--verbose=4", str(app_bundle)],
                capture_output=True,
                text=True
            )
            
            if "Developer ID" in result.stderr or "3rd Party Mac Developer" in result.stderr:
                print("   ✅ Signed with appropriate certificate")
            else:
                print("   ⚠️  Signature present but may not be App Store compatible")
                print("       Make sure to use '3rd Party Mac Developer Application' certificate")
            
            return True
        else:
            print("   ❌ Code signature verification failed")
            print(f"       Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("   ❌ codesign tool not found - install Xcode Command Line Tools")
        return False
    except Exception as e:
        print(f"   ❌ Error checking signature: {e}")
        return False

def check_entitlements(app_bundle):
    """Check entitlements"""
    print("🛡️  Checking entitlements...")
    
    try:
        result = subprocess.run(
            ["codesign", "--display", "--entitlements", "-", str(app_bundle)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout:
            print("   ✅ Entitlements present")
            
            # Check for key entitlements
            entitlements_xml = result.stdout
            
            required_entitlements = [
                "com.apple.security.app-sandbox",
                "com.apple.security.files.user-selected.read-write",
                "com.apple.security.network.client",
            ]
            
            for entitlement in required_entitlements:
                if entitlement in entitlements_xml:
                    print(f"   ✅ {entitlement}")
                else:
                    print(f"   ❌ {entitlement} - Missing")
            
            return True
        else:
            print("   ❌ No entitlements found or error reading them")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking entitlements: {e}")
        return False

def check_bundle_identifier(app_bundle):
    """Verify bundle identifier consistency"""
    print("🆔 Checking bundle identifier...")
    
    try:
        result = subprocess.run(
            ["codesign", "--display", "--verbose=1", str(app_bundle)],
            capture_output=True,
            text=True
        )
        
        if "com.slohmaier.enbraille" in result.stderr:
            print("   ✅ Bundle identifier: com.slohmaier.enbraille")
            return True
        else:
            print("   ❌ Bundle identifier mismatch or not found")
            print(f"       Output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking bundle identifier: {e}")
        return False

def check_accessibility_features(app_bundle):
    """Check accessibility-related configuration"""
    print("♿ Checking accessibility features...")
    
    plist_path = app_bundle / "Contents/Info.plist"
    if not plist_path.exists():
        return False
    
    try:
        with open(plist_path, 'rb') as f:
            plist_data = plistlib.load(f)
        
        accessibility_keys = {
            'NSSupportsVoiceOver': True,
            'NSSupportsScreenReader': True,
        }
        
        all_good = True
        for key, expected in accessibility_keys.items():
            if key in plist_data and plist_data[key] == expected:
                print(f"   ✅ {key}: {plist_data[key]}")
            else:
                print(f"   ⚠️  {key}: Missing or not set to {expected}")
                # This is a warning, not a failure
        
        return all_good
        
    except Exception as e:
        print(f"   ❌ Error checking accessibility features: {e}")
        return False

if __name__ == "__main__":
    success = validate_app_bundle()
    sys.exit(0 if success else 1)