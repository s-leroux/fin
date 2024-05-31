import unittest

import fin.utils.collections as uc

class TestDictionariesToList(unittest.TestCase):
    def test_it(self):
        test_cases = (
            "#0 Base case",
            ("x", "y"),
            [
                { "x": 10, "y": 100 },
                { "x": 20, "y": 200 },
                { "x": 30, "y": 300 },
                { "x": 40, "y": 400 },
            ],
            [
                [ 10, 100 ],
                [ 20, 200 ],
                [ 30, 300 ],
                [ 40, 400 ],
            ],

            "#1 extra fields",
            ("x", "y"),
            [
                { "x": 10, "y": 100 },
                { "x": 20, "y": 200, "z": 2000 },
                { "x": 30, "y": 300, "z": 3000 },
                { "x": 40, "y": 400 },
            ],
            [
                [ 10, 100 ],
                [ 20, 200 ],
                [ 30, 300 ],
                [ 40, 400 ],
            ],
        )

        while test_cases:
            desc, fields, dictionaries, expected, *test_cases = test_cases
            with self.subTest(desc=desc):
                actual = list(uc.dictionaries_to_list(fields, dictionaries))
                self.assertEqual(actual, expected)
