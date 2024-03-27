from fin.api import yf
from fin.seq2 import serie
from fin.seq2 import fc
from fin.seq2 import plot
from fin.datetime import CalendarDateDelta
"""
Plot two securities against each other and draw best-fit line.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/plot_xy.py
"""
client = yf.Client()

load = yf.Client().historical_data

duration = CalendarDateDelta(days=25)
ta = load("QQQ", duration)
tb = load("SPY", duration)
t = ta & tb
keyX="QQQ:Adj Close"
keyY="SPY:Adj Close"
print(t)
print(repr(ta))
print(repr(tb))
print(repr(t))
t = t.select(
        "QQQ:Adj Close",
        "SPY:Adj Close",
        (fc.named("BEST FIT"), fc.best_fit, keyX, keyY)
)

mp = plot.Multiplot(t, keyX, mode=plot.Multiplot.XY)
p = mp.new_plot(3)
p.draw_point(keyY)
p.draw_line("BEST FIT")

plot.gnuplot(mp, size=(1000,600), font="Sans,8")

