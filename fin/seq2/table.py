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
    """
    def __init__(self):
        self._serie = None
        self._meta = []

    def append(self, newSerie, *, formatter=None, title=None):
        """
        Register a new serie to be displayed as part of this table.

        Only one-column series are currently supported.
        """
        if self._serie is not None:
            index, left, right = newSerie.join(self._serie, newSerie)
        else:
            index, left, right = newSerie.index, (), newSerie.columns

        # Check limitations
        if len(right) != 1:
            raise ValueError(f"Only 1-column series are supported ({len(right)} found)")

        if title is None:
            title = ""

        if formatter is None:
            formatter = DEFAULT_FORMATTER

        self._serie = serie.Serie(index, *(left + right))
        self._meta.append(dict(
            title=title,
            formatter=formatter,
            ))

    def __str__(self, context=None):
        if self._serie is None:
            return ""

        if context is None:
            context = DEFAULT_CONTEXT

        columns = []
        columns.append([DEFAULT_FORMATTER(context, cell) for cell in self._serie.index])
        for column, meta in zip(self._serie.columns, self._meta):
            columns.append([meta["formatter"](context, cell) for cell in column])

        rows = []
        for row in zip(*columns):
            rows.append(", ".join([t[0]+t[1]+t[2] for t in row]))

        return "\n".join(rows)
