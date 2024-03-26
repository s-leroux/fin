from fin.seq2.column import Column

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

