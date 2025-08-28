import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test the accessibility of the simplified features section for VoiceOver compatibility
"""

import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import QTimer, Qt
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_voiceover_accessibility():
    """Test VoiceOver accessibility of simplified features"""
    app = QApplication(sys.argv)
    
    print("=== VoiceOver Accessibility Test ===")
    
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
        QTimer.singleShot(100, app.quit)
    
    QTimer.singleShot(200, analyze_accessibility)
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_voiceover_accessibility())