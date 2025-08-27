import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test script to verify the welcome page navigation flow
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QWizard
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_navigation_flow():
    """Test the welcome page navigation"""
    app = QApplication(sys.argv)
    
    # Enable logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create data and reset skip setting
    data = EnBrailleData(app)
    data.skipWelcomePage = False
    
    print("=== Navigation Flow Test ===")
    
    # Test 1: Normal flow with welcome page
    print("\n1. Testing normal flow (with welcome page)...")
    window = EnBrailleWindow(data)
    
    print(f"   - Start ID: {window.startId()}")
    print(f"   - Current page after creation: {window.currentId()}")
    
    # Simulate showing the window
    if hasattr(window, 'welcomePage'):
        welcome_page = window.welcomePage
        print(f"   - Welcome page is complete: {welcome_page.isComplete()}")
        print(f"   - Welcome page is final: {welcome_page.isFinalPage()}")
        print(f"   - Welcome page next ID: {welcome_page.nextId()}")
    
    print("   - Available wizard buttons:")
    buttons = [
        ("Back", window.button(QWizard.BackButton)),
        ("Next", window.button(QWizard.NextButton)),
        ("Finish", window.button(QWizard.FinishButton)),
        ("Cancel", window.button(QWizard.CancelButton))
    ]
    
    for name, button in buttons:
        if button:
            enabled = button.isEnabled()
            visible = button.isVisible()
            print(f"     {name}: enabled={enabled}, visible={visible}")
    
    # Test 2: Skip functionality
    print("\n2. Testing skip functionality...")
    data.skipWelcomePage = True
    window2 = EnBrailleWindow(data)
    
    print(f"   - Skip setting: {data.skipWelcomePage}")
    print(f"   - Start ID when skipping: {window2.startId()}")
    
    # Simulate showing the window to trigger show() method
    print("   - Simulating window show...")
    window2.show()
    print(f"   - Start ID after show: {window2.startId()}")
    print(f"   - Current ID after show: {window2.currentId()}")
    
    # Test 3: Page titles and order
    print("\n3. Page structure:")
    for i, page_id in enumerate(window.pageIds()):
        page = window.page(page_id)
        title = page.title()
        is_complete = page.isComplete()
        print(f"   {i}: ID={page_id}, Title='{title}', Complete={is_complete}")
    
    print("\n✅ Navigation flow test completed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_navigation_flow())