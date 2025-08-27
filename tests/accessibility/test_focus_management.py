import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test script to verify screen reader focus management functionality
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QWizard
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_focus_management():
    """Test that focus is properly managed when navigating between pages"""
    app = QApplication(sys.argv)
    
    # Enable logging to see focus changes
    logging.basicConfig(level=logging.DEBUG)
    
    # Create data and window
    data = EnBrailleData(app)
    window = EnBrailleWindow(data)
    
    print("Testing focus management...")
    print("1. Starting wizard - should focus first radio button")
    
    # Show the window
    window.show()
    
    def test_navigation():
        """Test navigation after window is shown"""
        current_page = window.currentPage()
        focused_widget = app.focusWidget()
        
        print(f"Current page: {current_page.__class__.__name__}")
        print(f"Focused widget: {focused_widget.__class__.__name__ if focused_widget else 'None'}")
        
        # Test going to next page if possible
        if window.button(QWizard.NextButton).isEnabled():
            print("2. Clicking Next - should focus first element on next page")
            window.next()
            
            QTimer.singleShot(100, lambda: check_focus_after_navigation())
        else:
            print("Next button not enabled, need to make a selection first")
            # Try to click first radio button
            start_page = window.startPage
            if start_page.buttonGroup.buttons():
                first_button = start_page.buttonGroup.buttons()[0]
                first_button.setChecked(True)
                print("3. Selected first option, now testing next page")
                QTimer.singleShot(200, lambda: window.next())
                QTimer.singleShot(300, lambda: check_focus_after_navigation())
    
    def check_focus_after_navigation():
        """Check focus after navigating to next page"""
        current_page = window.currentPage()
        focused_widget = app.focusWidget()
        
        print(f"After navigation - Current page: {current_page.__class__.__name__}")
        print(f"After navigation - Focused widget: {focused_widget.__class__.__name__ if focused_widget else 'None'}")
        
        if focused_widget:
            print(f"Widget accessible name: {focused_widget.accessibleName()}")
            print(f"Widget object name: {focused_widget.objectName()}")
            print("✓ Focus management working - screen reader should announce the focused element")
        else:
            print("✗ No focused widget - this may cause screen reader issues")
        
        # Test going back
        if window.button(QWizard.BackButton).isEnabled():
            print("4. Testing back navigation")
            QTimer.singleShot(500, lambda: window.back())
            QTimer.singleShot(600, lambda: check_back_navigation())
        else:
            QTimer.singleShot(1000, lambda: app.quit())
    
    def check_back_navigation():
        """Check focus after going back"""
        current_page = window.currentPage()
        focused_widget = app.focusWidget()
        
        print(f"After back navigation - Current page: {current_page.__class__.__name__}")
        print(f"After back navigation - Focused widget: {focused_widget.__class__.__name__ if focused_widget else 'None'}")
        
        print("✓ Focus management test completed")
        QTimer.singleShot(500, lambda: app.quit())
    
    # Start testing after window is fully loaded
    QTimer.singleShot(200, test_navigation)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_focus_management())