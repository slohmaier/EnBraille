import sys
import os
import unittest
import tempfile
import re
from unittest.mock import patch, MagicMock, mock_open

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Mock the Qt imports before importing the module
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()

# Mock QObject base class
class MockQObject:
    def __init__(self, *args, **kwargs):
        pass

# Replace QObject import
sys.modules['PySide6.QtCore'].QObject = MockQObject

from enbraille_functions.reformat import EnBrailleReformater
from enbraille_data import EnBrailleData, EnBrailleMainFct


class TestEnBrailleReformaterFileLoading(unittest.TestCase):
    """Test the EnBrailleReformater file loading and analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the QApplication dependency for EnBrailleData
        self.mock_app = MagicMock()
        self.mock_app.organizationName.return_value = "TestOrg"
        self.mock_app.applicationName.return_value = "TestApp"
    
    def test_page_number_regex(self):
        """Test the page number regex pattern"""
        regex = re.compile(r'^\s+\#\w+$')
        
        # Should match page numbers
        self.assertTrue(regex.match('\t#1'))
        self.assertTrue(regex.match('  #abc'))
        self.assertTrue(regex.match('    #123'))
        self.assertTrue(regex.match(' #a'))
        
        # Should not match
        self.assertFalse(regex.match('#1'))  # No leading space
        self.assertFalse(regex.match('\t#'))  # No word after #
        self.assertFalse(regex.match('\t#1 '))  # Trailing space
        self.assertFalse(regex.match('text #1'))  # Text before
    
    @patch('builtins.open', mock_open(read_data="Line 1\nLine 2\nLonger line here\n\t#1\nNew page\n\t#2\nEnd"))
    def test_load_file_analysis(self):
        """Test file loading and analysis"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should calculate max line length
            self.assertEqual(reformatter._maxLineLength, 16)  # "Longer line here"
            
            # Should detect page length (lines between page markers)
            self.assertGreater(reformatter._pageLength, 0)
    
    @patch('builtins.open', mock_open(read_data="A\nB\n\t#1\nC\nD\n\t#2\nE\nF\n\t#3"))
    def test_page_length_calculation(self):
        """Test page length calculation with consistent page breaks"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should detect consistent page length of 3 lines (including page marker)
            self.assertEqual(reformatter._pageLength, 3)
    
    @patch('builtins.open', mock_open(read_data="A\nB\n\t#1\nC\nD\nE\n\t#2\nF\nG\n\t#3"))
    def test_page_length_calculation_mixed(self):
        """Test page length calculation with mixed page lengths"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should pick most common page length (3 appears twice, 4 appears once)
            self.assertEqual(reformatter._pageLength, 3)
    
    @patch('builtins.open', mock_open(read_data="Line 1\nLine 2\nLine 3"))
    def test_no_page_markers(self):
        """Test file with no page markers"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should have zero page length
            self.assertEqual(reformatter._pageLength, 0)
    
    @patch('builtins.open', mock_open(read_data=""))
    def test_empty_file(self):
        """Test empty file handling"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should handle empty file gracefully
            self.assertEqual(reformatter._maxLineLength, 0)
            self.assertEqual(reformatter._pageLength, 0)
    
    def test_initialization_stores_filename(self):
        """Test that initialization stores the filename"""
        with patch('builtins.open', mock_open(read_data="test")), \
             patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            self.assertEqual(reformatter._filename, 'test.brf')


class TestEnBrailleReformaterParsing(unittest.TestCase):
    """Test the parsing logic of EnBrailleReformater"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_app = MagicMock()
        self.mock_app.organizationName.return_value = "TestOrg"  
        self.mock_app.applicationName.return_value = "TestApp"
    
    @patch('builtins.open', mock_open(read_data="Line 1\nLine 2"))
    def test_reformatter_has_parse_method(self):
        """Test that the reformatter has parsing capabilities"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should have the _parseParagraphs method (even if private)
            self.assertTrue(hasattr(reformatter, '_parseParagraphs'))
    
    @patch('builtins.open', mock_open())
    def test_reformatter_initialization_requirements(self):
        """Test reformatter initialization requirements"""
        with patch('os.path.exists', return_value=True):
            # Should require a filename
            reformatter = EnBrailleReformater('test.brf')
            
            # Should have required attributes after initialization
            self.assertTrue(hasattr(reformatter, '_filename'))
            self.assertTrue(hasattr(reformatter, '_maxLineLength'))
            self.assertTrue(hasattr(reformatter, '_pageLength'))


class TestEnBrailleReformaterConstants(unittest.TestCase):
    """Test the constants and class variables"""
    
    def test_page_number_regex_constant(self):
        """Test that the page number regex is properly defined"""
        # Test directly on the class
        with patch('builtins.open', mock_open()), \
             patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should have the regex pattern
            self.assertTrue(hasattr(reformatter, '_pagenoregex'))
            self.assertIsInstance(reformatter._pagenoregex, type(re.compile('')))
    
    def test_page_number_prefix_constant(self):
        """Test that the page number prefix is defined"""
        with patch('builtins.open', mock_open()), \
             patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should have the prefix constant
            self.assertTrue(hasattr(reformatter, '_pagenoprefix'))
            self.assertEqual(reformatter._pagenoprefix, '\t')


class TestEnBrailleReformaterEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_file_not_found_handling(self):
        """Test handling of missing files"""
        with self.assertRaises(FileNotFoundError):
            EnBrailleReformater('nonexistent.brf')
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_file_permission_error(self, mock_open):
        """Test handling of permission errors"""
        with self.assertRaises(PermissionError):
            EnBrailleReformater('restricted.brf')
    
    @patch('builtins.open', mock_open(read_data="Line with unicode: \u2603\n\t#\u2603"))
    def test_unicode_handling(self):
        """Test handling of unicode characters"""
        with patch('os.path.exists', return_value=True):
            try:
                reformatter = EnBrailleReformater('unicode.brf')
                # Should handle unicode gracefully
                self.assertIsInstance(reformatter._maxLineLength, int)
                self.assertIsInstance(reformatter._pageLength, int)
            except UnicodeError:
                self.fail("Should handle unicode characters")
    
    @patch('builtins.open', mock_open(read_data="Very long line " * 1000))
    def test_very_long_lines(self):
        """Test handling of very long lines"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('long.brf')
            
            # Should calculate line length correctly
            expected_length = len("Very long line " * 1000)
            self.assertEqual(reformatter._maxLineLength, expected_length)


class TestEnBrailleReformaterIntegration(unittest.TestCase):
    """Integration tests for the reformatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_app = MagicMock()
        self.mock_app.organizationName.return_value = "TestOrg"
        self.mock_app.applicationName.return_value = "TestApp"
        
        # Create a mock EnBrailleData
        with patch('PySide6.QtCore.QSettings'):
            self.mock_data = EnBrailleData(self.mock_app)
    
    @patch('builtins.open', mock_open(read_data="Test content\nLine 2\n\t#1\nNew page\n\t#2"))
    def test_complete_initialization_workflow(self):
        """Test complete initialization workflow"""
        with patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('test.brf')
            
            # Should have all required attributes
            self.assertIsNotNone(reformatter._filename)
            self.assertGreaterEqual(reformatter._maxLineLength, 0)
            self.assertGreaterEqual(reformatter._pageLength, 0)
            
            # Should be ready for reformatting operations
            self.assertTrue(hasattr(reformatter, 'reformat'))
    
    def test_reformatter_with_realistic_file_structure(self):
        """Test reformatter with realistic Braille file structure"""
        realistic_content = """This is the first line of text.
This is the second line.
    #1
This is the start of page 2.
Another line on page 2.
    #2
Final page content here.
Last line of the document.
    #3"""
        
        with patch('builtins.open', mock_open(read_data=realistic_content)), \
             patch('os.path.exists', return_value=True):
            reformatter = EnBrailleReformater('realistic.brf')
            
            # Should detect the structure
            self.assertGreater(reformatter._maxLineLength, 0)
            self.assertEqual(reformatter._pageLength, 3)  # 3 lines per page (including page marker)


class TestEnBrailleReformaterPageLengthLogic(unittest.TestCase):
    """Test the specific page length calculation logic"""
    
    def test_page_length_counting_algorithm(self):
        """Test the page length counting algorithm directly"""
        # Test data with various page lengths
        test_cases = [
            # (content, expected_page_length)
            ("A\n\t#1\nB\n\t#2", 2),  # 2 lines per page (including page marker)
            ("A\nB\n\t#1\nC\nD\n\t#2", 3),  # 3 lines per page (including page marker)
            ("A\nB\nC\n\t#1\nD\nE\nF\n\t#2", 4),  # 4 lines per page (including page marker)
            ("A\n\t#1\nB\nC\n\t#2\nD\n\t#3", 2),  # Mixed: 2,3,2 -> most common is 2
        ]
        
        for content, expected in test_cases:
            with patch('builtins.open', mock_open(read_data=content)), \
                 patch('os.path.exists', return_value=True):
                reformatter = EnBrailleReformater('test.brf')
                self.assertEqual(reformatter._pageLength, expected, 
                               f"Failed for content: {repr(content)}")


def run_tests():
    """Run the unittest suite"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=== EnBraille Reformatter Logic Unit Tests ===")
    print("Testing business logic (non-UI parts of enbraille_functions/reformat.py)")
    print()
    
    success = run_tests()
    
    if success:
        print("\n✅ All EnBraille Reformatter Logic tests passed!")
    else:
        print("\n❌ Some EnBraille Reformatter Logic tests failed!")
    
    sys.exit(0 if success else 1)