# Cross-Platform Compatibility Requirements

This document outlines the cross-platform compatibility requirements and implementations for EnBraille tests, ensuring reliable operation on both Windows and macOS.

## Basic Requirements

### 1. **Cross-Platform Test Support**
- All tests must work reliably on both Windows and macOS
- GUI tests must gracefully handle headless environments
- Platform-specific behaviors must be properly detected and handled

### 2. **GUI Test Framework** 
- Robust GUI availability detection for different platforms
- Automatic test skipping when GUI is not available
- Safe QApplication creation and cleanup
- Cross-platform event loop handling

### 3. **Platform Detection**
- **Windows**: Session type detection (Console vs Interactive)
- **macOS**: Window server access via AppKit or DISPLAY environment  
- **Linux**: X11 DISPLAY environment variable check

## Implementation

### GUI Test Utilities (`tests/gui_test_utils.py`)

#### Core Functions:
- `is_gui_available()`: Detects if GUI can be initialized on current platform
- `get_gui_skip_reason()`: Returns platform-specific skip reason if GUI unavailable
- `create_test_application()`: Creates QApplication with platform-specific configuration
- `skip_if_no_gui()`: Pytest decorator for conditional test skipping
- `gui_test_wrapper()`: Decorator providing robust GUI test error handling

#### Platform-Specific Logic:

**Windows:**
```python
# Check desktop window availability
user32 = ctypes.windll.user32
return user32.GetDesktopWindow() != 0
```

**macOS:**  
```python
# Check AppKit availability or SSH status
from AppKit import NSApplication
return os.environ.get('SSH_CONNECTION') is None
```

**Linux/Unix:**
```python
# Check X11 display
return os.environ.get('DISPLAY') is not None
```

### Updated Test Files

#### 1. Accessibility Tests
- `test_accessibility_features.py`: VoiceOver compatibility testing
- `test_focus_management.py`: Screen reader focus management

#### 2. Text Functions
- `test_text_conversion.py`: Text-to-braille conversion testing  

#### 3. Cross-Platform Validation
- `test_cross_platform_compatibility.py`: Comprehensive platform compatibility tests

## Usage Examples

### Basic GUI Test:
```python
from tests.gui_test_utils import skip_if_no_gui, gui_test_wrapper, create_test_application

@skip_if_no_gui()
@gui_test_wrapper
def test_my_gui_feature():
    app = create_test_application()
    if app is None:
        pytest.skip("Could not create QApplication")
    
    # Your GUI test code here
    # Platform info available via sys.platform
```

### Platform-Specific Tests:
```python
import platform

def test_windows_specific():
    if platform.system() != 'Windows':
        pytest.skip("Windows-specific test")
    # Windows-only test logic

def test_macos_specific():
    if platform.system() != 'Darwin':
        pytest.skip("macOS-specific test")
    # macOS-only test logic
```

## Test Results Status

### ✅ **Working Cross-Platform:**
- Core Libraries: 18/18 tests ✅
- Utilities: 25/25 tests ✅  
- Business Logic: 19/19 tests ✅
- Reformat Logic: 1/1 tests ✅
- Cross-Platform Validation: 6/7 tests ✅ (1 skipped on Windows as expected)

### ✅ **GUI Tests (Individual Execution):**
- Accessibility Features: ✅ (with proper platform detection)
- Focus Management: ✅ (with error handling)
- Text Conversion: ✅ (with cross-platform support)

### ⚠️ **Known Limitations:**
- GUI tests may conflict when run simultaneously due to QApplication state
- Some data model tests have QSettings mocking issues in test environment
- macOS tests require window server access (not available in SSH sessions)

## Validation Commands

### Core Functionality:
```bash
python -m pytest tests/core_libraries tests/utilities tests/business_logic tests/test_reformat.py tests/test_cross_platform_compatibility.py
```

### Individual GUI Tests:
```bash
python -m pytest tests/accessibility/test_accessibility_features.py -v
python -m pytest tests/accessibility/test_focus_management.py -v  
python -m pytest tests/text_functions/test_text_conversion.py -v
```

### Platform Detection:
```bash
python -c "from tests.gui_test_utils import PLATFORM_INFO; import json; print(json.dumps(PLATFORM_INFO, indent=2))"
```

## Best Practices

1. **Always use cross-platform utilities** from `gui_test_utils.py`
2. **Include platform detection** in GUI tests with proper skip conditions  
3. **Test both platforms** when making GUI-related changes
4. **Provide meaningful skip reasons** for platform-specific limitations
5. **Use proper error handling** with the `@gui_test_wrapper` decorator
6. **Avoid hardcoded platform assumptions** in test logic

This framework ensures EnBraille tests work reliably across Windows and macOS while providing clear feedback about platform-specific limitations.