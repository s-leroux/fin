import unittest

import array
from . import ternary

class TestTernaryParser(unittest.TestCase):
    def test_parser(self):
        testcases = (
                "#0 Empty string should not break",
                "",
                (),

                "#1 Parse sequence of T, F and N",
                ("T","F","F","N","T","N"),
                (+1, -1, -1,  0, +1,  0),

                "#2 Invalid characters in the ASCII range",
                ("T","F","X","N","T","N"),
                ValueError,

                "#3 Invalid characters in the ASCII range",
                ("T","F","\u6400","N","T","N"),
                ValueError,
            )

        while testcases:
            desc, pat, expected, *testcases = testcases
            with self.subTest(desc=desc):
                pat = "".join(pat).encode("utf8")
                if isinstance(expected, type):
                    # Exceptions
                    with self.assertRaises(expected):
                        res = ternary.parse_pattern(pat)
                else:
                    # Normal path
                    res = ternary.parse_pattern(pat)

                    self.assertIsInstance(res, array.array)
                    self.assertEqual(res.typecode, "b")
                    self.assertSequenceEqual(res, expected)
