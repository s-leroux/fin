from fin.seq.column import Column

from . import core

# ======================================================================
# Projections
# ======================================================================
def map(fct):
    """
    Map data using y_i = f(u_i0 .. u_in)
    """
    def _map(serie, *values):
        result = []
        push = result.append
        for i, row in enumerate(zip(*values)):
            try:
                push(fct(*row) if None not in row else None)
            except TypeError:
                push(None)

        return Column.from_sequence(result)

    return _map

def map_change(fct):
    """
    Map data using y_i = f(u_i, u_i-1)
    """
    # XXX Rename this as delta_map ?
    def _map(serie, values):
        rowcount = serie.rowcount
        result = [None]*rowcount
        prev = None

        for i, x in enumerate(values):
            if x is not None and prev is not None:
                result[i] = fct(x, prev)

            prev = x

        return Column.from_sequence(result)

    return _map

def thread(fct, n):
    """ Thread a function over a subset of the arguments.

        Modeled from https://reference.wolfram.com/language/ref/Thread.html
        See https://github.com/s-leroux/fin/issues/3
    """
    if n <= 0:
        raise ValueError(f"Tread does not yet support n < 0")

    def _thread(serie, *args):
        return tuple( (core.named(x.name), fct, x, args[n:]) for x in args[:n] )

    return _thread
