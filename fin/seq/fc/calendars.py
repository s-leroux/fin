import inspect

from fin import datetime
from fin.seq.column import Column

# ======================================================================
# Calendar functions
# ======================================================================
def shift_date(delta):
    """
    Offset a calendar date.
    """
    offset = datetime.asCalendarDateDelta(delta)

    def _shift_date(serie, dates):
        rowcount = serie.rowcount
        name = getattr(dates, "name", None)

        result = [None]*rowcount
        for idx, date in enumerate(dates):
            try:
                result[idx] = date+offset
            except ValueError as e:
                console.warn(f"Can't apply {inspect.currentframe().f_code.co_name} to {date}")
                console.info(str(e))

        return Column.from_sequence(result, name=name)

    return _shift_date

def hist2(f, n, interval):
    """
    Apply a function to data et recuring intervals
    """
    assert interval > 0
    def _hist(serie, data):
        rowcount = serie.rowcount
        result = [None]*rowcount
        for i, value in enumerate(data):
            if i < interval:
                result[i] = []
            else:
                result[i] = [value] + result[i-interval][:n]

        result = builtins.map(f, result)
        return Column.from_sequence(result)

    return _hist

def hist(f, n, years=0, months=0, days=0):
    """
    Apply a function to data at recuring intervals.
    """
    offset = datetime.CalendarDateDelta(years, months, days)
    def _hist(serie, dates, data):
        rowcount = serie.rowcount
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

        return Column.from_sequence(result)

    return _hist

