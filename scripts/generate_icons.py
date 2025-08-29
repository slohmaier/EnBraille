#!/usr/bin/env python3
"""
Icon Generation Script for EnBraille

This script generates PNG icons of various sizes from the SVG source file.
It requires Inkscape to be installed and available in PATH.

Usage:
    python scripts/generate_icons.py

The script will generate PNG files in the resources/assets/ directory.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_inkscape():
    """Check if Inkscape is available in PATH"""
    try:
        result = subprocess.run(['inkscape', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"Found Inkscape: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Inkscape not found in PATH")
        print("Please install Inkscape and make sure it's available in PATH")
        return False

def generate_icons():
    """Generate PNG icons from SVG source"""
    # Get script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    assets_dir = project_root / "resources" / "assets"
    svg_file = assets_dir / "Icon_Simple.svg"
    
    # Check if SVG source exists
    if not svg_file.exists():
        print(f"Error: SVG source file not found: {svg_file}")
        return False
    
    # Icon sizes to generate
    sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    
    print(f"Generating icons from: {svg_file}")
    print(f"Output directory: {assets_dir}")
    
    # Change to assets directory
    original_cwd = os.getcwd()
    os.chdir(assets_dir)
    
    try:
        for size in sizes:
            output_file = f"Icon_Simple_{size}px.png"
            print(f"  Generating {output_file} ({size}x{size})")
            
            cmd = [
                'inkscape',
                '--export-type=png',
                f'--export-filename={output_file}',
                f'--export-width={size}',
                f'--export-height={size}',
                'Icon_Simple.svg'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"    Error generating {output_file}: {result.stderr}")
                return False
            else:
                print(f"    ✓ Generated {output_file}")
        
        print("\nAll icons generated successfully!")
        print("\nNext steps:")
        print("1. Run: pyside6-rcc resources/enbraille_resources.qrc -o enbraille_resources_rc.py")
        print("2. Test the application to verify icons display correctly")
        
        return True
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

def main():
    """Main function"""
    print("EnBraille Icon Generator")
    print("=" * 40)
    
    # Check prerequisites
    if not check_inkscape():
        sys.exit(1)
    
    # Generate icons
    if not generate_icons():
        sys.exit(1)
    
    print("\nIcon generation completed successfully!")

if __name__ == "__main__":
    main()