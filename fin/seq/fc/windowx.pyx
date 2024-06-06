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

