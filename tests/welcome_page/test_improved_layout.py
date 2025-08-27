import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test the improved welcome page layout with repositioned and resized elements
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_improved_layout():
    """Test the improved welcome page layout"""
    app = QApplication(sys.argv)
    
    print("=== Improved Welcome Page Layout Test ===")
    
    # Create data and ensure welcome page is shown
    data = EnBrailleData(app)
    data.skipWelcomePage = False
    
    print("Creating window with improved layout...")
    window = EnBrailleWindow(data)
    window.show()
    
    def check_layout():
        print("\n📋 Layout Analysis:")
        
        current_page = window.currentPage()
        print(f"Current page: {current_page.__class__.__name__}")
        
        if hasattr(current_page, 'skipCheckbox') and hasattr(current_page, 'settingsButton'):
            checkbox = current_page.skipCheckbox
            button = current_page.settingsButton
            
            print(f"\n✅ Elements Found:")
            print(f"   - Skip checkbox: '{checkbox.text()}'")
            print(f"   - Settings button: '{button.text()}'")
            
            print(f"\n📐 Element Sizes:")
            print(f"   - Checkbox size: {checkbox.size().width()} x {checkbox.size().height()}")
            print(f"   - Button size: {button.size().width()} x {button.size().height()}")
            print(f"   - Button minimum size: {button.minimumWidth()} x {button.minimumHeight()}")
            
            print(f"\n📍 Element Positions:")
            checkbox_pos = checkbox.mapToGlobal(checkbox.rect().topLeft())
            button_pos = button.mapToGlobal(button.rect().topLeft())
            print(f"   - Checkbox position: ({checkbox_pos.x()}, {checkbox_pos.y()})")
            print(f"   - Button position: ({button_pos.x()}, {button_pos.y()})")
            
            print(f"\n🎨 Styling Applied:")
            print(f"   - Checkbox has custom stylesheet: {bool(checkbox.styleSheet())}")
            print(f"   - Button has custom stylesheet: {bool(button.styleSheet())}")
            print(f"   - Button shortcut: {button.shortcut().toString()}")
            
            print(f"\n🔍 Accessibility:")
            print(f"   - Checkbox accessible name: '{checkbox.accessibleName()}'")
            print(f"   - Button accessible name: '{button.accessibleName()}'")
            
        else:
            print("❌ Could not find checkbox or button elements")
        
        print("\n✅ Layout test completed!")
        print("\nExpected improvements:")
        print("- Settings button is now on the right edge")
        print("- Checkbox is on the left side")
        print("- Both elements are larger and more prominent")
        print("- Better spacing and visual hierarchy")
        
        QTimer.singleShot(1500, window.close)
    
    # Check layout after window is fully rendered
    QTimer.singleShot(300, check_layout)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_improved_layout())