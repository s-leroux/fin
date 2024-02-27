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

_str_formatter = StringRightFormatter()

class Tabular :
    """
    Display tabular data.

    Instances of this class store a 2d-array or formatted objects.
    This class is responsible for properly sizing the columns so formatted
    data can be nicely displayed.
    """
    def __init__(self, ncols):
        self._ncols = ncols
        self._cols = [(0,0)]*ncols
        self._rows = []

    def add_row(self, *data, formatters=None):
        """
        Add a new row to the tabular object.

        If `formatters` is None, `data` are asumed to be formatted,
        otherwise, data are formatter accordingly.
        """
        if formatters:
            data = [f(d) for f,d in zip(formatters, data)]

        if len(data) != self._ncols:
            raise ValueError(f"Wrong row size {len(data)}. Expected {self._ncols}")

        row = []
        for n, item in enumerate(data):
            text_before, sep, text_after, cell_length_before, cell_length_after = item
            max_before, max_after = self._cols[n]

            if cell_length_before > max_before:
                max_before = cell_length_before
            if cell_length_after > max_after:
                max_after = cell_length_after

            row.append((text_before, sep, text_after))
            self._cols[n] = (max_before, max_after)

        self._rows.append(row)

    def add_columns(self, *columns, formatters=None):
        for row in zip(*columns):
            self.add_row(*row, formatters=formatters)

    def content(self):
        cols = self._cols

        result = []
        for row in self._rows:
            curr = []
            result.append(curr)

            for (left_size, right_size), (left_text, sep, right_text) in zip(cols, row):
                curr.append(f"{left_text:>{left_size}}{sep}{right_text:<{right_size}}")

        return result

    def format(self, datamodel):
        fmt_columns = [] # the formmatted columns
        fmt_before = [] # the width of each column
        fmt_after = [] # the width of each column
        formaters = self._formatters

        for column, formatter in zip_longest(datamodel, self._formatters):
            if formatter is None:
                formatter = _str_formatter

            fmt_column = []
            max_before = 0
            max_after = 0
            for cell in column:
                text_before, sep, text_after, cell_length_before, cell_length_after = formatter(cell)
                if cell_length_before > max_before:
                    max_before = cell_length_before
                if cell_length_after > max_after:
                    max_after = cell_length_after
                fmt_column.append((text_before, sep, text_after))

            fmt_columns.append((max_before, max_after, fmt_column))

        return fmt_columns

    def to_rows(self, datamodel):
        fmt = self.format(datamodel)
        rows = []

        for left_size, right_size, column in fmt:
            idx = 0
            for left_text, sep, right_text in column:
                try:
                    row = rows[idx]
                except IndexError:
                    row = []
                    rows.append(row)

                row.append(f"{left_text:>{left_size}}{sep}{right_text:<{right_size}}")
                idx += 1

        return rows

    def to_string(self):
        rows = self.content()
        return "\n".join([" | ".join(row) for row in rows])

