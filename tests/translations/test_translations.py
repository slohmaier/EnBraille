#!/usr/bin/env python3
"""
Test script to verify German translations work in the GUI
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tools')))

import translation_helper
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

def test_gui_translations():
    """Test that GUI components use German translations"""
    
    # Load German translations
    translation_helper.load_translations('de')
    translation_helper.patch_qt_tr()
    
    app = QApplication([])
    
    # Create a simple test widget
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Test various strings that should be translated
    test_cases = [
        "Welcome to EnBraille",
        "Settings", 
        "About",
        "Text to BRF",
        "Error",
        "Choose file",
        "Braille table:"
    ]
    
    print("Testing GUI translations:")
    print("=" * 40)
    
    for original_text in test_cases:
        # Test direct translation
        translated = translation_helper.tr(original_text)
        
        # Test Qt widget translation
        label = QLabel()
        label.setText(label.tr(original_text))
        qt_translated = label.text()
        
        print(f"Original: {original_text}")
        print(f"Direct:   {translated}")
        print(f"Qt GUI:   {qt_translated}")
        print(f"Match:    {'✅' if translated == qt_translated else '❌'}")
        print("-" * 40)
        
        layout.addWidget(label)
    
    # Show the widget briefly to verify visually
    widget.setWindowTitle("German Translation Test")
    widget.show()
    
    # Process events briefly then close
    app.processEvents()
    
    print("✅ GUI translation test completed!")
    return True

if __name__ == "__main__":
    test_gui_translations()