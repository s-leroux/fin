""" Common algorithms usable on tables
"""
import math
import builtins

# ======================================================================
# Adapters
# ======================================================================
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

# ======================================================================
# Accumulator
# ======================================================================
def acc(value, neg=False, pos=True):
    """
    Increase the running value when pos is true, decrease it when neg is true.
    """
    def _acc(rowcount, value, neg, pos):
        result = [None]*rowcount
        a = 0.0

        for i, (vi, ni, pi) in enumerate(zip(value, neg, pos)):
            if pi:
                a += vi
            if ni:
                a -= vi

            result[i] = a

        return result

    return (_acc, value, neg, pos)

def acc2(value, buy, sell):
    """
    Simulate an investor that can buy and sell one share.

    The investor can only sell when it owns a share.
    """
    def _acc(rowcount, value, buy, sell):
        result = [None]*rowcount
        share = 0
        cash = 0
        a = 0

        for i, (v, b, s) in enumerate(zip(value, buy, sell)):
            if b and not share:
                share = 1
                cash -= v
            if s and share:
                share = 0
                cash += v

            result[i] = share*v+cash

        return result

    return (_acc, value, buy, sell)

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

def moving_average(n):
    return naive_window(lambda col:sum(col)/len(col), n)

def standard_deviation(n):
    sqrt = math.sqrt
    sum = builtins.sum
    a = 1.0/(n-1.0)
    b = a/n

    def s(rowcount, values):
        sigma_ui = 0.0
        sigma_ui2 = 0.0
        buffer = [None]*n
        nones = n
        ptr = 0
        result = [None]*rowcount

        for i, v in enumerate(values):
            x = buffer[ptr]
            if x is None:
                nones -= 1
            else:
                sigma_ui -= x
                sigma_ui2 -= x*x

            buffer[ptr] = v
            if v is None:
                nones += 1
            else:
                sigma_ui += v
                sigma_ui2 += v*v

            if not nones:
                result[i] = sqrt(a*sigma_ui2 - b*sigma_ui*sigma_ui)

            ptr += 1
            if ptr == n:
                ptr = 0

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
# Linear trend
# ======================================================================
def linear_trend(rowcount, values):
    """
    Compute the linear trend over the full dataset.
    """
    sigma_y = sigma_xy = sigma_xx = 0.0
    sigma_x = 0.0
    n = 0
    d = (len(values)-1) / 2.0
    print(rowcount, len(values), d)
    for i, value in enumerate(values):
        try:
            x = i-d # ensure ∑x = 0
            sigma_x += x
            print(i, x, sigma_x)
            sigma_y += value
            sigma_xy += x*value
            sigma_xx += x*x
            n += 1
        except TypeError:
            pass

    print(sigma_x, sigma_y, sigma_xx, sigma_xy)
    result = [None]*rowcount

    try:
        a = sigma_xy / sigma_xx
        b = sigma_y / n
        print("a,b = ", a, b)
    except (ZeroDivisionError, TypeError):
        pass
    else:
        for i in range(rowcount):
            x = i-d
            try:
                result[i] = a*x + b
            except TypeError:
                pass

    return result


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

def change(n=1):
    """
    Evaluates to the difference between the current value and the value n periods
    earlier.

    Formally, y_i = x_i - x_(i-n).
    """
    def _change(rowcount, x):
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

        return result

    return _change

# ======================================================================
# Compound functions
# ======================================================================
def ratio_to_moving_average(n):
    ma = mean(n)

    def _ratio_to_moving_average(rowcount, a):
        b = ma(rowcount, a)
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
# Calendar functions
# ======================================================================
import fin.seq.table
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

        return fin.seq.table.Column(name,result)

    return _shift_date

def hist2(f, n, interval):
    """
    Apply a function to data et recuring intervals
    """
    assert interval > 0
    def _hist(rowcount, data):
        result = [None]*rowcount
        for i, value in enumerate(data):
            if i < interval:
                result[i] = []
            else:
                result[i] = [value] + result[i-interval][:n]

        result = builtins.map(f, result)
        return result

    return _hist

def hist(f, n, years=0, months=0, days=0):
    """
    Apply a function to data at recuring intervals.
    """
    offset = datetime.CalendarDateDelta(years, months, days)
    def _hist(rowcount, dates, data):
        # First, build an index from date to row number:
        index = { date: idx for idx, date in enumerate(dates) }

        # Then build a mapping from one date to the preceeding period.
        translation = {}
        previous = None
        for date in dates:
            print(date, offset, date+offset, date+offset in index)
            try:
                other = date+offset
            except ValueError:
                continue

            # Map a date to its preceeding period if it exists,
            # else, use the closest matching date
            if other in index:
                translation[date] = other
                previous = other
            else:
                translation[date] = previous
        print(translation)

        # Now, for each date, build a vector of the values at recuring intervals
        result = [None]*rowcount
        for i, date in enumerate(dates):
            print(date, end=' ')
            v = []
            for j in range(n):
                idx = index.get(date, None)
                v.append(data[idx] if idx is not None else None)
                date = translation.get(date, None)
                if date is None:
                    break
            result[i] = f(v)
            print()

        return result

    return _hist
