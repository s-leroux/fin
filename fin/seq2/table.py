from fin.seq2 import serie
from fin.utils import formatters

DEFAULT_FORMATTER=formatters.StringLeftFormatter()
DEFAULT_CONTEXT=formatters.Context()

# ======================================================================
# Table class
# ======================================================================
class Table:
    """
    A representation of a Serie.

    XXX Possible rename this as "SerieFormatter".
    """
    def __init__(self, **kwargs):
        self._serie = None
        self._meta = []
        self._options = kwargs

    def append(self, newSerie, *, formatter=None, heading=None):
        """
        Register a new serie to be displayed as part of this table.
        """
        if self._serie is not None:
            index, left, right = newSerie.join(self._serie, newSerie)
        else:
            index, left, right = newSerie.index, (), newSerie.columns

        for c in right:
            fmt = formatter if formatter is not None else c.formatter
            if fmt is None:
                fmt = DEFAULT_FORMATTER

            self._meta.append(dict(
                heading=heading if heading is not None else c.name,
                formatter=fmt
                ))

        self._serie = serie.Serie(index, *(left + right))

    def prepare(self, context=None):
        """
        Prepare table by calling the formatter on each cell.
        """
        if self._serie is None:
            return () # Zero columns

        if context is None:
            context = DEFAULT_CONTEXT

        opt_heading = self._options.get("heading", True)

        columns = []
        heading = [] if not opt_heading else [ DEFAULT_FORMATTER(context, self._serie.index.name) ]
        columns.append(heading + [DEFAULT_FORMATTER(context, cell) for cell in self._serie.index])
        for column, meta in zip(self._serie.columns, self._meta):
            heading = [] if not opt_heading else [ DEFAULT_FORMATTER(context, meta["heading"]) ]

            columns.append(heading + [meta["formatter"](context, cell) for cell in column])

        return columns

    def __str__(self, context=None):
        lines = []
        for row in zip(*self.prepare(context)):
            lines.append(", ".join([t[0]+t[1]+t[2] for t in row]))

        return "\n".join(lines)
