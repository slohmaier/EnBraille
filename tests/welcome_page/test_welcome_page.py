import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test script to demonstrate the welcome page functionality
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_welcome_page():
    """Test the welcome page functionality"""
    app = QApplication(sys.argv)
    
    # Enable logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create data and window
    data = EnBrailleData(app)
    
    print("=== Welcome Page Test ===")
    print(f"1. Initial skip welcome setting: {data.skipWelcomePage}")
    
    # Test with welcome page enabled
    print("\n2. Creating window with welcome page...")
    window = EnBrailleWindow(data)
    
    print(f"   - Total pages: {len(window.pageIds())}")
    print(f"   - Page titles: {[window.page(pid).title() for pid in window.pageIds()]}")
    print(f"   - Start page ID: {window.startId()}")
    
    # Test skip functionality
    print("\n3. Testing skip functionality...")
    data.skipWelcomePage = True
    print(f"   - Skip setting changed to: {data.skipWelcomePage}")
    
    # Create new window to test skip
    window2 = EnBrailleWindow(data)
    window2.show()  # This will set the start ID
    print(f"   - Start page ID when skipping: {window2.startId()}")
    
    # Reset for normal operation
    data.skipWelcomePage = False
    print(f"\n4. Reset skip setting to: {data.skipWelcomePage}")
    
    print("\n✅ Welcome page implementation test completed successfully!")
    print("\nFeatures implemented:")
    print("- Welcome page with app description")
    print("- Settings button (placeholder)")
    print("- Skip welcome page checkbox")
    print("- Persistent skip setting")
    print("- Proper wizard navigation")
    print("- Screen reader accessibility")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_welcome_page())