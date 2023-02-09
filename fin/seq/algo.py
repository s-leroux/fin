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

    def s(ui):
        ui_squared = [u*u for u in ui]
        s1 = sum(ui_squared)
        s2 = sum(ui)**2
       
        return sqrt(a*s1-b*s2)

    return naive_window(s, n)
