#!/usr/bin/env python3
"""
Demo script showing EnBraille with German translations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import translation_helper
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout, QLabel, QPushButton

def demo_german_translations():
    """Demonstrate the German translation system"""
    
    print("🇩🇪 EnBraille German Translation Demo")
    print("=" * 50)
    
    # Load German translations
    if translation_helper.load_translations('de'):
        print("✅ German translations loaded successfully")
    else:
        print("❌ Failed to load German translations")
        return
    
    # Patch Qt system
    if translation_helper.patch_qt_tr():
        print("✅ Qt translation system patched")
    else:
        print("❌ Failed to patch Qt system")
        return
    
    app = QApplication([])
    
    # Create demo window with German text
    window = QWidget()
    window.setWindowTitle("EnBraille - Deutsch")
    window.resize(400, 300)
    
    layout = QVBoxLayout(window)
    
    # Add translated labels
    title = QLabel()
    title.setText(title.tr("Welcome to EnBraille"))
    title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title)
    
    subtitle = QLabel()
    subtitle.setText(subtitle.tr("Your comprehensive braille conversion toolkit"))
    subtitle.setStyleSheet("font-size: 12px; color: gray; margin: 5px;")
    layout.addWidget(subtitle)
    
    # Add function buttons
    text_btn = QPushButton()
    text_btn.setText(text_btn.tr("Text to BRF"))
    layout.addWidget(text_btn)
    
    document_btn = QPushButton()
    document_btn.setText(document_btn.tr("Convert Document to BRF"))
    layout.addWidget(document_btn)
    
    reformat_btn = QPushButton()
    reformat_btn.setText(reformat_btn.tr("Reformat BRF"))
    layout.addWidget(reformat_btn)
    
    settings_btn = QPushButton()
    settings_btn.setText(settings_btn.tr("Settings"))
    layout.addWidget(settings_btn)
    
    # Add event handlers for demo
    def show_about():
        about_text = QLabel().tr("About EnBraille")
        QMessageBox.information(window, about_text, 
                              QLabel().tr("EnBraille - Braille Conversion Tool\\n\\nA comprehensive tool for converting text and documents to braille format."))
    
    def show_settings():
        QMessageBox.information(window, 
                              QLabel().tr("Settings"),
                              QLabel().tr("Settings dialog will be implemented here."))
    
    settings_btn.clicked.connect(show_settings)
    
    # Show demo translations in console
    print("\\n📝 Sample translations:")
    sample_texts = [
        "Welcome to EnBraille",
        "Text to BRF", 
        "Settings",
        "About",
        "Error",
        "Choose file",
        "Save file",
        "Done.",
        "Please wait while your text is converted to BRF:",
        "Braille table:"
    ]
    
    for text in sample_texts:
        german = translation_helper.tr(text)
        print(f"  '{text}' → '{german}'")
    
    print("\\n🚀 Demo window opened!")
    print("💡 The window shows German translations in action.")
    print("🔧 To use German in the main app, run:")
    print("   python enbraille_main.py --language de")
    
    window.show()
    
    # Don't actually run the event loop in demo
    app.processEvents()
    print("\\n✅ German translation demo completed!")

if __name__ == "__main__":
    demo_german_translations()