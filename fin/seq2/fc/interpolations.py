import bisect

from fin.seq2.column import Column

# ======================================================================
# Utilities
# ======================================================================
def _index(col, x, *, bsearch=bisect.bisect_left):
    """
    Return the index of x in col, assuming col is sorted is ascending order.
    """
    idx = bsearch(col, x)
    if idx == len(col) or col[idx] != x:
        raise ValueError

    return idx

# ======================================================================
# Interpolation
# ======================================================================
def line(x1, x2):
    """
    Compute the line passing by (x1, y1_x1) and (x2, y2_x2).
    """
    def _line(serie, x_col, y1_col, y2_col=None):
        rowcount = serie.rowcount
        if y2_col is None:
            y2_col = y1_col

        x1_idx = _index(x_col, x1)
        x2_idx = _index(x_col, x2)
        y1 = y1_col[x1_idx]
        y2 = y2_col[x2_idx]

        if y1 is None or y2 is None:
            return [None]*rowcount

        # y = a+bx
        b = (y2-y1)/(x2_idx-x1_idx)
        a = y1-b*x1_idx
        result = []
        push = result.append

        for i in range(rowcount):
            push(a+b*i)

        return Column.from_sequence(result)

    return _line

