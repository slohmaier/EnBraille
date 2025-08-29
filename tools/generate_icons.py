#!/usr/bin/env python3
"""
Generate different sized PNG icons from SVG source
"""

import os
import sys
import subprocess
from pathlib import Path

def generate_icon_sizes():
    """Generate various icon sizes from SVG sources"""
    
    # Define the project root and paths
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "resources" / "assets"
    
    # SVG source files
    svg_files = {
        "Icon_Enhanced.svg": "Icon_Enhanced",
        "Icon_Compact.svg": "Icon_Compact", 
        "Icon.svg": "Icon"
    }
    
    # Target sizes for different use cases
    sizes = {
        16: "systray",      # System tray
        24: "small",        # Small toolbar
        32: "medium",       # Standard toolbar  
        48: "large",        # Large icons
        64: "xlarge",       # Extra large
        128: "xxlarge",     # App launcher
        256: "huge",        # High DPI
        512: "original"     # Full resolution
    }
    
    print("🎨 EnBraille Icon Generator")
    print("=" * 40)
    
    # Check if we have SVG files
    for svg_file in svg_files.keys():
        svg_path = assets_dir / svg_file
        if not svg_path.exists():
            print(f"❌ SVG file not found: {svg_file}")
            continue
            
        print(f"\n📂 Processing {svg_file}...")
        base_name = svg_files[svg_file]
        
        # Try different methods to convert SVG to PNG
        success = False
        
        # Method 1: Try using cairosvg (Python library)
        try:
            import cairosvg
            print("   Using cairosvg...")
            
            for size, suffix in sizes.items():
                output_file = assets_dir / f"{base_name}_{size}px.png"
                cairosvg.svg2png(
                    url=str(svg_path),
                    write_to=str(output_file),
                    output_width=size,
                    output_height=size
                )
                print(f"   ✅ Generated {size}x{size} -> {output_file.name}")
            
            success = True
            
        except ImportError:
            print("   cairosvg not available, trying alternatives...")
            
        # Method 2: Try using Inkscape command line
        if not success:
            try:
                # Test if Inkscape is available
                result = subprocess.run(['inkscape', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("   Using Inkscape...")
                    
                    for size, suffix in sizes.items():
                        output_file = assets_dir / f"{base_name}_{size}px.png"
                        subprocess.run([
                            'inkscape',
                            '--export-type=png',
                            f'--export-filename={output_file}',
                            f'--export-width={size}',
                            f'--export-height={size}',
                            str(svg_path)
                        ], check=True, capture_output=True)
                        print(f"   ✅ Generated {size}x{size} -> {output_file.name}")
                    
                    success = True
                    
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                print("   Inkscape not available...")
        
        # Method 3: Manual instructions if no tools available
        if not success:
            print(f"   ⚠️  No SVG conversion tools found for {svg_file}")
            print(f"   💡 Manual conversion needed:")
            print(f"      - Open {svg_file} in image editor (GIMP, Inkscape, etc.)")
            print(f"      - Export as PNG at different sizes: {list(sizes.keys())}")
    
    print("\n🎯 Icon Generation Summary:")
    print("- Enhanced version: Better for larger displays")
    print("- Compact version: Optimized for small sizes (systray)")
    print("- Original version: Clean, minimal design")
    
    print("\n💡 Usage in Qt applications:")
    print("- Set app icon: app.setWindowIcon(QIcon('path/to/icon.png'))")
    print("- System tray: tray.setIcon(QIcon('path/to/Icon_Compact_16px.png'))")
    
    return success

def create_ico_file():
    """Create Windows .ico file with multiple sizes"""
    try:
        from PIL import Image
        
        assets_dir = Path(__file__).parent.parent / "resources" / "assets"
        
        # Collect different sizes for ICO file
        ico_sizes = [16, 24, 32, 48, 64, 128, 256]
        images = []
        
        for size in ico_sizes:
            png_file = assets_dir / f"Icon_Compact_{size}px.png"
            if png_file.exists():
                img = Image.open(png_file)
                images.append(img)
        
        if images:
            ico_file = assets_dir / "EnBraille.ico"
            images[0].save(ico_file, format='ICO', sizes=[(img.width, img.height) for img in images])
            print(f"✅ Created Windows ICO file: {ico_file.name}")
            return True
        else:
            print("❌ No PNG files found for ICO creation")
            return False
            
    except ImportError:
        print("💡 Install Pillow to create ICO files: pip install Pillow")
        return False

if __name__ == "__main__":
    print("Starting icon generation...")
    
    svg_success = generate_icon_sizes()
    
    if svg_success:
        print("\nCreating Windows ICO file...")
        create_ico_file()
    
    print("\n✅ Icon generation completed!")
    
    # Instructions for manual conversion if needed
    if not svg_success:
        print("\n📋 Manual Conversion Instructions:")
        print("1. Open the SVG files in an image editor (GIMP, Inkscape, Photoshop)")
        print("2. Export/Save As PNG at these sizes:")
        for size in [16, 24, 32, 48, 64, 128, 256, 512]:
            print(f"   - {size}x{size} pixels")
        print("3. Name them: Icon_Enhanced_{size}px.png")
        print("4. Place in resources/assets/ directory")