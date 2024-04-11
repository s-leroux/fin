import math

from .statx import *

from fin.seq.column import Column
from fin.seq.fc.windows import naive_window
from fin.seq.fc import projections

# ======================================================================
# Statistics
# ======================================================================
def correlation(n):
    """
    Compute the Linear correlation between two columns over a n-period window.
    """
    sqrt = math.sqrt

    def _correlation(col_x, col_y):
        try:
            x_bar = sum(col_x)/n
            y_bar = sum(col_y)/n
        except TypeError:
            return None

        covar = [(x-x_bar)*(y-y_bar) for x, y in zip(col_x, col_y)]
        x_minus_x_bar = [(x-x_bar)**2 for x in col_x]
        y_minus_y_bar = [(y-y_bar)**2 for y in col_y]
        return sum(covar)/(sqrt(sum(x_minus_x_bar))*sqrt(sum(y_minus_y_bar)))
    return naive_window(_correlation, n)

def volatility(n, tau=1/252):
    """
    Compute the Annualized Historical Volatility over a n-period window.

    In practice this is the standard deviation of the day-to-day return.

    Parameters:
        n: the number of periods in the window. Often 20 or 21 for dayly data
            (corresponding to the number of trading days in one month)
        tau: inverse of the number of periods in one year
    """
    stddev = stdev.s(n)
    log = math.log
    k = math.sqrt(1/tau)
    vol = lambda stddev : stddev*k

    def _volatility(serie, values):
        rowcount = serie.rowcount
        # 1. Continuously compounded return for each period
        ui = projections.map_change(lambda curr, prev: log(curr/prev))(serie, values)
        # 2. Standard deviation
        result = stddev(serie, ui)
        # 3. Annualized values
        return projections.map(vol)(serie, result)

    return _volatility

def basic_sharpe_ratio(n):
    """
    Compute the Sharpe Ratio ignoring risk free return over a n-period window.
    """
    stddev = stdev.s(n)

    def _basic_sharpe_ratio(serie, values):
        rowcount = serie.rowcount
        s = iter(stddev(rowcount, values))
        result = [None]*(n-1)
        push = result.append

        i = iter(values)
        for _, _, _ in zip(range(n-1), i, s):
            pass

        j = iter(values)
        for x_i, x_j, s_i in zip(i, j, s):
            try:
                ret = (x_i - x_j) # TODO replace by average daily return
                push(ret/s_i)
            except TypeError:
                push(None)

        return Column.from_sequence(result, name=f"BSHARPE({n}), {values.name}")


    return _basic_sharpe_ratio

def best_fit(serie, col_x, col_y):
    rowcount = serie.rowcount
    """
    Compute the Linear Best Fit over the full dataset.
    """
    tx = []
    ty = []
    for x, y in zip(col_x, col_y):
        if x is not None and y is not None:
            tx.append(x)
            ty.append(y)

    x_bar = sum(tx)/len(tx)
    y_bar = sum(ty)/len(ty)

    covar = var = 0.0
    for x, y in zip(tx, ty):
        x_minus_x_bar = x-x_bar
        y_minus_y_bar = y-y_bar
        covar += x_minus_x_bar*y_minus_y_bar
        var += x_minus_x_bar*x_minus_x_bar

    beta = covar/var
    alpha = y_bar-x_bar*beta

    result = [None]*rowcount
    for i, x, in enumerate(col_x):
        try:
            result[i] = alpha+beta*x
        except TypeError:
            pass

    return Column.from_sequence(result, name=f"BESTFIT, {col_y.name}:{col_x.name}")


