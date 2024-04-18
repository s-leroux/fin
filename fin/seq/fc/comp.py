from fin.seq.column import Column
from fin.seq.coltypes import Ternary

# ======================================================================
# Comparison functions
# ======================================================================
def lt(serie, *cols):
    """
    Evaluates to True if all values in a row are sorted in ascending order.
    """
    if len(cols) < 1:
        result = (True,)*serie.rowcount
    else:
        result = []
        store = result.append

        for row in zip(*cols):
            it = iter(row)
            prev = next(it)
            if prev is None:
                t = None
            else:
                for curr in it:
                    if curr is None:
                        t = None
                        break
                    elif not prev < curr:
                        t = False
                        break
                    prev = curr
                else:
                    t = True

            store(t)

    return Column.from_sequence(
            result,
            name="(lt,"+",".join([col.name for col in cols])+")",
            type=Ternary()
        )

def gt(serie, *cols):
    """
    Evaluates to True if all values in a row are sorted in descending order.
    """
    if len(cols) < 1:
        result = (True,)*serie.rowcount
    else:
        result = []
        store = result.append

        for row in zip(*cols):
            it = iter(row)
            prev = next(it)
            if prev is None:
                t = None
            else:
                for curr in it:
                    if curr is None:
                        t = None
                        break
                    elif not prev > curr:
                        t = False
                        break
                    prev = curr
                else:
                    t = True

            store(t)

    return Column.from_sequence(
            result,
            name="(gt,"+",".join([col.name for col in cols])+")",
            type=Ternary()
        )

