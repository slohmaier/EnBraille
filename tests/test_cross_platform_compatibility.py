"""
Cross-platform compatibility tests for EnBraille.
Ensures all functionality works properly on both Windows and macOS.
"""

import sys
import os
import platform
import pytest
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.gui_test_utils import (
    PLATFORM_INFO, 
    is_gui_available, 
    get_gui_skip_reason,
    create_test_application,
    skip_if_no_gui,
    gui_test_wrapper
)

class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility requirements"""
    
    def test_platform_detection(self):
        """Test that platform detection works correctly"""
        self.assertIn(platform.system(), ['Windows', 'Darwin', 'Linux'])
        self.assertIsInstance(PLATFORM_INFO['system'], str)
        self.assertIsInstance(PLATFORM_INFO['gui_available'], bool)
        
    def test_windows_compatibility(self):
        """Test Windows-specific compatibility"""
        if platform.system() != 'Windows':
            self.skipTest("Windows-specific test")
            
        # Test Windows-specific features
        self.assertEqual(PLATFORM_INFO['system'], 'Windows')
        self.assertIsNotNone(PLATFORM_INFO['release'])
        
        # Test GUI availability on Windows
        if os.environ.get('SESSIONNAME') != 'Console':
            self.assertTrue(is_gui_available())
            self.assertIsNone(get_gui_skip_reason())
    
    def test_macos_compatibility(self):
        """Test macOS-specific compatibility"""
        if platform.system() != 'Darwin':
            self.skipTest("macOS-specific test")
            
        # Test macOS-specific features  
        self.assertEqual(PLATFORM_INFO['system'], 'Darwin')
        
        # Test GUI availability on macOS
        if os.environ.get('SSH_CONNECTION') is None:
            # Not in SSH session, should have GUI
            self.assertTrue(is_gui_available())

    def test_gui_availability_detection(self):
        """Test GUI availability detection across platforms"""
        result = is_gui_available()
        self.assertIsInstance(result, bool)
        
        skip_reason = get_gui_skip_reason()
        if result:
            self.assertIsNone(skip_reason)
        else:
            self.assertIsInstance(skip_reason, str)
            self.assertGreater(len(skip_reason), 0)

    @skip_if_no_gui()
    @gui_test_wrapper  
    def test_qapplication_creation(self):
        """Test QApplication creation across platforms"""
        app = create_test_application()
        self.assertIsNotNone(app)
        
        # Test platform-specific attributes
        system = platform.system()
        if system == 'Darwin':
            # macOS specific tests
            self.assertTrue(hasattr(app, 'setAttribute'))
        elif system == 'Windows':
            # Windows specific tests  
            self.assertTrue(hasattr(app, 'setAttribute'))


class TestReformatCompatibility(unittest.TestCase):
    """Test reformat functionality across platforms"""
    
    def test_reformat_logic(self):
        """Test that reformat logic works on all platforms"""
        from enbraille_functions.reformat import EnBrailleReformater
        
        # Test the cross-platform reformat fix without GUI
        testfile_dir = os.path.join(os.path.dirname(__file__), 'data')
        reformater = EnBrailleReformater(os.path.join(testfile_dir, 'reformat_simple.brf'))
        
        # Create mock data object
        class MockData:
            def __init__(self):
                self.reformatLineLength = 0
                self.reformatPageLength = 25
                self.reformatWordSplitter = '-'
                self.reformatKeepPageNo = False
                
        data = MockData()
        
        # Should return empty string on all platforms when line length = 0
        result = reformater.reformat(None, data)
        self.assertEqual('', result)


def test_import_compatibility():
    """Test that all imports work across platforms"""
    # Test PySide6 imports
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        from PySide6 import QtTest
        from PySide6.QtGui import QGuiApplication
        assert True, "PySide6 imports successful"
    except ImportError as e:
        pytest.fail(f"PySide6 import failed: {e}")
    
    # Test EnBraille imports
    try:
        from enbraille_data import EnBrailleData
        from enbraille_functions.reformat import EnBrailleReformater
        from enbraille_tools import generateOutput, reformatPragraph
        assert True, "EnBraille imports successful"
    except ImportError as e:
        pytest.fail(f"EnBraille import failed: {e}")


if __name__ == '__main__':
    print(f"Testing cross-platform compatibility on {platform.system()}")
    print(f"Platform info: {PLATFORM_INFO}")
    unittest.main()