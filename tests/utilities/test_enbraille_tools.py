import sys
import os
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from enbraille_tools import reformatPragraph, generateOutput, _BREILLENUMS


class TestReformatParagraph(unittest.TestCase):
    """Test the reformatPragraph function"""
    
    def test_simple_paragraph(self):
        """Test basic paragraph reformatting"""
        paragraph = "Hello world this is a test"
        result = reformatPragraph(paragraph, 10, '-')
        
        # Should break into appropriate lines
        self.assertIsInstance(result, list)
        self.assertTrue(all(len(line) <= 10 for line in result if line))
        
        # Should preserve all words (the function adds spaces that get doubled when joined)
        rejoined = ' '.join(result).replace('  ', ' ').strip()
        expected = paragraph
        self.assertEqual(rejoined, expected)
    
    def test_exact_line_length(self):
        """Test with words that exactly fit the line length"""
        paragraph = "hello world"  # exactly 11 characters
        result = reformatPragraph(paragraph, 11, '-')
        
        # Should fit exactly on one line
        self.assertEqual(len(result), 2)  # Last line is empty
        self.assertEqual(result[0], "hello world")
        self.assertEqual(result[1], "")
    
    def test_line_length_zero_or_negative(self):
        """Test with zero or negative line length"""
        paragraph = "Hello world this is a test"
        
        # Zero line length should return all words on one line (no trailing space)
        result = reformatPragraph(paragraph, 0, '-')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], paragraph)  # No trailing space in this case
        
        # Negative line length should also return all words on one line
        result = reformatPragraph(paragraph, -1, '-')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], paragraph)
    
    def test_word_splitting(self):
        """Test splitting of long words"""
        # Word longer than line length should be split
        paragraph = "supercalifragilisticexpialidocious"
        result = reformatPragraph(paragraph, 10, '-')
        
        # Should have multiple lines
        self.assertGreater(len(result), 1)
        
        # Split lines should end with separator
        for line in result[:-1]:  # All but last line
            if len(line) == 10:  # Full lines
                self.assertTrue(line.endswith('-'))
    
    def test_empty_paragraph(self):
        """Test with empty paragraph"""
        result = reformatPragraph("", 10, '-')
        # Function behavior: empty string becomes single space after split/join
        self.assertEqual(result, [' '])
    
    def test_single_word(self):
        """Test with single word"""
        result = reformatPragraph("hello", 10, '-')
        self.assertEqual(result, ['hello '])
    
    def test_multiple_spaces(self):
        """Test with multiple spaces between words"""
        paragraph = "hello    world"
        result = reformatPragraph(paragraph, 20, '-')
        
        # Function preserves multiple spaces (doesn't collapse them)
        self.assertEqual(result[0], "hello    world ")
    
    def test_different_separators(self):
        """Test with different line separators"""
        paragraph = "verylongwordthatneedstosplit"
        
        # Test with different separators
        for separator in ['-', '=', '~', '|']:
            result = reformatPragraph(paragraph, 10, separator)
            
            # Split lines should use the correct separator
            for line in result[:-1]:
                if len(line) == 10:
                    self.assertTrue(line.endswith(separator))
    
    def test_word_splitting_edge_cases(self):
        """Test edge cases in word splitting logic"""
        # Word that's exactly one character longer than line length
        paragraph = "abcdefghijk"  # 11 characters
        result = reformatPragraph(paragraph, 10, '-')
        
        # Should split correctly
        self.assertGreater(len(result), 1)
        
        # Test the splitting logic conditions
        # When lineLen + wordLen + 1 < lineLength
        paragraph = "ab cd"  # Should fit on one line with 10 char limit
        result = reformatPragraph(paragraph, 10, '-')
        self.assertEqual(result[0], "ab cd ")
        
        # When lineLen + wordLen == lineLength
        paragraph = "abcd efgh"  # Should fit exactly
        result = reformatPragraph(paragraph, 9, '-')
        self.assertEqual(result[0], "abcd efgh")
    
    def test_word_splitting_condition(self):
        """Test the specific word splitting condition (lineLen - wordLen > 2)"""
        # This tests line 39: if lineLen - wordLen > 2
        # Create a scenario where this condition matters
        
        # Start with some text to establish lineLen > 0
        paragraph = "ab verylongword"
        result = reformatPragraph(paragraph, 8, '-')
        
        # Should handle the splitting logic correctly
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 1)


class TestGenerateOutput(unittest.TestCase):
    """Test the generateOutput function"""
    
    def test_simple_output(self):
        """Test basic output generation"""
        lines = ["Line 1", "Line 2", "Line 3"]
        result = generateOutput(lines, 0, 40)  # No page breaks
        
        expected = "Line 1\nLine 2\nLine 3\n"
        self.assertEqual(result, expected)
    
    def test_no_page_breaks(self):
        """Test output without page breaks (pageLength = 0)"""
        lines = ["A", "B", "C", "D", "E"]
        result = generateOutput(lines, 0, 40)
        
        # Should not contain page numbers
        self.assertNotIn('#', result)
        
        # Should have all lines
        lines_in_result = result.strip().split('\n')
        self.assertEqual(lines_in_result, lines)
    
    def test_with_page_breaks(self):
        """Test output with page breaks"""
        lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        result = generateOutput(lines, 2, 20)  # Page break every 2 lines
        
        # Should contain page numbers
        self.assertIn('#', result)
        
        # Should contain Braille page numbers
        result_lines = result.split('\n')
        
        # Find page number lines (contain #)
        page_lines = [line for line in result_lines if '#' in line]
        self.assertGreater(len(page_lines), 0)
        
        # Check that page numbers are in Braille format
        for page_line in page_lines:
            page_part = page_line.strip().split()[-1]  # Get the page number part
            if page_part.startswith('#'):
                # Should contain Braille characters
                braille_part = page_part[1:]  # Remove #
                for char in braille_part:
                    if char.isdigit():
                        # Original digits should be converted to Braille
                        self.fail(f"Found unconverted digit {char} in {page_part}")
    
    def test_page_number_positioning(self):
        """Test that page numbers are right-aligned"""
        lines = ["A", "B"]
        result = generateOutput(lines, 2, 20)  # Page break after 2 lines
        
        result_lines = result.split('\n')
        page_lines = [line for line in result_lines if '#' in line]
        
        for page_line in page_lines:
            # Page numbers should be right-aligned
            # Format: spaces + page_number
            self.assertTrue(page_line.startswith(' '))
            
            # Total line length should be lineLength + 1 (including newline handling)
            # The page line should be properly formatted
            self.assertLessEqual(len(page_line), 20)
    
    def test_braille_number_conversion(self):
        """Test that numbers are converted to Braille correctly"""
        lines = ["Line"] * 10  # 10 lines to get to page 2
        result = generateOutput(lines, 5, 20)  # Page break every 5 lines
        
        # Should have page numbers converted to Braille
        for digit, braille in _BREILLENUMS.items():
            if f"#{digit}" in result:
                # Should be replaced with Braille equivalent
                self.assertIn(f"#{braille}", result)
    
    def test_empty_lines(self):
        """Test with empty lines list"""
        result = generateOutput([], 5, 20)
        self.assertEqual(result, "")
    
    def test_single_line(self):
        """Test with single line"""
        result = generateOutput(["Single line"], 0, 20)
        self.assertEqual(result, "Single line\n")
    
    def test_page_break_at_boundary(self):
        """Test page break calculation at exact boundaries"""
        # Test with exact multiples
        lines = ["A"] * 6  # Exactly 3 pages with pageLength=2
        result = generateOutput(lines, 2, 20)
        
        result_lines = result.split('\n')
        page_lines = [line for line in result_lines if '#' in line]
        
        # Should have page breaks (note: the logic adds page breaks after each page)
        self.assertGreater(len(page_lines), 0)
    
    def test_line_numbering(self):
        """Test that line numbering works correctly"""
        lines = ["A", "B", "C", "D"]
        result = generateOutput(lines, 2, 20)
        
        # The page number logic uses line number to determine when to insert page breaks
        # Line 1: A, Line 2: B -> Page break (lineno % pageLength == 0)
        # Line 3: C, Line 4: D -> Page break
        
        result_lines = result.split('\n')
        
        # Should have all original lines
        content_lines = [line for line in result_lines if line and not line.strip().startswith('#')]
        
        # Filter out empty lines
        content_lines = [line for line in content_lines if line.strip()]
        self.assertEqual(content_lines, lines)


class TestBrailleNumbers(unittest.TestCase):
    """Test the Braille numbers constant"""
    
    def test_braille_numbers_mapping(self):
        """Test that _BREILLENUMS has correct mappings"""
        expected_mappings = {
            '0': 'j', '1': 'a', '2': 'b', '3': 'c', '4': 'd', 
            '5': 'e', '6': 'f', '7': 'g', '8': 'h', '9': 'i'
        }
        
        self.assertEqual(_BREILLENUMS, expected_mappings)
    
    def test_all_digits_mapped(self):
        """Test that all digits 0-9 are mapped"""
        for digit in '0123456789':
            self.assertIn(digit, _BREILLENUMS)
        
        # Should have exactly 10 mappings
        self.assertEqual(len(_BREILLENUMS), 10)
    
    def test_braille_characters_unique(self):
        """Test that each digit maps to a unique Braille character"""
        braille_chars = list(_BREILLENUMS.values())
        unique_chars = set(braille_chars)
        
        # All characters should be unique
        self.assertEqual(len(braille_chars), len(unique_chars))
    
    def test_braille_characters_valid(self):
        """Test that Braille characters are lowercase letters"""
        for braille_char in _BREILLENUMS.values():
            self.assertTrue(braille_char.islower())
            self.assertTrue(braille_char.isalpha())
            self.assertEqual(len(braille_char), 1)


class TestEnbrailleToolsIntegration(unittest.TestCase):
    """Integration tests combining multiple functions"""
    
    def test_paragraph_to_output_workflow(self):
        """Test complete workflow from paragraph reformatting to output generation"""
        paragraph = "This is a long paragraph that needs to be reformatted into multiple lines."
        
        # Step 1: Reformat paragraph
        lines = reformatPragraph(paragraph, 20, '-')
        
        # Remove empty trailing line if present
        if lines and lines[-1] == '':
            lines = lines[:-1]
        
        # Step 2: Generate output with page breaks
        output = generateOutput(lines, 3, 20)
        
        # Should contain all words from original paragraph (accounting for word splitting)
        words_in_output = output.replace('\n', ' ').replace('-', ' ').split()
        original_words = paragraph.split()
        
        # Check that the essential content is preserved (allowing for word splits)
        output_text = output.replace('\n', ' ').replace('-', '').replace('#', ' ')
        for word in original_words:
            # Word might be split, so check if its characters are all present in sequence
            if word not in output_text:
                # Check if word appears as substring (may be split)
                word_chars = ''.join(c for c in word if c.isalpha())
                output_chars = ''.join(c for c in output_text if c.isalpha())
                self.assertIn(word_chars, output_chars, f"Word '{word}' not found in output")
        
        # Should contain proper formatting
        self.assertIsInstance(output, str)
        self.assertTrue(len(output) > 0)
    
    def test_page_numbering_integration(self):
        """Test page numbering with reformatted content"""
        # Create content that will span multiple pages
        long_text = "Word " * 50  # 50 repetitions of "Word "
        lines = reformatPragraph(long_text, 15, '-')
        
        # Remove empty trailing line
        if lines and lines[-1] == '':
            lines = lines[:-1]
        
        # Generate with frequent page breaks to test numbering
        output = generateOutput(lines, 5, 15)
        
        # Should have multiple page numbers
        page_markers = [line for line in output.split('\n') if '#' in line]
        self.assertGreater(len(page_markers), 1)
        
        # Page numbers should be converted to Braille
        for marker in page_markers:
            # Should not contain regular digits after the #
            page_part = marker.split('#')[1] if '#' in marker else ""
            for char in page_part:
                if char.isdigit():
                    self.fail(f"Found unconverted digit {char} in page marker")
    
    def test_edge_case_combinations(self):
        """Test edge cases when combining functions"""
        # Empty paragraph
        empty_lines = reformatPragraph("", 10, '-')
        empty_output = generateOutput(empty_lines, 5, 10)
        self.assertEqual(empty_output, " \n")  # Empty becomes space
        
        # Single character
        single_lines = reformatPragraph("A", 10, '-')
        single_output = generateOutput(single_lines, 5, 10)
        self.assertEqual(single_output, "A \n")
        
        # Very long word
        long_word = "x" * 100
        long_lines = reformatPragraph(long_word, 10, '-')
        long_output = generateOutput(long_lines, 5, 10)
        
        # Should handle gracefully
        self.assertIsInstance(long_output, str)
        self.assertGreater(len(long_output), 0)


def run_tests():
    """Run the unittest suite"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=== EnBraille Tools Unit Tests ===")
    print("Testing utility functions (enbraille_tools.py)")
    print()
    
    success = run_tests()
    
    if success:
        print("\n✅ All EnBraille Tools tests passed!")
    else:
        print("\n❌ Some EnBraille Tools tests failed!")
    
    sys.exit(0 if success else 1)