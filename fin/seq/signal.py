"""
Signals.
"""

from fin.seq.column import Column
from fin.seq import column

# ======================================================================
# Signals
# ======================================================================
def above():
    """
    Test if a_i > b_i.
    """
    def _above(rowcount, a, b):
        result = [None]*rowcount

        for i, row in enumerate(zip(a, b)):
            try:
                result[i] = row[0] > row[1]
            except TypeError:
                pass

        return Column.from_sequence(None, result)

    return _above

def below():
    r = above()

    def _below(rowcount, a, b):
        return r(rowcount, b, a)

    return _below

def almost_equal():
    """
    Test if |x_i - y_i| <= delta_i.
    """
    def _almost_equal(rowcount, x, y, delta):
        result = [None]*rowcount

        for i, (x, y, delta) in enumerate(zip(x, y, delta)):
            try:
                result[i] = -delta <= x-y <= delta
            except TypeError:
                pass

        return Column.from_sequence(None, result)

    return _almost_equal

def increase(p=1):
    """
    Test if x_i - x_(i-p) > threshold_i.
    """
    assert p > 0

    def _increase(rowcount, x, threshold=None):
        result = [None]*rowcount

        history = []
        for i, row in enumerate(zip(x, threshold or [0.0]*rowcount)):
            history.append(row)
            try:
                result[i] = history[-1][0] - history[-p-1][0] > history[-1][1]
            except (IndexError, TypeError) as e:
                pass

        return Column.from_sequence(None, result)

    return _increase

# ======================================================================
# Algorithms
# ======================================================================
def pattern(*events):
    """
    Detect matching patterns in data.

    A pattern made of n events is matched if events[i](data[-i]) is true for i in range(0,n).
    In other words, if events[0] is true today, and events[1] was true yesterday,
    event[2] was true the day before, and so on.
    """
    n = len(events)
    def _pattern(rowcount, *columns):
        result = [None]*rowcount
        history = []

        for i, row in enumerate(zip(*columns)):
            history.append(row)
            sig = row[0] and i >= n
            if sig:
                for j in range(1, n):
                    if not history[i-j][j]:
                        sig = False
                        break

            result[i] = sig

        return Column.from_sequence(None, result)

    return (_pattern, *events)

def when():
    """
    Evaluates to a_i if t_i is true, else b_i.
    """
    def _when(rowcount, test, a, b):
        result = [None]*rowcount

        for i, (vt, va, vb) in enumerate(zip(test, a, b)):
            result[i] = va if vt else vb

        return Column.from_sequence(None, result)

    return _when

# ======================================================================
# Quantifiers
# ======================================================================
def all(*signals):
    """
    True if all signals evaluates to true.
    """
    def _all(rowcount, *signals):
        result = [None]*rowcount

        for i, row in enumerate(zip(*signals)):
            r = True
            for value in row:
                r &= value
                if not r:
                    break
            result[i] = r

        return Column.from_sequence(None, result)

    return (_all, *signals)

def any(*signals):
    """
    True if any signal evaluates to true.
    """
    def _any(rowcount, *signals):
        result = [None]*rowcount

        for i, row in enumerate(zip(*signals)):
            r = False
            for value in row:
                if value:
                    r = True
                    break
            result[i] = r

        return Column.from_sequence(None, result)

    return (_any, *signals)
