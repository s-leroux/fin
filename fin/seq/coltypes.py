from fin.utils import formatters

# ======================================================================
# Types
# ======================================================================
class Type:
    def formatter(self, column):
        try:
            return self._formatter
        except AttributeError:
            self._formatter = formatter = self.new_formatter_for(column)
            return formatter

class Float(Type):
    """ The type for a column containing floating-point numbers.
    """
    def __init__(self, **kwargs):
        self._options = kwargs

    def new_formatter_for(self, column):
        try:
            precision = self._options["precision"]
        except KeyError:
            precision = 2 # XXX We should infer that value from the column

        return formatters.FloatFormatter(precision=precision)

class Other(Type):
    """ The default type for columns.
    """
    def new_formatter_for(self, column):
        return formatters.StringLeftFormatter()

Date = Other
DateTime = Other
