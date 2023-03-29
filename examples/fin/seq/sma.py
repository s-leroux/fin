from fin.api.yf import Client
from fin.seq import algo
from fin.datetime import CalendarDateDelta

"""
Compute the Simple Moving Average of the French CAC 40 index over a
50-day window.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/sma.py
"""
client = Client()
t = client.historical_data("^FCHI", CalendarDateDelta(days=900))
t.add_column("MA", (algo.sma(50), "Close"))

print(t)
