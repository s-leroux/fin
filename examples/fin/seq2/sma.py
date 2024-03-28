from fin.api.yf import Client
from fin.seq2 import fc
from fin.datetime import CalendarDateDelta

"""
Compute the Simple Moving Average of the French CAC 40 index over a
50-day window.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/sma.py
"""
client = Client()
t = client.historical_data("^FCHI", CalendarDateDelta(days=900))
t = t.select(
        fc.all,
        (fc.named("SMA"), fc.sma(50), "Close")
    )

print(t)
