import unittest

import fin.model.turbo as turbo
import fin.math

class TestModelExceptions(unittest.TestCase):
    def test_undefined(self):
        with self.assertRaises(fin.model.Underdefined) as cm:
            raise fin.model.Underdefined(('a','b','c'))
        self.assertRegex(str(cm.exception),"Too many missing parameters")
        self.assertRegex(str(cm.exception),"'a',\s*'b',\s*'c'")
