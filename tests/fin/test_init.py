import unittest

import fin

# ======================================================================
# Versioning
# ======================================================================
class TestVersioning(unittest.TestCase):
    def test_version_info(self):
        """ The package provides version info as a tuple of integers.
        """
        self.assertIsInstance(fin.__version_info__, tuple)
        self.assertSequenceEqual(tuple(map(type,fin.__version_info__)), (int,)*3)

    def test_version(self):
        """ The package provides the version number as a string.
        """
        self.assertIsInstance(fin.__version__, str)

    def test_version(self):
        """ The package provides history info.
        """
        self.assertIsInstance(fin.__history__, dict)
        self.assertIn(fin.__version__, fin.__history__)

