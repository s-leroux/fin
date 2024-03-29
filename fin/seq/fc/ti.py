from .tix import *

# ======================================================================
# Technical Indicators
# ======================================================================
def basing_point_bull(low, high):
    """
    Magee's Basing Point in a bull market as explained in "Technical Analysis
    for Stocks Trends, 11th Edition" p365.

    This indicator will find Minor Bottoms from a (low, close) price pair.
    """
    def _basing_point_bull(serie, low, high):
        rowcount = serie.rowcount
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

        return Column.from_sequence(result)

    return _basing_point_bull, low, high

def basing_point_bear(low, high):
    """
    Magee's Basing Point in a bear market as explained in "Technical Analysis
    for Stocks Trends, 11th Edition" p365.

    This indicator will find Minor Tops from a (low, close) price pair.
    """
    def _basing_point_bear(serie, low, high):
        rowcount = serie.rowcount
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

        return Column.from_sequence(result)

    return _basing_point_bear, low, high

