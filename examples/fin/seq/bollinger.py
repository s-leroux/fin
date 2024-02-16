from fin.api import yf
from fin.seq import algo
from fin.seq import plot
from fin.datetime import CalendarDateDelta
"""
Plot recent the quotes for a stock alongside with a couple of indicators.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/bollinger.py
"""
client = yf.Client()

t = client.historical_data("BAC", CalendarDateDelta(days=200))
sma, = t.add_column((algo.sma(5), "Close"))
boll_b, boll_m, boll_a = t.add_column((algo.bband(5), "Close"))

mp = plot.Multiplot(t, "Date")
p = mp.new_plot(3)
p.draw_candlestick("Open", "High", "Low", "Close")
p.draw_line(boll_a.name)
p.draw_line(boll_m.name)
p.draw_line(boll_b.name)

plot.gnuplot(mp, size=(1000,600), font="Sans,8")
