from fin.api import yf
from fin.seq import algo

"""
Compute the Simple Moving Average of the French CAC 40 index over a
50-day window.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/sma.py
"""
t = yf.historical_data("^FCHI", yf.timedelta(days=900))
t.add_column("MA", (algo.sma(50), "Close"))

print(t)
