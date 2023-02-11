""" Common algorithms usable on tables
"""
import math
import builtins

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

def map(fct):
    def _map(rowcount, values):
        result = [None]*rowcount
        i = rowcount
        while i:
            i -= 1
            x = values[i]
            result[i] = fct(x) if x is not None else None

        return result

    return _map

def volatility(n, tau=1/252):
    """ The price volatility over a n-period window
    """
    stddev = standard_deviation(n)
    log = math.log
    k = math.sqrt(1/tau)
    vol = lambda stddev : stddev*k

    def _volatility(rowcount, values):
        ui = [None]*rowcount
        prev = values[0]
        i = 1
        while i < rowcount:
            x = values[i]
            ui[i] = log(x/prev)
            prev = x

            i += 1

        result = stddev(rowcount, ui)
        return map(vol)(rowcount, result)

    return _volatility