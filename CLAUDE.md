# Claude Code Configuration for EnBraille

This document contains configuration and documentation for Claude Code development assistance on the EnBraille project.

## Project Overview

EnBraille is a cross-platform Braille text processing application built with Python and PySide6. It provides text-to-Braille conversion, document reformatting, and accessibility features for Windows and macOS.

## Development Documentation

### Cross-Platform Compatibility
The project enforces strict cross-platform compatibility between Windows and macOS. All tests and functionality must work reliably on both platforms.

📚 **[Cross-Platform Compatibility Guide](docs/CROSS_PLATFORM_COMPATIBILITY.md)**

Key requirements:
- All GUI tests use cross-platform detection and graceful fallbacks
- Platform-specific behaviors are properly handled
- Tests automatically skip when GUI is unavailable (headless environments)
- QApplication creation is robust across platforms

### Test Framework
The project uses a custom cross-platform GUI test framework located in `tests/gui_test_utils.py`:

```python
from tests.gui_test_utils import skip_if_no_gui, gui_test_wrapper, create_test_application

@skip_if_no_gui()
@gui_test_wrapper
def test_gui_feature():
    app = create_test_application()
    # Your GUI test code here
```

### Core Testing Categories
- **Core Libraries** (`tests/core_libraries/`): Braille translation and core functionality
- **Utilities** (`tests/utilities/`): Text processing and formatting utilities  
- **Business Logic** (`tests/business_logic/`): Document processing and reformatting
- **Accessibility** (`tests/accessibility/`): Screen reader and accessibility features
- **Cross-Platform** (`tests/test_cross_platform_compatibility.py`): Platform compatibility validation

## Development Commands

### Running Tests
```bash
# Core functionality (cross-platform safe)
python -m pytest tests/core_libraries tests/utilities tests/business_logic

# Individual GUI tests (Windows/macOS)
python -m pytest tests/accessibility/test_accessibility_features.py -v

# Cross-platform validation
python -m pytest tests/test_cross_platform_compatibility.py -v

# Platform detection test
python -c "from tests.gui_test_utils import PLATFORM_INFO; import json; print(json.dumps(PLATFORM_INFO, indent=2))"
```

### Building and Deployment
```bash
# Build executable
python -m PyInstaller EnBraille.spec

# Run application
python enbraille_main.py
```

## Code Guidelines

1. **Cross-Platform First**: All new features must work on both Windows and macOS
2. **GUI Test Safety**: Use `@gui_test_wrapper` and `@skip_if_no_gui()` decorators
3. **Platform Detection**: Use `tests.gui_test_utils` for platform-specific logic
4. **Error Handling**: GUI tests must gracefully handle crashes and missing dependencies
5. **Documentation**: Update relevant docs when adding platform-specific features

## Key Files and Directories

```
EnBraille/
├── docs/                           # Project documentation
│   ├── CROSS_PLATFORM_COMPATIBILITY.md  # Cross-platform requirements & implementation
│   └── *.md                       # Feature-specific documentation
├── tests/
│   ├── gui_test_utils.py          # Cross-platform GUI test framework
│   ├── accessibility/             # Accessibility and screen reader tests
│   ├── core_libraries/            # Core Braille functionality tests
│   └── test_cross_platform_compatibility.py  # Platform validation
├── enbraille_functions/           # Core application logic
├── enbraille_gui.py              # Main GUI implementation
├── enbraille_data.py             # Data model and settings
└── enbraille_main.py             # Application entry point
```

## Recent Improvements

### Cross-Platform Test Framework (September 2025)
- Implemented robust GUI availability detection for Windows and macOS
- Added automatic test skipping for headless environments
- Created `@gui_test_wrapper` decorator for safe GUI testing
- Fixed segmentation faults in GUI tests on Windows
- Added comprehensive platform compatibility validation

### Test Fixes
- ✅ Fixed PySide6.QtTest import issues across platforms
- ✅ Resolved reformat test expected output mismatches
- ✅ Added proper QApplication state management
- ✅ Implemented graceful GUI test fallbacks

## Contact & Contribution

When working on EnBraille:
1. Always test on both Windows and macOS (or ensure cross-platform compatibility)
2. Use the provided GUI test utilities for any GUI-related tests
3. Update documentation when adding new features
4. Run cross-platform validation tests before submitting changes

For questions about cross-platform compatibility, refer to the [Cross-Platform Compatibility Guide](docs/CROSS_PLATFORM_COMPATIBILITY.md).