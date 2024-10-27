import unittest
import os
from enbraille_functions.reformat import EnBrailleReformater
from test_utilenbraille import gen_data

TESTFILE_DIR = os.path.join(os.path.dirname(__file__), 'data')

class TestReformatBRF(unittest.TestCase):

    def test_reformat_simple(self):
        reformater = EnBrailleReformater(os.path.join(TESTFILE_DIR, 'reformat_simple.brf'))
        data = gen_data()
        data.reformatLineLength = 0
        self.assertEqual('', reformater.reformat(None, data))
        