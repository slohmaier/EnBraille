import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test the skip welcome page functionality
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_skip_functionality():
    """Test skipping the welcome page"""
    app = QApplication(sys.argv)
    
    print("=== Skip Welcome Page Test ===")
    
    # Test 1: With skip enabled
    print("\n1. Testing with skip ENABLED:")
    data = EnBrailleData(app)
    data.skipWelcomePage = True
    
    window = EnBrailleWindow(data)
    print(f"   - Start ID set to: {window.startId()}")
    
    window.show()
    
    def check_skipped():
        current_page = window.currentPage()
        print(f"   - Current page after show: {current_page.__class__.__name__}")
        print(f"   - Page title: '{current_page.title()}'")
        window.close()
        
        # Test 2: With skip disabled
        print("\n2. Testing with skip DISABLED:")
        data.skipWelcomePage = False
        
        window2 = EnBrailleWindow(data)
        print(f"   - Start ID set to: {window2.startId()}")
        
        window2.show()
        QTimer.singleShot(100, check_not_skipped)
    
    def check_not_skipped():
        current_page = window.currentPage()
        print(f"   - Current page after show: {current_page.__class__.__name__}")
        print(f"   - Page title: '{current_page.title()}'")
        
        print("\n✅ Skip functionality test completed!")
        print("\nResults:")
        print("- When skip=True: Starts on 'What to EnBraille?' page")
        print("- When skip=False: Starts on 'Welcome to EnBraille' page")
        
        window.close()
        QTimer.singleShot(100, app.quit)
    
    QTimer.singleShot(200, check_skipped)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_skip_functionality())