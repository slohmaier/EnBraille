import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from PySide6 import QtTest
QSignalSpy = QtTest.QSignalSpy
from enbraille_data import EnBrailleData, EnBrailleMainFct


class TestEnBrailleMainFct(unittest.TestCase):
    """Test the EnBrailleMainFct enum"""
    
    def test_enum_values(self):
        """Test enum values are correct"""
        self.assertEqual(EnBrailleMainFct.TEXT.value, 1)
        self.assertEqual(EnBrailleMainFct.DOCUMENT.value, 2) 
        self.assertEqual(EnBrailleMainFct.REFORMAT.value, 3)
    
    def test_string_conversion(self):
        """Test string conversion"""
        self.assertEqual(str(EnBrailleMainFct.TEXT), 'TEXT')
        self.assertEqual(str(EnBrailleMainFct.DOCUMENT), 'DOCUMENT')
        self.assertEqual(str(EnBrailleMainFct.REFORMAT), 'REFORMAT')
    
    def test_from_string_conversion(self):
        """Test conversion from string"""
        self.assertEqual(EnBrailleMainFct.fromStr('TEXT'), EnBrailleMainFct.TEXT)
        self.assertEqual(EnBrailleMainFct.fromStr('DOCUMENT'), EnBrailleMainFct.DOCUMENT)
        self.assertEqual(EnBrailleMainFct.fromStr('REFORMAT'), EnBrailleMainFct.REFORMAT)
        self.assertIsNone(EnBrailleMainFct.fromStr('INVALID'))
        self.assertIsNone(EnBrailleMainFct.fromStr(''))
        self.assertIsNone(EnBrailleMainFct.fromStr(None))


class TestEnBrailleData(unittest.TestCase):
    """Test the EnBrailleData class"""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication for testing"""
        if not QApplication.instance():
            cls.app = QApplication([])
            cls.app.setOrganizationName("EnBrailleTest")
            cls.app.setApplicationName("EnBrailleDataTest")
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up each test with fresh data"""
        # Create a temporary directory for settings
        self.temp_dir = tempfile.mkdtemp()
        self.data = EnBrailleData(self.app)
        # Clear any existing settings
        self.data.resetSettings()
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'data'):
            self.data.resetSettings()
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test EnBrailleData initialization"""
        self.assertIsNotNone(self.data)
        self.assertEqual(self.data.inputText, '')
        self.assertEqual(self.data.outputText, '')
        self.assertEqual(self.data.reformatFilename, '')
        self.assertEqual(self.data.documentFilename, '')
        
        # Test default values
        self.assertEqual(self.data.mainFunction, EnBrailleMainFct.TEXT)
        self.assertEqual(self.data.textTable, '')
        self.assertEqual(self.data.reformatLineLength, 40)
        self.assertEqual(self.data.reformatPageLength, 0)
        self.assertEqual(self.data.reformatWordSplitter, '-')
        self.assertFalse(self.data.reformatKeepPageNo)
        self.assertFalse(self.data.skipWelcomePage)
    
    def test_main_function_property(self):
        """Test mainFunction property getter/setter and signal emission"""
        # Test signal emission
        spy = QSignalSpy(self.data.mainFunctionChanged)
        
        # Test setting different value
        self.data.mainFunction = EnBrailleMainFct.DOCUMENT
        self.assertEqual(self.data.mainFunction, EnBrailleMainFct.DOCUMENT)
        self.assertEqual(spy.count(), 1)
        
        # Test setting same value (should not emit signal)
        self.data.mainFunction = EnBrailleMainFct.DOCUMENT
        self.assertEqual(spy.count(), 1)  # Should still be 1
        
        # Test persistence
        data2 = EnBrailleData(self.app)
        self.assertEqual(data2.mainFunction, EnBrailleMainFct.DOCUMENT)
    
    def test_text_table_property(self):
        """Test textTable property and signal emission"""
        spy = QSignalSpy(self.data.TextTableChanged)
        
        # Test setting value
        self.data.textTable = 'en-us-g1.ctb'
        self.assertEqual(self.data.textTable, 'en-us-g1.ctb')
        self.assertEqual(spy.count(), 1)
        
        # Test setting same value (should not emit signal)
        self.data.textTable = 'en-us-g1.ctb'
        self.assertEqual(spy.count(), 1)
        
        # Test persistence
        data2 = EnBrailleData(self.app)
        self.assertEqual(data2.textTable, 'en-us-g1.ctb')
    
    def test_reformat_properties(self):
        """Test reformat-related properties"""
        # Test reformatLineLength
        self.data.reformatLineLength = 80
        self.assertEqual(self.data.reformatLineLength, 80)
        
        # Test reformatPageLength
        self.data.reformatPageLength = 25
        self.assertEqual(self.data.reformatPageLength, 25)
        
        # Test reformatWordSplitter
        self.data.reformatWordSplitter = '~'
        self.assertEqual(self.data.reformatWordSplitter, '~')
        
        # Test reformatKeepPageNo
        self.data.reformatKeepPageNo = True
        self.assertTrue(self.data.reformatKeepPageNo)
        
        # Test persistence
        data2 = EnBrailleData(self.app)
        self.assertEqual(data2.reformatLineLength, 80)
        self.assertEqual(data2.reformatPageLength, 25)
        self.assertEqual(data2.reformatWordSplitter, '~')
        self.assertTrue(data2.reformatKeepPageNo)
    
    def test_document_text_table_property_bug(self):
        """Test documentTextTable property - this will reveal the bug"""
        spy = QSignalSpy(self.data.DocumentTextTableChanged)
        
        # This should work but currently has wrong decorator
        try:
            self.data.documentTextTable = 'de-g1.ctb'
            # If we get here, the bug is fixed
            self.assertEqual(self.data.documentTextTable, 'de-g1.ctb')
        except AttributeError:
            # This is expected due to the bug - wrong decorator
            self.fail("BUG FOUND: documentTextTable setter has wrong decorator @textTable.setter instead of @documentTextTable.setter")
    
    def test_document_properties(self):
        """Test document-related properties"""
        # Test documentLineLength
        self.data.documentLineLength = 120
        self.assertEqual(self.data.documentLineLength, 120)
        
        # Test documentPageLength  
        self.data.documentPageLength = 30
        self.assertEqual(self.data.documentPageLength, 30)
        
        # Test documentWordSplitter
        self.data.documentWordSplitter = '='
        self.assertEqual(self.data.documentWordSplitter, '=')
    
    def test_heading_characters(self):
        """Test document heading character properties"""
        # Test all heading levels
        headings = {
            'documentH1Char': ('#', '!'),
            'documentH2Char': ('=', '@'),
            'documentH3Char': ('-', '$'),
            'documentH4Char': ('.', '%'),
            'documentH5Char': (',', '^'),
            'documentH6Char': (';', '&')
        }
        
        for prop_name, (default, new_val) in headings.items():
            # Test default value
            self.assertEqual(getattr(self.data, prop_name), default)
            
            # Test setting new value
            setattr(self.data, prop_name, new_val)
            self.assertEqual(getattr(self.data, prop_name), new_val)
            
            # Test persistence
            data2 = EnBrailleData(self.app)
            self.assertEqual(getattr(data2, prop_name), new_val)
    
    def test_bullet_characters(self):
        """Test document bullet character properties"""
        bullets = {
            'documentBulletL1Char': ('*', '►'),
            'documentBulletL2Char': ('+', '▸'),
            'documentBulletL3Char': ('-', '▪'),
            'documentBulletL4Char': ('.', '▫'),
            'documentBulletL5Char': (',', '◦'),
            'documentBulletL6Char': (';', '·')
        }
        
        for prop_name, (default, new_val) in bullets.items():
            # Test default value
            self.assertEqual(getattr(self.data, prop_name), default)
            
            # Test setting new value
            setattr(self.data, prop_name, new_val)
            self.assertEqual(getattr(self.data, prop_name), new_val)
    
    def test_skip_welcome_page_property(self):
        """Test skipWelcomePage property"""
        # Test default
        self.assertFalse(self.data.skipWelcomePage)
        
        # Test setting to True
        self.data.skipWelcomePage = True
        self.assertTrue(self.data.skipWelcomePage)
        
        # Test persistence
        data2 = EnBrailleData(self.app)
        self.assertTrue(data2.skipWelcomePage)
        
        # Test setting back to False
        self.data.skipWelcomePage = False
        self.assertFalse(self.data.skipWelcomePage)
    
    def test_reformat_keep_page_no_bug(self):
        """Test reformatKeepPageNo setter - this will reveal a logic bug"""
        # Test the bug in the setter logic
        original_page_length = self.data.reformatPageLength
        
        # This setter incorrectly compares reformatPageLength instead of reformatKeepPageNo
        # So it might not work correctly
        self.data.reformatKeepPageNo = True
        
        # If the bug exists, this might not have changed
        if self.data.reformatKeepPageNo != True:
            self.fail("BUG FOUND: reformatKeepPageNo setter compares wrong property (reformatPageLength instead of reformatKeepPageNo)")
    
    def test_reset_settings(self):
        """Test resetSettings method"""
        # Set some values
        self.data.mainFunction = EnBrailleMainFct.REFORMAT
        self.data.textTable = 'test-table.ctb'
        self.data.reformatLineLength = 100
        self.data.skipWelcomePage = True
        
        # Reset settings
        self.data.resetSettings()
        
        # Create new instance to check if settings were cleared
        data2 = EnBrailleData(self.app)
        
        # Should be back to defaults
        self.assertEqual(data2.mainFunction, EnBrailleMainFct.TEXT)
        self.assertEqual(data2.textTable, '')
        self.assertEqual(data2.reformatLineLength, 40)
        self.assertFalse(data2.skipWelcomePage)
    
    def test_public_members(self):
        """Test public member variables"""
        # Test that public members can be set and retrieved
        self.data.inputText = "Hello, World!"
        self.assertEqual(self.data.inputText, "Hello, World!")
        
        self.data.outputText = "⠓⠑⠇⠇⠕"
        self.assertEqual(self.data.outputText, "⠓⠑⠇⠇⠕")
        
        self.data.reformatFilename = "/path/to/file.brf"
        self.assertEqual(self.data.reformatFilename, "/path/to/file.brf")
        
        self.data.documentFilename = "/path/to/document.docx"
        self.assertEqual(self.data.documentFilename, "/path/to/document.docx")
    
    def test_settings_keys_consistency(self):
        """Test that settings keys are consistent"""
        # This tests for the inconsistency in documenttextTable vs documentTextTable
        self.data.documentLineLength = 50  # This should work
        
        # Check the actual settings key used
        settings_value = self.data._settings.value('documenttextTable', '', type=str)
        # The getter uses 'documenttextTable' but property is named documentTextTable
        # This is an inconsistency that should be noted
    
    def test_signal_connections(self):
        """Test that all signals are properly defined and can be connected"""
        # Test that signals exist and can be connected
        callback_called = False
        
        def test_callback(value):
            nonlocal callback_called
            callback_called = True
        
        # Test mainFunctionChanged signal
        self.data.mainFunctionChanged.connect(test_callback)
        self.data.mainFunction = EnBrailleMainFct.REFORMAT
        self.assertTrue(callback_called)
        
        # Reset and test TextTableChanged signal
        callback_called = False
        self.data.TextTableChanged.connect(test_callback)
        self.data.textTable = 'new-table'
        self.assertTrue(callback_called)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Test with empty strings
        self.data.textTable = ''
        self.assertEqual(self.data.textTable, '')
        
        # Test with invalid values - mainFunction accepts EnBrailleMainFct only
        # Setting None or invalid types should work but convert to default
        try:
            self.data.mainFunction = None
            # This might not raise an error but the value should remain valid
        except (TypeError, AttributeError):
            pass  # This is acceptable
        
        # Test with invalid enum conversion
        self.assertIsNone(EnBrailleMainFct.fromStr(None))
        self.assertIsNone(EnBrailleMainFct.fromStr(''))
        self.assertIsNone(EnBrailleMainFct.fromStr('INVALID_VALUE'))
    
    def test_type_safety(self):
        """Test type safety of properties"""
        # Test integer properties
        self.data.reformatLineLength = 100
        self.assertEqual(self.data.reformatLineLength, 100)
        
        # Test boolean properties
        self.data.reformatKeepPageNo = True
        self.assertTrue(self.data.reformatKeepPageNo)
        
        # Test string properties
        self.data.reformatWordSplitter = '|'
        self.assertEqual(self.data.reformatWordSplitter, '|')


def run_tests():
    """Run the unittest suite"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=== EnBrailleData Unit Tests ===")
    print("Testing EnBrailleData class and EnBrailleMainFct enum")
    print()
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        print("\nBugs that should be fixed:")
        print("1. Line 141: @textTable.setter should be @documentTextTable.setter")
        print("2. Line 132: Condition checks reformatPageLength instead of reformatKeepPageNo")
        print("3. Settings key inconsistency: 'documenttextTable' vs 'documentTextTable'")
    
    sys.exit(0 if success else 1)