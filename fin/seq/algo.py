""" Common algorithms usable on tables
"""
import math
import builtins

# ======================================================================
# Window functions
# ======================================================================
def window(fct, n):
    def _window(rowcount, *cols):
        i = n-1
        result = [None]*rowcount
        while i < rowcount:
            result[i] = fct(i-n+1, i+1, *cols)
            i += 1

        return result

    return _window

def naive_window(fct, n):
    def _fct(start, end, *cols):
        return fct(*[col[start:end] for col in cols])

    return window(_fct, n)

def by_row(fct):
    """
    Evaluates a function row by row on a list of columns.
    """
    def _by_row(rowcount, *cols):
        result = [None]*rowcount
        i = 0
        rows = zip(*cols)
        while i < rowcount:
            row = next(rows)
            try:
                result[i] = fct(*row)
            except Exception as e:
                result[i] = str(e) # ???
                pass
            i += 1

        return result

    return _by_row

def moving_average(n):
    return naive_window(lambda col:sum(col)/len(col), n)

def standard_deviation(n):
    sqrt = math.sqrt
    sum = builtins.sum
    a = 1.0/(n-1.0)
    b = a/n

    def s(rowcount, values):
        buffer = [0.0]*n
        sigma_ui = 0.0
        sigma_ui2 = 0.0
        ptr = 0
        nones = 0
        result = [None]*rowcount
        i = 0
        while i < n-1:
            x = values[i]
            buffer[i] = x
            if x is None:
                nones += 1
            else:
                sigma_ui += x
                sigma_ui2 += x*x

            i += 1

        ptr = i
        while True:
            x = values[i]
            buffer[ptr] = x
            if x is None:
                nones += 1
            else:
                sigma_ui += x
                sigma_ui2 += x*x

            if not nones:
                result[i] = sqrt(a*sigma_ui2 - b*sigma_ui*sigma_ui)

            i += 1
            if i == rowcount:
                break

            ptr += 1
            if ptr == n:
                ptr = 0
            x = buffer[ptr]
            if x is None:
                nones -= 1
            else:
                sigma_ui -= x
                sigma_ui2 -= x*x

        return result

    return s

def naive_standard_deviation(n):
    variance = naive_variance(n)
    sqrt = math.sqrt

    def _standard_deviation(rowcount, values):
        result = variance(rowcount, values)
        i = 0
        while i < rowcount:
            try:
                result[i] = sqrt(result[i])
            except TypeError:
                pass

            i+=1
        return result

    return _standard_deviation

def mean(n):
    """ The mean over a n-period window
    """
    def _mean(rowcount, values):
        result = [None]*rowcount
        cache = [None]*n
        nones = n
        ptr = 0

        acc = 0.0
        i = 0
        while i < rowcount:
            try:
                acc -= cache[ptr]
            except TypeError:
                nones -=1

            x = values[i]
            cache[ptr] = x
            ptr += 1
            if ptr == n:
                ptr = 0

            try:
                acc += x
                if not nones:
                    result[i] = acc/n
            except TypeError:
                nones += 1

            i += 1

        return result

    return _mean

def naive_variance(n):
    """ The variance over a n-periode time frame
    """
    sum = builtins.sum
    a = 1.0/(n-1.0)
    b = a/n

    def _variance(ui):
        ui_squared = [u*u for u in ui]
        s1 = sum(ui_squared)
        s2 = sum(ui)**2

        return a*s1-b*s2

    return naive_window(_variance, n)

def volatility(n, tau=1/252):
    """ The price volatility over a n-period window
    """
    stddev = standard_deviation(n)
    log = math.log
    k = math.sqrt(1/tau)
    vol = lambda stddev : stddev*k

    def _volatility(rowcount, values):
        ui = map1(lambda curr, prev: log(curr/prev))(rowcount, values)
        result = stddev(rowcount, ui)
        return map(vol)(rowcount, result)

    return _volatility

# ======================================================================
# Core functions
# ======================================================================
def constantly(value):
    """
    Evaluates to a list made of contant values.
    """
    def _constantly(rowcount):
        return [value]*rowcount

    return _constantly

def shift(n):
    """
    Shift a column by n periods.

    Sometimes called the "lag" operator.
    """
    def _shift(rowcount, values):
        if n > 0:
            return values[n:] + [None]*n
        else:
            return [None]*-n + values[:n]

    return _shift

def ratio(rowcount, a, b):
    """
    Evaluates to the line-by-line ratio of two columns.

    Formally, y_i = to a_i/b_i.
    """
    result = [None]*rowcount
    for idx, a_i, b_i in zip(range(rowcount), a, b):
        try:
            result[idx] = a_i/b_i
        except TypeError:
            # One value is probably None
            pass
        except ZeroDivisionError:
            # b_i is 0.0
            result[idx] = float("inf") if a_i > 0 else float("-inf") if a_i < 0 else None

    return result

def difference(fct, y0):
    """ Map data using a difference(1) function y_i = f(u_i, y_i-1)
    """
    def _difference(rowcount, values):
        pass

    return _difference

# ======================================================================
# Compound functions
# ======================================================================
def ratio_to_moving_average(n):
    ma = mean(n)

    def _ratio_to_moving_average(rowcount, a, b):
        b = ma(rowcount, b)
        return ratio(rowcount, a, b)

    return _ratio_to_moving_average

# ======================================================================
# Projections
# ======================================================================
def map(fct):
    """ Map data using y_i = f(u_i)
    """
    def _map(rowcount, values):
        result = [None]*rowcount
        i = rowcount
        while i:
            i -= 1
            x = values[i]
            result[i] = fct(x) if x is not None else None

        return result

    return _map

def mapn(fct):
    """ Map data using y_i = f(u_i0 .. u_in)
    """
    def _mapn(rowcount, *values):
        result = [None]*rowcount
        for i, row in enumerate(zip(*values)):
            try:
                result[i] = fct(*row)
            except TypeError:
                pass

        return result

    return _mapn

def map1(fct):
    """ Map data using y_i = f(u_i, u_i-1)
    """
    def _map(rowcount, values):
        result = [None]*rowcount
        prev = None

        for i, x in enumerate(values):
            if x is not None and prev is not None:
                result[i] = fct(x, prev)

            prev = x

        return result

    return _map

# ======================================================================
# Utilities
# ======================================================================
import fin.seq.table
named = lambda name : lambda rowcount, col : fin.seq.table.Table.Column(name, col.value)

# ======================================================================
# Calendar functions
# ======================================================================
from fin import datetime

def shift_date(years=0, months=0, days=0):
    """
    Offset a calendar date.
    """
    offset = datetime.CalendarDateDelta(years, months, days)

    def _shift_date(rowcount, dates):
        name = getattr(dates, "name", None)

        result = [None]*rowcount
        for idx, date in enumerate(dates):
            try:
                result[idx] = date+offset
            except ValueError:
                pass

        return fin.seq.table.Table.Column(name,result)

    return _shift_date
