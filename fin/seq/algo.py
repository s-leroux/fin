""" Common algorithms usable on tables
"""
import math
import builtins
import bisect
from collections import deque

from fin.utils.log import console

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

# ======================================================================
# Technical indicator
# ======================================================================
def sma(n):
    """
    Compute the Simple Moving Average over a n-period window.
    """
    def _sma(rowcount, values):
        result = []
        push = result.append
        sigma_x = 0
        buffer = [None]*n
        nones = n
        ptr = 0

        for v in values:
            x = buffer[ptr]
            try:
                sigma_x -= x
            except TypeError:
                nones -=1

            buffer[ptr] = v
            ptr += 1
            if ptr == n:
                ptr = 0

            try:
                sigma_x += v
            except TypeError:
                nones +=1

            push(None if nones else sigma_x/n)


        return result
    return _sma

# ======================================================================
# Stats
# ======================================================================
def standard_deviation(n):
    """
    Compute the Standard Deviation over a n-period window.
    """
    var = variance(n)
    sqrt = math.sqrt

    def s(rowcount, values):
        values = var(rowcount, values)
        result = []
        push = result.append

        for v in values:
            push(None if v is None else sqrt(v))

        return result
    return s

def variance(n):
    """
    Compute the Variance over a n-period window.
    """
    a = 1.0/(n-1.0)
    b = a/n

    def s(rowcount, values):
        sigma_ui = 0.0
        sigma_ui2 = 0.0
        buffer = [None]*n
        nones = n
        ptr = 0
        result = []
        push = result.append

        for i, v in enumerate(values):
            x = buffer[ptr]

            try:
                sigma_ui -= x
                sigma_ui2 -= x*x
            except TypeError:
                nones -= 1

            buffer[ptr] = v
            ptr += 1
            if ptr == n:
                ptr = 0

            try:
                sigma_ui += v
                sigma_ui2 += v*v
            except TypeError:
                nones += 1

            push(None if nones else a*sigma_ui2 - b*sigma_ui*sigma_ui)

        return result
    return s

def volatility(n, tau=1/252):
    """
    Compute the Annualized Historical Volatility over a n-period window.

    In practice this is the standard deviation of the day-to-day return.

    Parameters:
        n: the number of periods in the window. Often 20 or 21 for dayly data
            (corresponding to the number of trading days in one month)
        tau: inverse of the number of periods in one year
    """
    stddev = standard_deviation(n)
    log = math.log
    k = math.sqrt(1/tau)
    vol = lambda stddev : stddev*k

    def _volatility(rowcount, values):
        # 1. Continuously compounded return for each period
        ui = map1(lambda curr, prev: log(curr/prev))(rowcount, values)
        # 2. Standard deviation
        result = stddev(rowcount, ui)
        # 3. Annualized values
        return map(vol)(rowcount, result)

    return _volatility

def beta(n):
    """
    Compute the Beta between two columns over a n-period window.
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
    return naive_window(_beta, n)

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
# Indicators
# ======================================================================
def basing_point_bull(low, high):
    """
    Magee's Basing Point in a bull market as explained in "Technical Analysis
    for Stocks Trends, 11th Edition" p365.

    This indicator will find Minor Bottoms from a (low, close) price pair.
    """
    def _basing_point_bull(rowcount, low, high):
        MINUS_INF = float("-inf")
        result = []
        push = result.append
        it = zip(range(rowcount), low, high)
        current = None
        highest = MINUS_INF
        n = 0

        for i, l, h in it:
            if l is None or h is None:
                push(current)
                continue
            if h > highest:
                # Possible new high
                high_day_of_the_lowest = highest = h
                lowest = l
                n = 0
            elif l < lowest:
                # Possible new low
                lowest = l
                high_day_of_the_lowest = h
                n = 0
            elif l > high_day_of_the_lowest:
                # One periode completly outside the lowest day
                n += 1

            if n > 2:
                # New Basing Point found. Reset.
                current = lowest
                highest = MINUS_INF

            push(current)

        return result

    return _basing_point_bull, low, high

def basing_point_bear(low, high):
    """
    Magee's Basing Point in a bear market as explained in "Technical Analysis
    for Stocks Trends, 11th Edition" p365.

    This indicator will find Minor Tops from a (low, close) price pair.
    """
    def _basing_point_bear(rowcount, low, high):
        PLUS_INF = float("inf")
        result = []
        push = result.append
        it = zip(range(rowcount), low, high)
        current = None
        lowest = PLUS_INF
        n = 0

        for i, l, h in it:
            if l is None or h is None:
                push(current)
                continue
            if l < lowest:
                # Possible new low
                low_day_of_the_highest = lowest = l
                highest = h
                n = 0
            elif h > highest:
                # Possible new low
                highest = h
                low_day_of_the_highest = l
                n = 0
            elif h < low_day_of_the_highest:
                # One periode completly outside the highest day
                n += 1

            if n > 2:
                # New Basing Point found. Reset.
                current = highest
                lowest = PLUS_INF

            push(current)

        return result

    return _basing_point_bear, low, high

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

def min(n):
    """
    Sliding minimum over a n-periods window.
    """
    assert n > 0
    def _min(rowcount, values):
        result = []
        store = result.append
        queue = deque()
        popleft = queue.popleft
        pushright = queue.append
        cooldown = n-1

        for value in values:
            try:
                while len(queue) >= n:
                    popleft()
                while len(queue) and queue[0] > value:
                    popleft()
                pushright(value)
            except TypeError:
                cooldown = n

            if cooldown:
                store(None)
                cooldown -= 1
            else:
                store(queue[0])

        return result

    return _min

def max(n):
    """
    Sliding maximum over a n-periods window.
    """
    assert n > 0
    def _max(rowcount, values):
        result = []
        store = result.append
        queue = deque()
        popleft = queue.popleft
        pushright = queue.append
        cooldown = n-1

        for value in values:
            try:
                while len(queue) >= n:
                    popleft()
                while len(queue) and queue[0] < value:
                    popleft()
                pushright(value)
            except TypeError:
                cooldown = n

            if cooldown:
                store(None)
                cooldown -= 1
            else:
                store(queue[0])

        return result

    return _max

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
    ma = sma(n)

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

def _index(col, x, *, bsearch=bisect.bisect_left):
    idx = bsearch(col, x)
    if idx == len(col) or col[idx] != x:
        raise ValueError

    return idx

def line(x1, x2, x_col, y1_col, y2_col=None):
    """
    Extrapolate a linear trend by two points.
    """
    if y2_col is None:
        y2_col = y1_col

    def _line(rowcount, x_col, y1_col, y2_col):
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

        return result

    return _line, x_col, y1_col, y2_col

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
