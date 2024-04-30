import builtins

from fin.seq.column import Column

from cpython.ref cimport PyObject

from fin.mem cimport alloca
from fin.seq.column cimport Column
from fin.seq.serie cimport Serie

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

def named(new_name):
    """
    Evaluates to a function that changes the name of a column.
    """
    def _named(serie, column):
        return column.rename(new_name)

    return _named

def rownum(serie):
    return Column.from_sequence(builtins.range(serie.rowcount), type="i")

def coalesce(Serie serie, *cols):
    cdef unsigned n = serie.rowcount
    cdef unsigned l = len(cols)
    cdef PyObject ***cols_ptr = <PyObject***>alloca(l*sizeof(PyObject**))
    cdef Column col
    cdef unsigned i
    for i, col in enumerate(cols):
        cols_ptr[i] = col.get_py_values()._base_ptr

    cdef list result = []
    cdef PyObject *it
    cdef PyObject *none_ptr = <PyObject*>None

    cdef unsigned j = 0
    while j < n:
        i = 0
        it = none_ptr
        while i<l:
            if cols_ptr[i][j] != none_ptr:
                it = cols_ptr[i][j]
                break
            i += 1

        assert it != NULL
        result.append(<object>it)
        j += 1

    return Column.from_sequence(result)

def shift(n):
    """
    Evaluate to a function that shift the values in a column.

    Sometimes called the "lag" operator.
    """
    # XXX This should accept to multiple columns!
    def _shift(serie, values):
        return values.shift(n)

    return _shift

