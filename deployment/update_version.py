#!/usr/bin/env python3
"""
Update version numbers across all deployment files
"""

import sys
import re
from pathlib import Path

def update_version(new_version):
    """Update version in all relevant files"""
    print(f"🔄 Updating version to {new_version}")
    
    project_root = Path(__file__).parent.parent
    
    # Files to update with their patterns
    files_to_update = [
        {
            'file': project_root / 'setup.py',
            'pattern': r"version='[^']*'",
            'replacement': f"version='{new_version}'"
        },
        {
            'file': project_root / 'deployment/macos/Info.plist',
            'pattern': r'<key>CFBundleVersion</key>\s*<string>[^<]*</string>',
            'replacement': f'<key>CFBundleVersion</key>\n    <string>{new_version}</string>'
        },
        {
            'file': project_root / 'deployment/macos/Info.plist',
            'pattern': r'<key>CFBundleShortVersionString</key>\s*<string>[^<]*</string>',
            'replacement': f'<key>CFBundleShortVersionString</key>\n    <string>{new_version}</string>'
        }
    ]
    
    # Update About dialog version in GUI
    gui_file = project_root / 'enbraille_gui.py'
    if gui_file.exists():
        files_to_update.append({
            'file': gui_file,
            'pattern': r"Version 1\.0 - Professional Braille Conversion Tool",
            'replacement': f"Version {new_version} - Professional Braille Conversion Tool"
        })
    
    updated_count = 0
    
    for file_info in files_to_update:
        file_path = file_info['file']
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply replacement
            new_content, count = re.subn(
                file_info['pattern'],
                file_info['replacement'],
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            if count > 0:
                # Write back updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Updated {file_path.name} ({count} replacement(s))")
                updated_count += 1
            else:
                print(f"⚠️  No version found to update in {file_path.name}")
                
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
    
    print(f"\n🎉 Updated version to {new_version} in {updated_count} file(s)")
    
    # Show next steps
    print(f"\nNext steps:")
    print(f"1. Test the application with new version")
    print(f"2. Commit changes: git commit -am 'Update version to {new_version}'")
    print(f"3. Tag release: git tag v{new_version}")
    print(f"4. Build and deploy: ./deploy_to_appstore.sh")

def get_current_version():
    """Get current version from setup.py"""
    setup_file = Path(__file__).parent.parent / 'setup.py'
    
    if not setup_file.exists():
        return "Unknown"
    
    try:
        with open(setup_file, 'r') as f:
            content = f.read()
        
        match = re.search(r"version='([^']*)'", content)
        if match:
            return match.group(1)
    except Exception:
        pass
    
    return "Unknown"

def main():
    if len(sys.argv) != 2:
        current_version = get_current_version()
        print(f"Usage: {sys.argv[0]} <new_version>")
        print(f"Current version: {current_version}")
        print(f"Example: {sys.argv[0]} 1.0.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format (basic check)
    if not re.match(r'^\d+\.\d+(\.\d+)?$', new_version):
        print("❌ Invalid version format. Use: major.minor or major.minor.patch")
        sys.exit(1)
    
    update_version(new_version)

if __name__ == "__main__":
    main()