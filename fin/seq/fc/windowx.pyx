from fin.seq.serie cimport Serie
from fin.seq.column cimport Column
from fin.seq.ag.corex cimport CAggregateFunction

def aggregate_over(CAggregateFunction ag, unsigned n):
    """ Bridge between aggregate functions and window functions.
    """
    def _aggregate_over(Serie serie, Column col):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned i = n-1
        cdef list result = [ None ]*min(i, rowcount)

        while i < rowcount:
            i += 1
            result.append(ag.eval(col, i-n ,i))

        return Column.from_sequence(result, type=ag.type_for(col))

    return _aggregate_over

def cumulate(CAggregateFunction ag, unsigned _n_max=0):
    """ Cumulative application of the given function.

        This is very close to aggregate_over, but here the window's size growth
        from 1 to n_max, avoiding the sequence of `None` elements at the start of the result.

        If `_n_max` is 0, it will be set to `serie.rowcount`.
    """
    def _cumulate(Serie serie, Column col):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned n_max = rowcount if _n_max == 0 else _n_max
        cdef unsigned n = 1
        cdef unsigned i = 0
        cdef list result = []

        while i < rowcount:
            i += 1
            result.append(ag.eval(col, i-n, i))
            if n < n_max:
                n+=1

        return Column.from_sequence(result, type=ag.type_for(col))

    return _cumulate
