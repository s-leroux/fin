from fin.seq.column import Column

from fin.seq.fc import windows

# ======================================================================
# Greeks
# ======================================================================
def delta(n=1):
    """
    Compute the Rate Of Change of a series over a period of time.

    Formally, y_i = x_i - x_(i-n).
    """
    def _delta(serie, x):
        rowcount = serie.rowcount
        #
        # According to timeit, this is the fastest algorithm I could find
        #
        result = []
        store = result.append
        it = iter(x)
        jt = iter(x)

        # Consume the n first items
        for _ in range(n):
            store(None)
            next(it)

        # Remaining of the list
        for i, j in zip(it, jt):
            try:
                store(i-j)
            except TypeError:
                store(None)

        return Column.from_sequence(result)

    return _delta

def beta(n):
    """
    Compute the Beta between two columns over a n-period windows.
    """
    def _beta(col_x, col_y):
        try:
            x_bar = sum(col_x)/n
            y_bar = sum(col_y)/n
        except TypeError:
            return None

        covar = [(x-x_bar)*(y-y_bar) for x, y in zip(col_x, col_y)]
        var = [(x-x_bar)**2 for x in col_x]
        return sum(covar)/sum(var)
    return windows.naive_window(_beta, n)

def alpha(n):
    """
    Compute the Alpha between two columns over a n-period windows.
    """
    def _alpha(col_x, col_y):
        try:
            x_bar = sum(col_x)/n
            y_bar = sum(col_y)/n
        except TypeError:
            return None

        covar = [(x-x_bar)*(y-y_bar) for x, y in zip(col_x, col_y)]
        var = [(x-x_bar)**2 for x in col_x]
        return y_bar - x_bar*sum(covar)/sum(var)
    return windows.naive_window(_alpha, n)


