import unittest

from fin import datetime
from fin.seq import coltypes

class TestFloat(unittest.TestCase):
    def test_parse_sequence(self):
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
                actual = typ.parse_sequence(seq)
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
                typ.parse_sequence(seq)
                self.assertEqual(typ._options["precision.inferred"], precision)

class TestDateTime(unittest.TestCase):
    def test_parse_sequence(self):
        dt = datetime.CalendarDateTime(2023, 12, 5, 18, 30, 14)
        test_cases = (
                "#0 Idendtity",
                dt,
                dt,

                "#1 From iso string",
                "2023-12-05 18:30:14",
                dt,

                "#2 From timestamp",
                dt.timestamp,
                dt,

                "#3 None",
                None,
                None,
            )

        while test_cases:
            desc, indata, expected, *test_cases = test_cases
            typ = coltypes.DateTime()
            with self.subTest(desc=desc):
                actual = typ.parse_sequence((indata,))
                self.assertSequenceEqual(actual, (expected,))

