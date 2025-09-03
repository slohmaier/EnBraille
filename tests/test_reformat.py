import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from enbraille_functions.reformat import EnBrailleReformater
from tests.test_utilenbraille import gen_data

TESTFILE_DIR = os.path.join(os.path.dirname(__file__), 'data')

class TestReformatBRF(unittest.TestCase):

    def test_reformat_simple(self):
        reformater = EnBrailleReformater(os.path.join(TESTFILE_DIR, 'reformat_simple.brf'))
        data = gen_data()
        # Mock the reformatLineLength property to return 0 for testing
        def mock_line_length(self):
            return 0
        data.__class__.reformatLineLength = property(mock_line_length)
        # Verify it's actually 0
        self.assertEqual(0, data.reformatLineLength)
        self.assertEqual('', reformater.reformat(None, data))
        