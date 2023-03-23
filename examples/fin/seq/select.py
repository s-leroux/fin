from fin.api import yf
from fin.seq import algo

"""
Example of column selection.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/select.py
"""
t = yf.historical_data("^FCHI", yf.timedelta(days=20))
t = t.select(
        "High",
        "Low",
        "Close",
        { "name": "Volume (k)", "expr": (algo.map(lambda x : x//1000), "Volume") },
        )

print(t)

t = yf.historical_data("^FCHI", yf.timedelta(days=20), select=("Date", "Close"))
print(t)
