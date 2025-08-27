import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Visual test of the welcome page to see the actual button behavior
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_welcome_visual():
    """Visually test the welcome page buttons"""
    app = QApplication(sys.argv)
    
    # Create data and ensure welcome page is shown
    data = EnBrailleData(app)
    data.skipWelcomePage = False
    
    print("Creating window with welcome page enabled...")
    window = EnBrailleWindow(data)
    
    print("Showing window...")
    window.show()
    
    def check_buttons():
        current_page = window.currentPage()
        print(f"Current page: {current_page.__class__.__name__}")
        print(f"Page title: {current_page.title()}")
        print(f"Page is complete: {current_page.isComplete()}")
        
        if hasattr(current_page, 'nextId'):
            print(f"Next ID: {current_page.nextId()}")
        if hasattr(current_page, 'isFinalPage'):
            print(f"Is final page: {current_page.isFinalPage()}")
        
        # Check button states
        from PySide6.QtWidgets import QWizard
        back_btn = window.button(QWizard.BackButton)
        next_btn = window.button(QWizard.NextButton)
        finish_btn = window.button(QWizard.FinishButton)
        
        print(f"Back button - enabled: {back_btn.isEnabled()}, visible: {back_btn.isVisible()}")
        print(f"Next button - enabled: {next_btn.isEnabled()}, visible: {next_btn.isVisible()}")
        print(f"Finish button - enabled: {finish_btn.isEnabled()}, visible: {finish_btn.isVisible()}")
        
        # Close after 2 seconds
        QTimer.singleShot(2000, window.close)
    
    # Check buttons after window is fully loaded
    QTimer.singleShot(100, check_buttons)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_welcome_visual())