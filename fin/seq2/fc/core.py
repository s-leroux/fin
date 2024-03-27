import builtins

from fin.seq2.column import Column

# ======================================================================
# Core functions
# ======================================================================
def constant(n, **kwargs):
    """
    Evaluates to a function returning a constant column.
    """
    def _sequence(serie):
        return Column.from_constant(serie.rowcount, n)

    return _sequence

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
    def _named(serie):
        return serie[spec]

    return _named

def named(new_name):
    """
    Evaluates to a function that changes the name of a column.
    """
    def _named(serie, column):
        return column.rename(new_name)

    return _named

def shift(n):
    """
    Evaluate to a function that shift the values in a column.

    Sometimes called the "lag" operator.
    """
    # XXX This should accept to multiple columns!
    def _shift(serie, values):
        return values.shift(n)

    return _shift

