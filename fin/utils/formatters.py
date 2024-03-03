from itertools import zip_longest

from fin.utils import termcap

class FloatFormatter:
    def __init__(self, *, digits=8, precision=2):
        self._digits = digits
        self._precision = precision

    def __call__(self, number):
        number = float(number)
        left, right = f"{number:{self._digits}.{self._precision}f}".split(".")
        return (left, ".", right, len(left), len(right))

class PercentFormatter(FloatFormatter):
    def __call__(self, number):
        left, sep, right, llen, rlen = FloatFormatter.__call__(self, number*100.0)
        return (left, sep, right+"%", llen, rlen+1)

class ColorFloatFormatter(FloatFormatter):
    def __init__(self, *args, tc=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._termcap = tc

    def __call__(self, number):
        number = float(number)
        left, sep, right, llen, rlen = FloatFormatter.__call__(self, number)

        if number < 0:
            color = self._termcap.red
        elif number > 0:
            color = self._termcap.green
        else:
            color = lambda x : x

        return (color(left), color(sep), color(right), llen, rlen)

class StringLeftFormatter:
    def __call__(self, string):
        """
        The default formatter.
        """
        result = str(string)
        return ("", "", result, 0, len(result))

class StringRightFormatter:
    def __call__(self, string):
        """
        The default formatter.
        """
        result = str(string)
        return (result,  "", "", len(result), 0)
