import unittest

from fin.seq2 import serie
from fin.seq2 import presentation

class TestPresentation(unittest.TestCase):
    def test_create_one_column_presentation(self):
        pres = presentation.Presentation(
                heading=False,
            )
        ser = serie.Serie("ABCDEF", (1,2,3,4,5,6))
        
        expected = "\n".join((
                "A, 1",
                "B, 2",
                "C, 3",
                "D, 4",
                "E, 5",
                "F, 6",
        ))
        self.assertEqual(pres(ser), expected)

