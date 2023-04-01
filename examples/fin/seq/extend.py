from fin import datetime
from fin.seq import table
from fin.seq import expr

"""
Demonstrate how one could add more rows to a table

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/extend.py
"""

from_date = datetime.parseisodate("2023-03-27")
one_week = [from_date, *from_date.iter_by(days=1,n=6)]

a = one_week[:3]
b = one_week[3:]


t = table.Table(len(a))
t.add_column("Date", expr.iterable(a))
t.add_column("X", 1)
print(t)

t = table.outer_join(t, { "Date": b }, "Date")
print(t)
