import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from libbrl import libbrlImpls, libbrlInterface, libbrlImpl, libbrlLouis


class TestLibbrlEnums(unittest.TestCase):
    """Test the libbrl enums and interfaces"""
    
    def test_libbrl_impls_enum(self):
        """Test libbrlImpls enum"""
        self.assertEqual(libbrlImpls.LOUIS.value, 1)
        self.assertEqual(libbrlImpls.LOUIS.name, 'LOUIS')
    
    def test_libbrl_interface_abstract(self):
        """Test that libbrlInterface is abstract"""
        interface = libbrlInterface()
        
        with self.assertRaises(NotImplementedError):
            interface.listTables()
        
        with self.assertRaises(NotImplementedError):
            interface.translate("test", "table")


class TestLibbrlImpl(unittest.TestCase):
    """Test the libbrlImpl factory function"""
    
    def test_default_implementation(self):
        """Test default implementation returns Louis"""
        impl = libbrlImpl()
        self.assertIsInstance(impl, libbrlLouis)
    
    def test_explicit_louis_implementation(self):
        """Test explicit Louis implementation"""
        impl = libbrlImpl(libbrlImpls.LOUIS)
        self.assertIsInstance(impl, libbrlLouis)
    
    def test_invalid_implementation(self):
        """Test invalid implementation raises error"""
        # Create a mock invalid enum value that's not LOUIS
        invalid_impl = MagicMock()
        invalid_impl.__eq__ = lambda x, y: False  # Not equal to LOUIS
        
        with self.assertRaises(NotImplementedError):
            libbrlImpl(invalid_impl)


class TestLibbrlLouis(unittest.TestCase):
    """Test the libbrlLouis implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.louis_impl = libbrlLouis()
    
    def test_initialization(self):
        """Test Louis implementation initialization"""
        self.assertIsNone(self.louis_impl._tables)
        self.assertIsInstance(self.louis_impl, libbrlInterface)
    
    @patch('libbrl.louis')
    @patch('builtins.open', mock_open(read_data="# liblouis: English Grade 1\ndisplay: English Grade 1"))
    @patch('os.path.basename')
    def test_list_tables_success(self, mock_basename, mock_louis):
        """Test successful table listing"""
        # Mock the Louis library calls
        mock_table_ptr = MagicMock()
        mock_table_ptr.__getitem__.side_effect = [
            b'/path/to/en-us-g1.ctb',  # First table
            b'/path/to/de-g1.ctb',     # Second table
            None                        # End marker
        ]
        mock_louis.liblouis.lou_listTables.return_value = mock_table_ptr
        
        # Mock basename to return filename
        mock_basename.side_effect = ['en-us-g1.ctb', 'de-g1.ctb']
        
        # Mock ctypes.string_at
        with patch('libbrl.ctypes.string_at') as mock_string_at:
            mock_string_at.side_effect = [
                b'/path/to/en-us-g1.ctb',
                b'/path/to/de-g1.ctb'
            ]
            
            # Call listTables
            tables = self.louis_impl.listTables()
            
            # Verify results
            expected_tables = {
                'English Grade 1': 'en-us-g1.ctb',
                'English Grade 1': 'de-g1.ctb'  # Note: duplicate key will overwrite
            }
            
            self.assertIsInstance(tables, dict)
            self.assertGreater(len(tables), 0)
            
            # Verify tables are cached
            self.assertIsNotNone(self.louis_impl._tables)
            
            # Second call should return cached result
            tables2 = self.louis_impl.listTables()
            self.assertIs(tables, tables2)
    
    def test_list_tables_caching(self):
        """Test that tables are cached after first call"""
        # Mock tables
        test_tables = {'English Grade 1': 'en-us-g1.ctb'}
        self.louis_impl._tables = test_tables
        
        # Call listTables - should return cached result
        result = self.louis_impl.listTables()
        self.assertIs(result, test_tables)
    
    @patch('libbrl.louis.translateString')
    def test_translate_with_table_name(self, mock_translate):
        """Test translation with table name"""
        # Set up mock tables
        self.louis_impl._tables = {
            'English Grade 1': 'en-us-g1.ctb',
            'German Grade 1': 'de-g1.ctb'
        }
        
        # Mock translation result
        mock_translate.return_value = '⠓⠑⠇⠇⠕'
        
        # Test translation
        result = self.louis_impl.translate('Hello', 'English Grade 1')
        
        # Verify call
        mock_translate.assert_called_once_with(['en-us-g1.ctb'], 'Hello')
        self.assertEqual(result, '⠓⠑⠇⠇⠕')
    
    @patch('libbrl.louis.translateString')
    def test_translate_with_table_filename(self, mock_translate):
        """Test translation with table filename"""
        # Set up mock tables
        self.louis_impl._tables = {
            'English Grade 1': 'en-us-g1.ctb',
        }
        
        # Mock translation result
        mock_translate.return_value = '⠓⠑⠇⠇⠕'
        
        # Test translation with filename
        result = self.louis_impl.translate('Hello', 'en-us-g1.ctb')
        
        # Verify call
        mock_translate.assert_called_once_with(['en-us-g1.ctb'], 'Hello')
        self.assertEqual(result, '⠓⠑⠇⠇⠕')
    
    def test_translate_unknown_table(self):
        """Test translation with unknown table"""
        # Set up mock tables
        self.louis_impl._tables = {
            'English Grade 1': 'en-us-g1.ctb',
        }
        
        # Test with unknown table
        with self.assertRaises(ValueError) as context:
            self.louis_impl.translate('Hello', 'unknown-table')
        
        self.assertIn('Unknown table unknown-table', str(context.exception))
    
    @patch('libbrl.louis.translateString')
    def test_translate_lazy_loading_tables(self, mock_translate):
        """Test that translate loads tables if not already loaded"""
        # Ensure tables are not loaded
        self.louis_impl._tables = None
        
        # Mock listTables method
        with patch.object(self.louis_impl, 'listTables') as mock_list_tables:
            mock_list_tables.return_value = {'English Grade 1': 'en-us-g1.ctb'}
            mock_translate.return_value = '⠓⠑⠇⠇⠕'
            
            # Call translate
            result = self.louis_impl.translate('Hello', 'English Grade 1')
            
            # Verify listTables was called
            mock_list_tables.assert_called_once()
            mock_translate.assert_called_once_with(['en-us-g1.ctb'], 'Hello')
            self.assertEqual(result, '⠓⠑⠇⠇⠕')
    
    def test_translate_empty_input(self):
        """Test translation with empty input"""
        # Set up mock tables
        self.louis_impl._tables = {'English Grade 1': 'en-us-g1.ctb'}
        
        with patch('libbrl.louis.translateString') as mock_translate:
            mock_translate.return_value = ''
            
            result = self.louis_impl.translate('', 'English Grade 1')
            
            mock_translate.assert_called_once_with(['en-us-g1.ctb'], '')
            self.assertEqual(result, '')
    
    def test_translate_special_characters(self):
        """Test translation with special characters"""
        # Set up mock tables
        self.louis_impl._tables = {'English Grade 1': 'en-us-g1.ctb'}
        
        with patch('libbrl.louis.translateString') as mock_translate:
            mock_translate.return_value = '⠼⠁⠃⠉'
            
            # Test with numbers and symbols
            result = self.louis_impl.translate('123!@#', 'English Grade 1')
            
            mock_translate.assert_called_once_with(['en-us-g1.ctb'], '123!@#')
            self.assertEqual(result, '⠼⠁⠃⠉')


class TestLibbrlIntegration(unittest.TestCase):
    """Integration tests for the libbrl module"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from factory to translation"""
        with patch('libbrl.louis') as mock_louis, \
             patch('builtins.open', mock_open(read_data="# liblouis: English Grade 1\n")), \
             patch('os.path.basename', return_value='en-us-g1.ctb'):
            
            # Mock Louis library
            mock_table_ptr = MagicMock()
            # Use list instead of side_effect to avoid StopIteration
            mock_table_ptr.__getitem__ = MagicMock(side_effect=lambda i: [b'/path/to/en-us-g1.ctb', None][i])
            mock_louis.liblouis.lou_listTables.return_value = mock_table_ptr
            mock_louis.translateString.return_value = '⠓⠑⠇⠇⠕'
            
            with patch('libbrl.ctypes.string_at', return_value=b'/path/to/en-us-g1.ctb'):
                # Get implementation
                impl = libbrlImpl()
                
                # List tables
                tables = impl.listTables()
                self.assertIsInstance(tables, dict)
                
                # Translate text - use the table filename since that's what will be available
                if 'English Grade 1' in tables:
                    result = impl.translate('Hello', 'English Grade 1')
                else:
                    # Fallback to filename
                    result = impl.translate('Hello', 'en-us-g1.ctb')
                self.assertEqual(result, '⠓⠑⠇⠇⠕')
    
    def test_multiple_implementations(self):
        """Test that multiple implementations can coexist"""
        impl1 = libbrlImpl(libbrlImpls.LOUIS)
        impl2 = libbrlImpl(libbrlImpls.LOUIS)
        
        # They should be different instances
        self.assertIsNot(impl1, impl2)
        self.assertIsInstance(impl1, libbrlLouis)
        self.assertIsInstance(impl2, libbrlLouis)


class TestLibbrlErrorHandling(unittest.TestCase):
    """Test error handling in libbrl module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.louis_impl = libbrlLouis()
    
    @patch('libbrl.louis')
    @patch('os.path.basename', return_value='en-us-g1.ctb')
    def test_list_tables_file_not_found(self, mock_basename, mock_louis):
        """Test handling of missing table files"""
        # Mock Louis library
        mock_table_ptr = MagicMock()
        mock_table_ptr.__getitem__.side_effect = [b'/path/to/missing.ctb', None]
        mock_louis.liblouis.lou_listTables.return_value = mock_table_ptr
        
        with patch('libbrl.ctypes.string_at', return_value=b'/path/to/missing.ctb'), \
             patch('builtins.open', side_effect=FileNotFoundError("Table file not found")):
            
            # Should raise the file not found error (current implementation doesn't handle it)
            with self.assertRaises(FileNotFoundError):
                self.louis_impl.listTables()
    
    @patch('libbrl.louis.translateString', side_effect=Exception("Translation error"))
    def test_translate_louis_error(self, mock_translate):
        """Test handling of Louis translation errors"""
        # Set up mock tables
        self.louis_impl._tables = {'English Grade 1': 'en-us-g1.ctb'}
        
        # Translation should propagate the error
        with self.assertRaises(Exception) as context:
            self.louis_impl.translate('Hello', 'English Grade 1')
        
        self.assertIn("Translation error", str(context.exception))


def run_tests():
    """Run the unittest suite"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=== LibBRL Unit Tests ===")
    print("Testing Braille translation library (libbrl.py)")
    print()
    
    success = run_tests()
    
    if success:
        print("\n✅ All LibBRL tests passed!")
    else:
        print("\n❌ Some LibBRL tests failed!")
    
    sys.exit(0 if success else 1)