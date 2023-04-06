from fin.api import yf
from fin.seq import table
from fin.seq import algo
from fin.seq import plot
from fin.datetime import CalendarDateDelta
"""
Plot two securities against each other and draw best-fit line.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/plot_xy.py
"""
client = yf.Client()

load = yf.Client().historical_data

duration = CalendarDateDelta(days=25)
ta = load("QQQ", duration, select=["Date", dict(name="QQQ", expr="Adj Close")])
tb = load("SPY", duration, select=["Date", dict(name="SPY", expr="Adj Close")])
t = table.join(ta,tb,"Date")
t.add_column("BEST FIT", (algo.best_fit, "QQQ", "SPY"))

mp = plot.Multiplot(t, "QQQ", mode=plot.Multiplot.XY)
p = mp.new_plot(3)
p.draw_point("SPY")
p.draw_line("BEST FIT")

plot.gnuplot(mp, size=(1000,600), font="Sans,8")

