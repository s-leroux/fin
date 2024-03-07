from fin.utils import termcap

class Context(dict):
    def __init__(self, **kwargs):
        self['termcap'] = kwargs.get('termcap') or termcap.TermCap()

    @staticmethod
    def for_stdout():
        return Context(
            termcap=termcap.TermCap.for_stdout(),
        )

def compose(parent, child):
    def _format(context, obj):
        return child(context, obj, parent)

    return _format

class ComposableFormatter:
    def __add__(self, child):
        return compose(self, child)

class ColorFormatter(ComposableFormatter):
    def __init__(self, color):
        self._color = color

    def __call__(self, context, obj, parent):
        tc = context['termcap']

        left, sep, right, llen, rlen = parent(context, obj)

        if tc is not None:
            color = getattr(tc, self._color)
        else:
            color = lambda x : x

        return (color(left), color(sep), color(right), llen, rlen)

def Red():
    return ColorFormatter('red')

def Yellow():
    return ColorFormatter('yellow')

def Green():
    return ColorFormatter('green')

def Gray():
    return ColorFormatter('gray')

class FloatFormatter(ComposableFormatter):
    def __init__(self, *, precision=2):
        self._precision = precision

    def __call__(self, context, number):
        number = float(number)
        left, right = f"{number:.{self._precision}f}".split(".")
        return (left, ".", right, len(left), len(right))

class PercentFormatter(FloatFormatter):
    def __call__(self, context, number):
        left, sep, right, llen, rlen = FloatFormatter.__call__(self, context, number*100.0)
        return (left, sep, right+"%", llen, rlen+1)

class ColorFloatFormatter(FloatFormatter):
    def __call__(self, context, number):
        number = float(number)
        left, sep, right, llen, rlen = FloatFormatter.__call__(self, context, number)

        tc = context['termcap']
        if number < 0:
            color = tc.red
        elif number > 0:
            color = tc.green
        else:
            color = lambda x : x

        return (color(left), color(sep), color(right), llen, rlen)

class StringLeftFormatter(ComposableFormatter):
    def __call__(self, context, string):
        result = str(string)
        return ("", "", result, 0, len(result))

class StringRightFormatter(ComposableFormatter):
    def __call__(self, context, string):
        result = str(string)
        return (result,  "", "", len(result), 0)
