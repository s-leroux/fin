from fin.api.yf import Client
from fin.seq import fc
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
        (fc.named("Volume (k)"), fc.map(lambda x : x//1000), "Volume"),
    )
print(t)

t = client.historical_data("^FCHI", CalendarDateDelta(days=20)).select("Close")
print(t)
