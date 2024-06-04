from fin.seq import serie
from fin.utils import formatters

DEFAULT_FORMATTER=formatters.StringRightFormatter()
DEFAULT_CONTEXT=formatters.Context()

def CSVFormatter(heading, columns, context, options):
    lines = []
    delimiter = options.get("delimiter", ", ")
    lines.append(delimiter.join([t for t, *_ in heading]))
    for row in zip(*columns):
        lines.append(delimiter.join([t for t, *_ in row]))

    return "\n".join(lines)+"\n"

def justify(text, llen, rlen, llen_max, rlen_max):
    """
    Clip the text or add spaces so it fits exactly into a `llen+rlen` character width string.

    The string is assumed to not contain newlines.
    """
    text = (llen_max-llen)*" " + text + (rlen_max-rlen)*" "
    width_max = llen_max+rlen_max

    while len(text) > width_max and text[0] == " ":
        text = text[1:]

    while len(text) > width_max and text[-1] == " ":
        text = text[:-1]

    # FIXME This can break escape sequences!
    if len(text) > width_max:
        return text[:width_max-1] + "…"

    return text

def TabularFormatter(heading, columns, context, options):
    width = []

    for column in columns:
        llen_max = 0 # left spacing
        rlen_max = 0 # right spacing

        for _, llen, rlen in column:
            llen_max = max(llen_max, llen)
            rlen_max = max(rlen_max, rlen)

        width.append((llen_max,rlen_max))

    col_sep = options.get("column-separator"," | ")
    heading_sep = options.get("heading-separator","-")

    lines = []
    if options.get("heading", True):
        line = []
        for (llen_max, rlen_max), cell in zip(width, heading):
            line.append(justify(*cell, llen_max, rlen_max))
        lines.append(col_sep.join(line))

        if heading_sep:
            line = []
            for llen_max,rlen_max in width:
                sep = ""
                while len(sep) < llen_max+rlen_max:
                    sep += heading_sep
                sep = sep[:llen_max+rlen_max]
                line.append(sep)

            lines.append(col_sep.join(line))

    for row in zip(*columns):
        line = []
        for (llen_max,rlen_max), cell in zip(width, row):
            line.append(justify(*cell, llen_max, rlen_max))
        lines.append(col_sep.join(line))

    return "\n".join(lines)


PRESENTATIONS = {
    "CSV": CSVFormatter,
    "TABULAR": TabularFormatter,
}

# ======================================================================
# Presentation class
# ======================================================================
class Presentation:
    """
    A representation of a Serie.

    XXX Possible rename this as "SerieFormatter".
    """
    def __init__(self, format="TABULAR", **kwargs):
        if not callable(format):
            format = PRESENTATIONS[format]

        self._format = format
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
        columns.append([DEFAULT_FORMATTER(context, cell) for cell in serie.index])
        for column in serie.data:
            if opt_heading:
                heading.append(DEFAULT_FORMATTER(context, column.name))

            columns.append(column.format(context))

        return heading, columns

    def __call__(self, serie, context=None):
        if context is None:
            context = DEFAULT_CONTEXT

        heading, columns = self.prepare(serie, context)
        return self._format(heading, columns, context, self._options)

