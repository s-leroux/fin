from fin.api import yf
from fin.seq import algo
from fin.seq import plot

"""
Plot recent the quotes for a stock alongside with a couple of indicators.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/plot.py
"""
t = yf.historical_data("BAC", yf.timedelta(days=500),select=["Date", dict(name="Close", expr="Adj Close")])
t.add_column("SMA200", (algo.sma(200), "Close"))
t.add_column("SMA50", (algo.sma(50), "Close"))
t.add_column("SMA10", (algo.sma(10), "Close"))
t = t.lstrip(["SMA200"])

mp = plot.Multiplot(t, "Date")
p = mp.new_plot(3)
p.draw_line("Close")
p.draw_line("SMA200")
p.draw_line("SMA50")
p.draw_line("SMA10")

plot.gnuplot(mp, size=(1000,600), font="Sans,8")

