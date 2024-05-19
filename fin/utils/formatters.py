from fin.utils import termcap
from fin.datetime import asCalendarDate

# ======================================================================
# Context
# ======================================================================
class Context(dict):
    def __init__(self, **kwargs):
        self['termcap'] = kwargs.get('termcap') or termcap.TermCap()

    @staticmethod
    def for_stdout():
        return Context(
            termcap=termcap.TermCap.for_stdout(),
        )

# ======================================================================
# Composable formatters
# ======================================================================
def compose(parent, child):
    def _format(context, obj):
        return child(context, obj, parent)

    return _format

class ComposableFormatter:
    def __add__(self, child):
        return compose(self, child)

# ======================================================================
# Color formatters
# ======================================================================
class ColorFormatter(ComposableFormatter):
    def __init__(self, color):
        self._color = color

    def __call__(self, context, obj, parent):
        tc = context['termcap']

        text, llen, rlen = parent(context, obj)

        if tc is not None:
            color = getattr(tc, self._color)
        else:
            color = lambda x : x

        return (color(text), llen, rlen)

def Red():
    return ColorFormatter('red')

def Yellow():
    return ColorFormatter('yellow')

def Green():
    return ColorFormatter('green')

def Gray():
    return ColorFormatter('gray')

# ======================================================================
# Float formatters
# ======================================================================
class FloatFormatter(ComposableFormatter):
    def __init__(self, *, precision=2):
        self._precision = precision

    def __call__(self, context, number):
        try:
            number = float(number)
        except TypeError:
            return (str(number), 0, 0)

        text = f"{number:.{self._precision}f}"
        dp_idx = text.find(".")
        if dp_idx < 0:
            llen = len(text)
            rlen = 0
        else:
            llen = dp_idx
            rlen = len(text)-dp_idx

        return (text, llen, rlen)

class PercentFormatter(FloatFormatter):
    def __call__(self, context, number):
        text, llen, rlen = FloatFormatter.__call__(self, context, number*100.0)
        return (text+"%", llen, rlen+1)

class ColorFloatFormatter(FloatFormatter):
    def __call__(self, context, number):
        number = float(number)
        text, llen, rlen = FloatFormatter.__call__(self, context, number)

        tc = context['termcap']
        if number < 0:
            color = tc.red
        elif number > 0:
            color = tc.green
        else:
            color = lambda x : x

        return (color(text), llen, rlen)

# ======================================================================
# Ternary value formatter
# ======================================================================
class TernaryFormatter(ComposableFormatter):
    def __init__(self, *, true, false, none):
        self._true = true
        self._false = false
        self._none = none

    def __call__(self, context, value):
        if value is True:
            text = self._true
        elif value is False:
            text = self._false
        elif value is None:
            text = self._none
        else:
            raise ValueError(f"Ternary logic value expected, found {value!r}")

        return (text, len(text), 0)

# ======================================================================
# String formatters
# ======================================================================
class StringLeftFormatter(ComposableFormatter):
    def __call__(self, context, string):
        result = str(string)
        return (result, 0, len(result))

class StringRightFormatter(ComposableFormatter):
    def __call__(self, context, string):
        result = str(string)
        return (result, len(result), 0)

# ======================================================================
# DateTime formatters
# ======================================================================
class DateTimeFormatter(ComposableFormatter):
    def __init__(self, *, format=None):
        self._format = format

    def __call__(self, context, date):
        try:
            date = asCalendarDate(date)
        except:
            return (str(date), 0, 0)

        fmt = self._format
        if fmt is not None:
            text = date.format(self._format)
        else:
            test = str(date)

        return (text, len(text), 0)

IntegerFormatter = StringRightFormatter

