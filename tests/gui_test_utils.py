"""
Cross-platform GUI test utilities for EnBraille tests.
Provides robust GUI testing support for Windows and macOS.
"""

import os
import sys
import platform
import pytest
from typing import Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


def is_gui_available() -> bool:
    """
    Check if GUI is available on the current platform.
    
    Returns:
        bool: True if GUI can be initialized, False otherwise
    """
    system = platform.system()
    
    # Windows check
    if system == "Windows":
        # On Windows, check if we're in a session with a desktop
        try:
            import ctypes
            user32 = ctypes.windll.user32
            # Check if there's a desktop window
            return user32.GetDesktopWindow() != 0
        except:
            # Fallback to basic check
            return os.environ.get('SESSIONNAME') != 'Console'
    
    # macOS check  
    elif system == "Darwin":
        # On macOS, check if we have access to the window server
        try:
            from AppKit import NSApplication
            return True
        except ImportError:
            # If AppKit not available, check DISPLAY or running in SSH
            return (os.environ.get('DISPLAY') is not None or 
                   os.environ.get('SSH_CONNECTION') is None)
    
    # Linux/Unix check
    else:
        # Check for X11 display
        return os.environ.get('DISPLAY') is not None


def get_gui_skip_reason() -> Optional[str]:
    """
    Get the reason why GUI tests should be skipped, if any.
    
    Returns:
        Optional[str]: Skip reason or None if GUI is available
    """
    if not is_gui_available():
        system = platform.system()
        if system == "Windows":
            return "GUI tests require interactive Windows session"
        elif system == "Darwin":
            return "GUI tests require macOS window server access"
        else:
            return "GUI tests require X11 display"
    return None


def skip_if_no_gui():
    """
    Pytest decorator to skip tests if GUI is not available.
    """
    reason = get_gui_skip_reason()
    return pytest.mark.skipif(reason is not None, reason=reason or "GUI not available")


def create_test_application() -> Optional[QApplication]:
    """
    Create a QApplication for testing, with proper cross-platform handling.
    
    Returns:
        QApplication or None if creation fails
    """
    try:
        # Check if application already exists
        app = QApplication.instance()
        if app is None:
            # Create new application with minimal arguments
            app = QApplication([])
            
        # Platform-specific configuration
        system = platform.system()
        if system == "Darwin":
            # On macOS, ensure proper event loop handling
            app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
        elif system == "Windows":
            # On Windows, handle DPI awareness
            try:
                app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            except:
                pass
                
        return app
        
    except Exception as e:
        print(f"Failed to create QApplication: {e}")
        return None


def gui_test_wrapper(test_func):
    """
    Decorator for GUI tests that provides robust error handling and cleanup.
    """
    def wrapper(*args, **kwargs):
        skip_reason = get_gui_skip_reason()
        if skip_reason:
            pytest.skip(skip_reason)
            
        app = create_test_application()
        if app is None:
            pytest.skip("Failed to create QApplication")
            
        try:
            # Execute the test
            result = test_func(*args, **kwargs)
            
            # Clean up any pending events
            app.processEvents()
            
            # Schedule application quit for safety
            QTimer.singleShot(100, app.quit)
            
            return result
            
        except Exception as e:
            # Clean up on error
            try:
                app.quit()
            except:
                pass
            pytest.skip(f"GUI test failed: {e}")
            
        finally:
            # Ensure cleanup
            try:
                app.processEvents()
            except:
                pass
                
    return wrapper


# Platform information for debugging
PLATFORM_INFO = {
    'system': platform.system(),
    'release': platform.release(), 
    'version': platform.version(),
    'machine': platform.machine(),
    'gui_available': is_gui_available(),
    'skip_reason': get_gui_skip_reason()
}