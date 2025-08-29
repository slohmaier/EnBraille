#!/usr/bin/env python3
"""
Translation helper for EnBraille
Simple Python-based translation system that doesn't require Qt tools
"""

import os
import sys
from typing import Optional

# Global translation dictionary
_current_translations = {}

def load_translations(language_code: str = 'en') -> bool:
    """Load translations for the specified language."""
    global _current_translations
    
    if language_code == 'en':
        _current_translations = {}
        return True
    
    try:
        # Try to import the translation module
        translations_dir = os.path.join(os.path.dirname(__file__), '..', 'translations')
        sys.path.insert(0, translations_dir)
        
        translation_module_name = f'enbraille_{language_code}'
        translation_module = __import__(translation_module_name)
        
        if hasattr(translation_module, 'TRANSLATIONS'):
            _current_translations = translation_module.TRANSLATIONS
            return True
        else:
            _current_translations = {}
            return False
            
    except ImportError:
        _current_translations = {}
        return False

def tr(text: str) -> str:
    """Translate text using current language."""
    global _current_translations
    return _current_translations.get(text, text)

def get_system_language() -> str:
    """Get system language code."""
    import locale
    try:
        # Get system locale
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            # Extract language code (first 2 characters)
            return system_locale[:2].lower()
    except:
        pass
    
    return 'en'  # Default to English

# Monkey patch for QObject.tr() method
def patch_qt_tr():
    """Patch Qt's tr() method to use our translation system."""
    try:
        from PySide6.QtCore import QObject
        
        # Store original tr method from QObject
        original_tr = QObject.tr
        
        def patched_tr(sourceText, disambiguation=None, n=-1):
            """Patched tr method that uses our translation system."""
            # First try our translation system
            translated = tr(sourceText)
            if translated != sourceText:
                return translated
            
            # Fall back to original Qt translation
            return original_tr(sourceText, disambiguation, n)
        
        # Replace the tr method on QObject
        QObject.tr = staticmethod(patched_tr)
        return True
        
    except ImportError:
        # PySide6 not available
        return False