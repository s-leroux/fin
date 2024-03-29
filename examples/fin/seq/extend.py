from fin import datetime
from fin.seq import serie
from fin.seq import fc

"""
Demonstrate how one could add more rows to a table using 
a full outer join.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/extend.py
"""

from_date = datetime.parseisodate("2023-03-27")
one_week = [from_date, *from_date.iter_by(days=1,n=6)]

a = serie.Serie.create(
        (fc.named("Date"), fc.sequence(one_week[:3])),
        (fc.named("X"), fc.constant(1)),
    )
b = serie.Serie.create(
        (fc.named("Date"), fc.sequence(one_week[3:])),
        (fc.named("Y"), fc.constant(2)),
    )
print(a)
print(b)

print(a | b)
