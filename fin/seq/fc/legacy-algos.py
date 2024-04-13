""" Common algorithms for column expressions
"""
import math
import builtins
import bisect
from collections import deque

from fin.utils.log import console

from fin.seq.fc.algox import *

# ======================================================================
# Adapters
# ======================================================================
def by_row(fct):
    """
    Evaluates a function row by row on a list of columns.
    """
    def _by_row(serie, *cols):
        rowcount = serie.rowcount
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

        return Column.from_sequence(result)

    return _by_row

# ======================================================================
# Accumulator
# ======================================================================
def acc(value, neg=False, pos=True):
    """
    Increase the running value when pos is true, decrease it when neg is true.
    """
    def _acc(serie, value, neg, pos):
        rowcount = serie.rowcount
        result = [None]*rowcount
        a = 0.0

        for i, (vi, ni, pi) in enumerate(zip(value, neg, pos)):
            if pi:
                a += vi
            if ni:
                a -= vi

            result[i] = a

        return Column.from_sequence(result)

    return (_acc, value, neg, pos)

def acc2(value, buy, sell):
    """
    Simulate an investor that can buy and sell one share.

    The investor can only sell when it owns a share.
    """
    def _acc(serie, value, buy, sell):
        rowcount = serie.rowcount
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

        return Column.from_sequence(result)

    return (_acc, value, buy, sell)

# ======================================================================
# Window functions
# ======================================================================
def window(fct, n):
    def _window(serie, *cols):
        rowcount = serie.rowcount
        i = n-1
        result = [None]*rowcount
        while i < rowcount:
            result[i] = fct(i-n+1, i+1, *cols)
            i += 1

        return Column.from_sequence(result)

    return _window

def naive_window(fct, n):
    def _fct(start, end, *cols):
        return fct(*[col[start:end] for col in cols])

    return window(_fct, n)





# ======================================================================
# Compound functions
# ======================================================================
def ratio_to_moving_average(n):
    ma = sma(n)

    def _ratio_to_moving_average(serie, a):
        b = ma(serie, a)
        return ratio(serie, a, b)

    return _ratio_to_moving_average


