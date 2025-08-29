# EnBraille Project Structure

This document describes the organized structure of the EnBraille project after cleanup and reorganization.

## 📁 Root Directory Structure

```
EnBraille/
├── 📄 LICENSE                    # GPL v3 License
├── 📄 README.md                  # Main project README
├── 📄 PROJECT_STRUCTURE.md       # This file
├── 📄 requirements.txt           # Python dependencies
├── 📄 setup.py                   # Python package setup
├── 📂 docs/                      # 📚 Documentation
├── 📂 tests/                     # 🧪 Test files
├── 📂 tools/                     # 🔧 Utility tools and helpers
├── 📂 scripts/                   # 📜 Shell/batch scripts
├── 📂 resources/                 # 🎨 Assets and resources
├── 📂 translations/              # 🌍 Language translations
├── 📂 deployment/                # 🚀 Deployment configuration
├── 📂 enbraille_functions/       # 📦 Core functionality modules
├── 📄 enbraille_main.py          # 🏁 Main application entry point
├── 📄 enbraille_gui.py           # 🖥️ GUI components
├── 📄 enbraille_data.py          # 💾 Data management
├── 📄 enbraille_widgets.py       # 🔲 Custom UI widgets
├── 📄 enbraille_tools.py         # ⚙️ Core utility functions
└── 📄 libbrl.py                  # 📖 Braille library interface
```

## 📚 Documentation (`docs/`)

Contains all project documentation:
- **README.md** - Documentation index
- **ACCESSIBILITY_FEATURES.md** - Accessibility feature documentation
- **DARK_MODE_FIX.md** - Dark mode implementation details
- **GERMAN_TRANSLATIONS_SUMMARY.md** - German translation guide
- **LAYOUT_IMPROVEMENTS.md** - UI layout improvement documentation
- **TRANSLATIONS.md** - Translation system documentation
- **SCROLLABLE_FEATURES_IMPROVEMENTS.md** - Scrollable features documentation
- **WELCOME_PAGE_FEATURES.md** - Welcome page feature documentation
- **WELCOME_PAGE_FIXED.md** - Welcome page fixes documentation

## 🧪 Test Suite (`tests/`)

Organized test structure:

```
tests/
├── 📄 README.md                  # Test documentation
├── 📄 test_epub_and_markdown.py  # EPUB and Markdown conversion tests
├── 📄 test_reformat.py           # BRF reformatting tests
├── 📄 test_utilenbraille.py      # Utility function tests
├── 📄 tst_reformater.py          # Legacy reformatter tests
├── 📂 accessibility/             # Accessibility feature tests
├── 📂 data/                      # Test data files (EPUB samples, etc.)
├── 📂 navigation/                # Navigation flow tests
├── 📂 translations/              # Translation system tests
├── 📂 ui_components/             # UI component tests
└── 📂 welcome_page/              # Welcome page tests
```

### Test Categories:
- **Accessibility** - VoiceOver, screen reader compatibility
- **Navigation** - Application flow and navigation
- **UI Components** - Individual widget and dialog tests
- **Welcome Page** - Welcome screen functionality
- **Translations** - German translation system tests

## 🔧 Tools & Utilities (`tools/`)

Development and utility tools:
- **run_tests.py** - Test runner utility
- **translation_helper.py** - Translation system implementation
- **util_epub.py** - EPUB processing utilities

## 📜 Scripts (`scripts/`)

Automation and build scripts:
- **addlicheaders.bat** - Add license headers to files
- **deploy_to_appstore.sh** - App Store deployment script
- **runtests.bat** - Windows test runner batch file
- **start.bat** - Windows application launcher

## 🎨 Resources (`resources/`)

Application assets and resources:
- **assets/** - Icons and images
  - Icon.png, Icon.logoist, Title.logoist
- **enbraille_resources.py** - Qt resource file
- **enbraille_resources.qrc** - Qt resource configuration
- **enbraille_resources_rc.py** - Compiled Qt resources
- **gpl-v3.tmpl** - GPL license template

## 🌍 Translations (`translations/`)

Multi-language support:
- **enbraille_de.py** - German translation dictionary
- **enbraille_de.ts** - Qt German translation source

Supported Languages:
- 🇺🇸 English (default)
- 🇩🇪 German (Deutsch) - Complete translation

## 📦 Core Modules (`enbraille_functions/`)

Core application functionality:
- **document.py** - Document conversion (EPUB, Markdown → BRF)
- **reformat.py** - BRF file reformatting
- **text.py** - Text to BRF conversion

## 🚀 Deployment (`deployment/`)

Platform-specific deployment configurations:
- **macos/** - macOS App Store deployment
- **requirements-build.txt** - Build-time dependencies
- **update_version.py** - Version management utility

## 🏁 Main Application Files

- **enbraille_main.py** - Application entry point, handles startup and translations
- **enbraille_gui.py** - Main GUI components and windows
- **enbraille_data.py** - Settings and data management
- **enbraille_widgets.py** - Custom Qt widgets
- **enbraille_tools.py** - Core utility functions
- **libbrl.py** - Braille translation library interface

## 🔄 Import Structure

After reorganization, imports follow this pattern:

```python
# Tools and utilities
from tools.util_epub import epub2md
from tools.translation_helper import load_translations

# Resources
import resources.enbraille_resources as _

# Core modules
from enbraille_functions.document import EnBrailleDocument
from enbraille_functions.reformat import EnBrailleReformat
from enbraille_functions.text import EnBrailleText
```

## 🎯 Benefits of This Organization

1. **Clear separation of concerns** - Each directory has a specific purpose
2. **Easy navigation** - Related files are grouped together
3. **Clean root directory** - Only essential files at the top level
4. **Scalable structure** - Easy to add new components
5. **Professional organization** - Follows Python project best practices
6. **Better maintainability** - Code is easier to find and maintain

## 🔧 Running the Application

After reorganization, the application still runs normally:

```bash
# Standard startup
python enbraille_main.py

# With German translation
python enbraille_main.py --language de

# Run tests
python tools/run_tests.py

# Or from scripts directory
scripts/start.bat          # Windows
scripts/runtests.bat       # Windows tests
```

## 📋 Migration Notes

The reorganization maintains backward compatibility:
- All import paths have been updated
- Core functionality remains unchanged  
- Test suite continues to work
- Translation system is preserved
- Build scripts are functional

This structure provides a solid foundation for future development and makes the project more professional and maintainable.