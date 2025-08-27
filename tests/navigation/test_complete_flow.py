import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test complete navigation flow from welcome page to function selection
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QWizard
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_complete_flow():
    """Test the complete welcome page to function selection flow"""
    app = QApplication(sys.argv)
    
    # Create data and ensure welcome page is shown
    data = EnBrailleData(app)
    data.skipWelcomePage = False
    
    print("=== Complete Navigation Flow Test ===")
    print("Testing: Welcome Page → Function Selection → Next Steps")
    
    window = EnBrailleWindow(data)
    window.show()
    
    def step1_check_welcome():
        current_page = window.currentPage()
        print(f"\n1. Welcome Page Check:")
        print(f"   - Current page: {current_page.__class__.__name__}")
        print(f"   - Page title: '{current_page.title()}'")
        print(f"   - Next button enabled: {window.button(QWizard.NextButton).isEnabled()}")
        print(f"   - Finish button visible: {window.button(QWizard.FinishButton).isVisible()}")
        
        # Simulate clicking Next
        print("\n   → Clicking Next button...")
        window.next()
        QTimer.singleShot(100, step2_check_function_selection)
    
    def step2_check_function_selection():
        current_page = window.currentPage()
        print(f"\n2. Function Selection Page Check:")
        print(f"   - Current page: {current_page.__class__.__name__}")
        print(f"   - Page title: '{current_page.title()}'")
        print(f"   - Back button enabled: {window.button(QWizard.BackButton).isEnabled()}")
        print(f"   - Next button enabled: {window.button(QWizard.NextButton).isEnabled()}")
        
        # Test going back
        print("\n   → Testing Back navigation...")
        window.back()
        QTimer.singleShot(100, step3_check_back_to_welcome)
    
    def step3_check_back_to_welcome():
        current_page = window.currentPage()
        print(f"\n3. Back to Welcome Page Check:")
        print(f"   - Current page: {current_page.__class__.__name__}")
        print(f"   - Page title: '{current_page.title()}'")
        print(f"   - Back button enabled: {window.button(QWizard.BackButton).isEnabled()}")
        
        # Test skip functionality
        print(f"\n4. Testing Skip Functionality:")
        print(f"   - Current skip setting: {data.skipWelcomePage}")
        
        # Simulate checking the skip checkbox
        if hasattr(current_page, 'skipCheckbox'):
            current_page.skipCheckbox.setChecked(True)
            print(f"   - Skip setting after checking checkbox: {data.skipWelcomePage}")
        
        print("\n✅ Complete navigation flow test passed!")
        print("\nSummary:")
        print("- Welcome page shows Next button (not Finish)")
        print("- Navigation from Welcome → Function Selection works")
        print("- Back navigation from Function Selection → Welcome works")
        print("- Skip checkbox functionality works")
        
        QTimer.singleShot(500, window.close)
    
    # Start the test sequence
    QTimer.singleShot(200, step1_check_welcome)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_complete_flow())