import unittest

from fin.seq import coltypes

class TestFloat(unittest.TestCase):
    def test_parse_string_sequence(self):
        test_cases = (
                "#0 Basic use case",
                ( "10.5", "1.45", "100.345", "1.2345", "-10"),
                ( 10.5, 1.45, 100.345, 1.2345, -10),

                "#1 Non-float input",
                ( "10.5", "1.45", "n/a", "NaN", "None", "-10"),
                ( 10.5, 1.45, None, None, None, -10),
            )

        while test_cases:
            desc, seq, expected, *test_cases = test_cases
            typ = coltypes.Float()
            with self.subTest(desc=desc):
                actual = typ.parse_string_sequence(seq)
                self.assertSequenceEqual(actual, expected)

    def test_precision_inference(self):
        test_cases = (
                "#0 Basic use case",
                ( "10.5", "1.45", "100.345", "1.2345", "-10"),
                4,
                "#1 Integers only",
                ( "10", "1", "100", "12345", "-10"),
                2, # XXX Should be zero?

            )

        while test_cases:
            desc, seq, precision, *test_cases = test_cases
            typ = coltypes.Float()
            with self.subTest(desc=desc):
                typ.parse_string_sequence(seq)
                self.assertEqual(typ._options["precision.inferred"], precision)

