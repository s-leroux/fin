from fin.api import yf
from fin.seq import fc
from fin.seq import plot
from fin.datetime import CalendarDateDelta
"""
Plot recent the quotes for a stock alongside with a couple of indicators.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/plot.py
"""
client = yf.Client()

t = client.historical_data("BAC", CalendarDateDelta(days=500),select=["Date", dict(name="Close", expr="Adj Close")])
t = t.select(
    "Date",
    "Close",
    (fc.named("SMA200"), fc.sma(200), "Close"),
    (fc.named("SMA50"), fc.sma(50), "Close"),
    (fc.named("SMA10"), fc.sma(10), "Close"),
)
t = t.lstrip("SMA200")

mp = plot.Multiplot(t, "Date")
p = mp.new_plot(3)
p.draw_line("Close")
p.draw_line("SMA200")
p.draw_line("SMA50")
p.draw_line("SMA10")

plot.gnuplot(mp, size=(1000,600), font="Sans,8")

