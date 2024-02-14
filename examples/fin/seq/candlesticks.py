from fin.api import yf
from fin.seq import algo
from fin.seq import plot
from fin.datetime import CalendarDateDelta
"""
Plot recent the quotes for a stock alongside with a couple of indicators.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/plot.py
"""
client = yf.Client()

t = client.historical_data("BAC", CalendarDateDelta(days=100))
sma, = t.add_column((algo.sma(5), "Close"))

mp = plot.Multiplot(t, "Date")
p = mp.new_plot(3)
p.draw_candlestick("Open", "High", "Low", "Close")
p.draw_line(sma.name)

plot.gnuplot(mp, size=(1000,600), font="Sans,8")
