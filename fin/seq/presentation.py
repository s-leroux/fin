from fin.seq import serie
from fin.utils import formatters

DEFAULT_FORMATTER=formatters.StringLeftFormatter()
DEFAULT_CONTEXT=formatters.Context()

# ======================================================================
# Presentation class
# ======================================================================
class Presentation:
    """
    A representation of a Serie.

    XXX Possible rename this as "SerieFormatter".
    """
    def __init__(self, **kwargs):
        self._options = kwargs

    def prepare(self, serie, context):
        """
        Prepare table by calling the formatter on each cell.

        This is a low-level function for sub-classes implementators.
        It assumes the context parameter is not None.
        """
        if serie is None:
            raise ValueError("The serie parameter can't be None")
        if context is None:
            raise ValueError("The context parameter can't be None")

        opt_heading = self._options.get("heading", True)

        columns = []
        heading = [] if not opt_heading else [ DEFAULT_FORMATTER(context, serie.index.name) ]
        columns.append(heading + [DEFAULT_FORMATTER(context, cell) for cell in serie.index])
        for column in serie.columns:
            heading = [] if not opt_heading else [ DEFAULT_FORMATTER(context, column.name) ]
            formatter = column.formatter
            if formatter is None:
                formatter = DEFAULT_FORMATTER

            columns.append(heading + [formatter(context, cell) for cell in column])

        return columns

    def __call__(self, serie, context=None):
        if context is None:
            context = DEFAULT_CONTEXT

        lines = []
        for row in zip(*self.prepare(serie, context)):
            lines.append(", ".join([t[0]+t[1]+t[2] for t in row]))

        return "\n".join(lines)
