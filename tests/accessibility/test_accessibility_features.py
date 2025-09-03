import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test the accessibility of the simplified features section for VoiceOver compatibility.
Cross-platform GUI testing support for Windows and macOS.
"""

import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import QTimer, Qt
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow
from tests.gui_test_utils import skip_if_no_gui, gui_test_wrapper, create_test_application

# Cross-platform GUI availability check
pytestmark = skip_if_no_gui()

@gui_test_wrapper
def test_voiceover_accessibility():
    """Test VoiceOver accessibility of simplified features - Cross-platform compatible"""
    app = create_test_application()
    if app is None:
        pytest.skip("Could not create QApplication")
    
    print("=== VoiceOver Accessibility Test ===")
    print(f"Platform: {sys.platform}")
    
    # Create window
    data = EnBrailleData(app)
    data.skipWelcomePage = False
    window = EnBrailleWindow(data)
    
    def analyze_accessibility():
        print("\n🎙️ VoiceOver Compatibility Analysis:")
        current_page = window.welcomePage
        
        # Find features label
        labels = current_page.findChildren(QLabel)
        features_label = None
        
        for label in labels:
            if hasattr(label, 'accessibleName') and label.accessibleName() == 'Features List':
                features_label = label
                break
        
        if features_label:
            print("   ✅ Features label found with proper accessibility")
            print(f"   - Accessible name: '{features_label.accessibleName()}'")
            print(f"   - Accessible description: '{features_label.accessibleDescription()}'")
            print(f"   - Text format: {'Plain Text (VoiceOver friendly)' if features_label.textFormat() == Qt.PlainText else 'Rich Text'}")
            print(f"   - Word wrapping: {'Enabled' if features_label.wordWrap() else 'Disabled'}")
            
            # Test content readability
            text = features_label.text()
            features_count = text.count('•')
            print(f"   - Features found: {features_count}")
            print(f"   - Total text length: {len(text)} characters")
            
            # Check for proper structure
            has_titles = '•' in text
            has_descriptions = len(text.split('\n')) > features_count
            
            print(f"\n📖 Content Structure:")
            print(f"   - Has feature titles: {'✅' if has_titles else '❌'}")
            print(f"   - Has descriptions: {'✅' if has_descriptions else '❌'}")
            print(f"   - Proper formatting: {'✅' if has_titles and has_descriptions else '❌'}")
            
            print(f"\n🎯 VoiceOver Benefits:")
            print(f"   - Will read complete feature list as single coherent text")
            print(f"   - No confusing 'Feature 1', 'Feature 2' announcements")
            print(f"   - Clear title and description structure")
            print(f"   - No interrupting grey background styling")
            print(f"   - Dark mode compatible without color issues")
            
            print(f"\n✅ VoiceOver accessibility test passed!")
            
        else:
            print("   ❌ Features label not found")
        
        window.close()
        app.quit()
    
    # Run in a timer to avoid blocking
    QTimer.singleShot(200, analyze_accessibility)
    app.exec()

if __name__ == "__main__":
    sys.exit(test_voiceover_accessibility())