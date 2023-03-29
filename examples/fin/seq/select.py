from fin.api.yf import Client
from fin.seq import algo
from fin.datetime import CalendarDateDelta

"""
Example of column selection.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/select.py
"""
client = Client()
t = client.historical_data("^FCHI", CalendarDateDelta(days=20))
t = t.select(
        "High",
        "Low",
        "Close",
        { "name": "Volume (k)", "expr": (algo.map(lambda x : x//1000), "Volume") },
        )

print(t)

t = client.historical_data("^FCHI", CalendarDateDelta(days=20), select=("Date", "Close"))
print(t)
