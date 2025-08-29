#!/usr/bin/env python3
"""
Validation script for German translations in EnBraille
"""

import sys
import os
# Add the root project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def validate_german_translations():
    """Validate that German translations are working properly"""
    
    print("🇩🇪 EnBraille German Translation Validation")
    print("=" * 50)
    
    # Test 1: Translation loading
    print("Test 1: Loading German translations...")
    try:
        import tools.translation_helper as translation_helper
        if translation_helper.load_translations('de'):
            print("✅ German translations loaded successfully")
        else:
            print("❌ Failed to load German translations")
            return False
    except Exception as e:
        print(f"❌ Error loading translations: {e}")
        return False
    
    # Test 2: Translation functionality
    print("\nTest 2: Translation functionality...")
    test_cases = [
        ("Welcome to EnBraille", "Willkommen zu EnBraille"),
        ("Settings", "Einstellungen"),
        ("Error", "Fehler"),
        ("Text to BRF", "Text zu BRF")
    ]
    
    for english, expected_german in test_cases:
        actual_german = translation_helper.tr(english)
        if actual_german == expected_german:
            print(f"✅ '{english}' → '{actual_german}'")
        else:
            print(f"❌ '{english}' → '{actual_german}' (expected: '{expected_german}')")
            return False
    
    # Test 3: Qt integration
    print("\nTest 3: Qt integration...")
    try:
        from PySide6.QtWidgets import QApplication, QLabel
        
        app = QApplication([])
        
        # Patch Qt system
        if translation_helper.patch_qt_tr():
            print("✅ Qt translation system patched")
        else:
            print("❌ Failed to patch Qt system")
            return False
            
        # Test Qt widget translation
        label = QLabel()
        german_text = label.tr('Welcome to EnBraille')
        if german_text == 'Willkommen zu EnBraille':
            print(f"✅ Qt widget translation: '{german_text}'")
        else:
            print(f"❌ Qt widget translation failed: '{german_text}'")
            return False
            
    except Exception as e:
        print(f"❌ Qt integration error: {e}")
        return False
    
    # Test 4: Application startup
    print("\nTest 4: Application startup...")
    try:
        # Import main application components
        from enbraille_data import EnBrailleData
        from enbraille_gui import EnBrailleWelcomePage
        
        # Create test data
        data = EnBrailleData(app)
        
        # Try creating welcome page (this was failing before)
        welcome_page = EnBrailleWelcomePage(data)
        print("✅ Application components can be created with German translations")
        
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        return False
    
    print("\n🎉 All validation tests passed!")
    print("\n💡 Usage:")
    print("  python enbraille_main.py --language de")
    print("  # or just: python enbraille_main.py (if system locale is German)")
    
    return True

if __name__ == "__main__":
    success = validate_german_translations()
    sys.exit(0 if success else 1)