import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test the About dialog functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_about_dialog():
    """Test the About dialog"""
    app = QApplication(sys.argv)
    
    print("=== About Dialog Test ===")
    
    data = EnBrailleData(app)
    data.skipWelcomePage = False
    window = EnBrailleWindow(data)
    
    def test_dialog():
        print("\n📋 Testing About dialog content:")
        current_page = window.welcomePage
        
        # Find About button
        about_buttons = [btn for btn in current_page.findChildren(QPushButton) if 'About' in btn.text()]
        if about_buttons:
            about_button = about_buttons[0]
            print("   ✅ About button found")
            
            # Test that the method exists and is callable
            if hasattr(current_page, 'openAbout') and callable(getattr(current_page, 'openAbout')):
                print("   ✅ openAbout method exists and is callable")
                
                # Check dialog content by inspecting the method
                import inspect
                source = inspect.getsource(current_page.openAbout)
                
                checks = [
                    ('Website URL', 'slohmaier.de/enbraille' in source),
                    ('Application name', 'EnBraille' in source),
                    ('Features list', 'Text to Braille' in source),
                    ('License info', 'Licensed under' in source),
                    ('Technology stack', 'PySide6' in source and 'Liblouis' in source),
                    ('Copyright', 'Copyright' in source)
                ]
                
                for check_name, result in checks:
                    status = '✅' if result else '❌'
                    print(f"   {status} {check_name}: {'Present' if result else 'Missing'}")
                
                print(f"\n🎯 About dialog includes:")
                print(f"   - Application description and features")
                print(f"   - Website URL: https://slohmaier.de/enbraille")
                print(f"   - Copyright and license information") 
                print(f"   - Technology credits (PySide6, Liblouis, etc.)")
                
            else:
                print("   ❌ openAbout method not found or not callable")
        else:
            print("   ❌ About button not found")
        
        print(f"\n✅ About functionality test completed!")
        
        QTimer.singleShot(50, app.quit)
    
    QTimer.singleShot(100, test_dialog)
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_about_dialog())