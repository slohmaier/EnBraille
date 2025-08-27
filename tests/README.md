# EnBraille Tests

This directory contains all test files organized by functionality.

## Test Structure

### 📋 Welcome Page Tests (`welcome_page/`)
- `test_welcome_page.py` - Basic welcome page functionality
- `test_welcome_visual.py` - Visual layout testing  
- `test_improved_layout.py` - Layout improvements verification
- `test_scrollable_features.py` - Scrollable features section tests
- `test_dark_mode_compatibility.py` - Dark mode theme compatibility

### ♿ Accessibility Tests (`accessibility/`)
- `test_focus_management.py` - Screen reader focus management
- `test_accessibility_features.py` - VoiceOver compatibility tests

### 🎨 UI Components Tests (`ui_components/`)
- `test_about_dialog.py` - About dialog functionality

### 🧭 Navigation Tests (`navigation/`)
- `test_navigation_flow.py` - Basic navigation between pages
- `test_complete_flow.py` - End-to-end navigation testing
- `test_skip_functionality.py` - Skip welcome page feature

### 🧪 Core Function Tests (root level)
- `test_epub_and_markdown.py` - Document processing tests
- `test_reformat.py` - BRF reformatting tests
- `test_utilenbraille.py` - Utility function tests

## Running Tests

To run all tests:
```bash
python -m pytest tests/
```

To run tests by category:
```bash
# Welcome page tests only
python -m pytest tests/welcome_page/

# Accessibility tests only  
python -m pytest tests/accessibility/

# UI component tests only
python -m pytest tests/ui_components/

# Navigation tests only
python -m pytest tests/navigation/
```

To run a specific test:
```bash
python tests/welcome_page/test_welcome_page.py
```

## Test Requirements

Tests require:
- PySide6
- EnBraille application modules
- Qt environment (for GUI tests)

Note: GUI tests may require a display/window manager to run properly.