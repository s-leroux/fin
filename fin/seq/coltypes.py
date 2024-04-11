import sys

from fin.utils.log import console
from fin.utils import formatters

# ======================================================================
# Utilities
# ======================================================================
def _parse_string_sequence(sequence, converter):
    result = []
    push = result.append

    for item in sequence:
        try:
            item = converter(item)
        except:
            e = sys.exc_info()[1] # This will also catch an exception that doesn't inherit from Exception
            console.warn(f"Can't convert {item} using {converter}")
            console.info(str(e))
            item = None

        push(item)

    return tuple(result)

# ======================================================================
# Types
# ======================================================================
class Type:
    def __init__(self, **kwargs):
        self._options = kwargs

    def formatter(self, column):
        try:
            return self._formatter
        except AttributeError:
            self._formatter = formatter = self.new_formatter_for(column)
            return formatter

    def new_formatter_for(self, column):
        return formatters.StringLeftFormatter()


    def parse_string_sequence(self, sequence):
        """ Convert from a sequence of string to a tuple of the receiver's type instances.
        """
        return tuple(sequence)


def _infer_precision_from_data(column):
    precision = 2
    for cell in column:
        if type(cell) is str:
            precision = max(precision, cell.rfind("."))

    return precision
class Float(Type):
    """ The type for a column containing floating-point numbers.

        This type support the following options:
        - precision:
            The number of digits after the decimal separator when converting
            to a string.
    """
    def new_formatter_for(self, column):
        try:
            precision = self._options["precision"]
        except KeyError:
            precision = _infer_precision_from_data(column)

        return formatters.FloatFormatter(precision=precision)

    def parse_string_sequence(self, sequence):
        return _parse_string_sequence(sequence, float)

class Integer(Type):
    """ The type for a column containing integer numbers.
    """
    def new_formatter_for(self, column):
        return formatters.IntegerFormatter()

    def parse_string_sequence(self, sequence):
        return _parse_string_sequence(sequence, int)

class Other(Type):
    """ The default type for columns.

        This type support the following options:
        - from_string:
            A function to convert from a string to the most meaningful format for
            this type of data..
    """
    def parse_string_sequence(self, sequence):
        try:
            converter = self._options["from_string"]
        except KeyError:
            return super().parse_string_sequence(sequence)

        return _parse_string_sequence(sequence, converter)

Date = Other
DateTime = Other
