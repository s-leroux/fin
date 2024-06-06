from fin.seq.column import Column

from fin.seq.fc.windowx import *

# ======================================================================
# Window functions
# ======================================================================
def window(fct, n):
    def _window(serie, *cols):
        rowcount = serie.rowcount
        i = n-1
        result = [None]*rowcount
        while i < rowcount:
            result[i] = fct(i-n+1, i+1, *cols)
            i += 1

        return Column.from_sequence(result)

    return _window

def naive_window(fct, n):
    def _fct(start, end, *cols):
        return fct(*[col[start:end] for col in cols])

    return window(_fct, n)

