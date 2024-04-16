import builtins

from fin.seq.column import Column

# ======================================================================
# Core functions
# ======================================================================
def constant(n, **kwargs):
    """
    Evaluates to a function returning a constant column.
    """
    def _constant(serie):
        return Column.from_constant(serie.rowcount, n)

    return _constant

def sequence(seq, **kwargs):
    """
    Evaluates to a function returning a sequence.

    Sequence length is not checked against serie.rowcount to allow
    this function use for the index parameter in Serie.create().
    """
    def _sequence(serie):
        return Column.from_sequence(seq, **kwargs)

    return _sequence

def range(*args):
    """
    Evaluates to a function returning a range.

    Shorthand for `fc.sequence(range(...))`
    """
    def _range(serie):
        return Column.from_sequence(builtins.range(*args))

    return _range

def get(spec):
    """
    Evaluates to a function returning a sub-set of the serie columns.
    """
    def _get(serie):
        return serie[spec]

    return _get

def all(serie):
    """
    Evaluates to the whole list of columns in the context.

    Think of this like the star(`*`) in an SQL statement `SELECT * FROM ...`.
    """
    return serie.columns # Or serie[:] ?


def named(new_name):
    """
    Evaluates to a function that changes the name of a column.
    """
    def _named(serie, column):
        return column.rename(new_name)

    return _named

def rownum(serie):
    return Column.from_sequence(builtins.range(serie.rowcount), type="i")

def shift(n):
    """
    Evaluate to a function that shift the values in a column.

    Sometimes called the "lag" operator.
    """
    # XXX This should accept to multiple columns!
    def _shift(serie, values):
        return values.shift(n)

    return _shift

