import unittest

from fin.seq2.fc import ti
from fin.seq2.column import Column
from fin.seq2.serie import Serie

from tests.fin.seq2.fc import utilities

# ======================================================================
# Technical indicators
# ======================================================================
class TestSimpleMovingAverage(unittest.TestCase):
    def test_sma(self):
        actual = utilities.apply(self,
            ti.sma(2),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual.py_values, [ None, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5 ])

class TestIndicators(unittest.TestCase):
    """
    Test engine for indicators.
    """
    def test_indicators(self):
        #
        # Test definitions
        #
        tests = [
            #
            # Average True Range
            #
            [
                ti.atr(4),
                "from 'Technical Analysis from A to Z, 2nd edition', p69",
                3, 1, # data geometry
                4, # precision
                # Data
                # tesseract --psm 6 photo.png - | sed -E -e 's/\s12\.?/ 12./g' -e 's/\s-?0/&./g' -e 's/\.\././g' | column -t
                12.3125, 12.1875, 12.2500, None,
                12.2500, 12.1562, 12.1875, None,
                12.3125, 12.1875, 12.2500, None,
                12.2812, 12.1250, 12.1875, 0.1250,
                12.3750, 12.1250, 12.3750, 0.1562,
                12.3750, 12.2812, 12.3125, 0.1406,
                12.3125, 12.1875, 12.2188, 0.1367,
                12.3750, 12.1875, 12.3438, 0.1494,
                12.5000, 12.2812, 12.5000, 0.1668,
                12.5938, 12.3125, 12.3750, 0.1954,
                12.3438, 12.2812, 12.3438, 0.1700,
                12.4062, 12.2812, 12.3438, 0.1587,
                12.3750, 12.2812, 12.2812, 0.1425,
                12.4062, 12.2812, 12.3750, 0.1381,
                12.3750, 11.9688, 12.0938, 0.2052,
                12.2812, 12.0938, 12.1562, 0.2007,
                12.2500, 12.0000, 12.0625, 0.2130,
                12.0625, 11.6562, 11.9688, 0.2614,
                12.3125, 12.1562, 12.1875, 0.2819,
                12.3125, 12.1250, 12.1562, 0.2583,
            ],
            [
                ti.atr(5),
                "from https://github.com/TulipCharts/tulipindicators/blob/master/tests/untest.txt",
                3, 1, # data geometr
                3, # precision
                # Data
                82.15,  81.29,  81.59,  None,
                81.89,  80.64,  81.06,  None,
                83.03,  81.31,  82.87,  None,
                83.3,   82.65,  83.0,   None,
                83.85,  83.07,  83.61,  1.116,
                83.9,   83.11,  83.15,  1.051,
                83.33,  82.49,  82.84,  1.009,
                84.3,   82.3,   83.99,  1.207,
                84.84,  84.15,  84.55,  1.136,
                85.0,   84.11,  84.36,  1.086,
                85.9,   84.03,  85.53,  1.243,
                86.58,  85.39,  86.54,  1.233,
                86.98,  85.76,  86.89,  1.23,
                88.0,   87.17,  87.77,  1.206,
                87.87,  87.01,  87.29,  1.137,
            ],
            #
            # Exponential Moving Average
            #
            [
                ti.ema(3),
                "ema",
                1, 1, # data geometry
                5, # precision
                # Data
                10, None,
                11, None,
                12, None,
                13, 12.12500, # XXX should we discard that value or not?
                14, 13.06250,
                15, 14.03125,
                16, 15.01562,
                17, 16.00781,
                18, 17.00391,
                19, 18.00195,
            ],
            #
            # Exponential Moving Average
            #
            [
                ti.ema(3),
                "ema with missing data",
                1, 1, # data geometry
                5, # precision
                # Data
                10,   None,
                11,   None,
                12,   None,
                13,   12.12500,
                14,   13.06250,
                None, None,
                16,   None,
                17,   None,
                18,   None,
                19,   18.12500,
            ],
            #
            # True Range
            #
            [
                ti.tr,
                "from 'Technical Analysis from A to Z, 2nd edition', p69",
                3, 1, # data geometry
                4, # precision
                # Data
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2500, 12.1562, 12.1875, 0.0938,
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2812, 12.1250, 12.1875, 0.1562,
                12.3750, 12.1250, 12.3750, 0.2500,
                12.3750, 12.2812, 12.3125, 0.0938,
                12.3125, 12.1875, 12.2188, 0.1250,
                12.3750, 12.1875, 12.3438, 0.1875,
                12.5000, 12.2812, 12.5000, 0.2188,
                12.5938, 12.3125, 12.3750, 0.2813,
                12.3438, 12.2812, 12.3438, 0.0938,
                12.4062, 12.2812, 12.3438, 0.1250,
                12.3750, 12.2812, 12.2812, 0.0938,
                12.4062, 12.2812, 12.3750, 0.1250,
                12.3750, 11.9688, 12.0938, 0.4062,
                12.2812, 12.0938, 12.1562, 0.1874,
                12.2500, 12.0000, 12.0625, 0.2500,
                12.0625, 11.6562, 11.9688, 0.4063,
                12.3125, 12.1562, 12.1875, 0.3437,
                12.3125, 12.1250, 12.1562, 0.1875,
            ],
            [
                ti.tr,
                "tr with missing data",
                3, 1, # data geometry
                4, # precision
                # Data
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2500, 12.1562, 12.1875, 0.0938,
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2812, 12.1250, 12.1875, 0.1562,
                12.3750, 12.1250, 12.3750, 0.2500,
                12.3750, 12.2812, 12.3125, 0.0938,
                12.3125,    None, 12.2188,   None,
                12.3750, 12.1875, 12.3438, 0.1875,
                12.5000, 12.2812, 12.5000, 0.2188,
                12.5938, 12.3125, 12.3750, 0.2813,
                12.3438, 12.2812, 12.3438, 0.0938,
                12.4062, 12.2812,    None, 0.1250,
                12.3750, 12.2812, 12.2812, 0.0938,
                12.4062, 12.2812, 12.3750, 0.1250,
                12.3750, 11.9688, 12.0938, 0.4062,
                   None, 12.0938, 12.1562,   None,
                12.2500, 12.0000, 12.0625, 0.2500,
                12.0625, 11.6562, 11.9688, 0.4063,
                12.3125, 12.1562, 12.1875, 0.3437,
                12.3125, 12.1250, 12.1562, 0.1875,
            ],
            #
            # Wilder's Smooting
            #
            [
                ti.wilders(5),
                "from 'Technical Analysis from A to Z, 2nd edition', p366",
                1, 1, # data geometry
                4, # precision
                # Data
                62.1250, None,
                61.1250, None,
                62.3438, None,
                65.3125, None,
                63.9688, 62.9750,
                63.4375, 63.0675,
                63.0000, 63.0540,
                63.7812, 63.1995,
                63.4062, 63.2408,
                63.4062, 63.2739,
                62.4375, 63.1066,
                61.8438, 62.8540,
            ],
            [
                ti.wilders(5),
                "from https://github.com/TulipCharts/tulipindicators/blob/master/tests/untest.txt",
                1, 1, # data geometry
                3, # precision
                # Data
                81.59, None,
                81.06, None,
                82.87, None,
                83.00, None,
                83.61, 82.426,
                83.15, 82.571,
                82.84, 82.625,
                83.99, 82.898,
                84.55, 83.228,
                84.36, 83.455,
                85.53, 83.870,
                86.54, 84.404,
                86.89, 84.901,
                87.77, 85.475,
                87.29, 85.838,
            ],
            [
                ti.wilders(5),
                "wilders with missing data",
                1, 1, # data geometry
                3, # precision
                # Data
                81.59, None,
                81.06, None,
                82.87, None,
                83.00, None,
                83.61, 82.426,
                83.15, 82.571,
                82.84, 82.625,
                None,  None,
                84.55, None,
                84.36, None,
                85.53, None,
                86.54, None,
                86.89, 85.574,
                87.77, 86.013,
                87.29, 86.269,
            ],
        ]
        #
        # End of definitions
        #

        for (fct, desc, input_size, output_size, precision, *data) in tests:
            # Split the data in columns
            total_size = input_size+output_size
            src = []
            for i in range(input_size):
                src.append(data[i::total_size])
            expected = []
            for i in range(input_size, total_size):
                expected.append(data[i::total_size])

            try:
                nrows = len(src[0])
            except IndexError:
                # Fallback in case we want to test zero-column expressions.
                nrows = 10

            with self.subTest(fct=fct, desc=desc):
                src = [Column.from_sequence(seq) for seq in src]
                serie = Serie.create(Column.from_sequence(range(nrows)))
                actual = [ fct(serie, *src) ]
                actual = [[x and round(x, precision) for x in col] for col in actual]
                self.assertSequenceEqual(actual, expected)

