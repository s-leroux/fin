from fin.api import yf
from fin.seq import fc
from fin.seq import plot
from fin.datetime import CalendarDateDelta
"""
Plot recent the quotes for a stock alongside with a couple of indicators.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/bollinger.py
"""
client = yf.Client()

t = client.historical_data("BAC", CalendarDateDelta(days=200))
t = t.extend(
        (fc.sma(5), "Close"),
        (fc.bband(5), "Close"),
)
sma, boll_b, boll_m, boll_a = t.columns[-4:]

mp = plot.Multiplot(t, "Date")
p = mp.new_plot(3)
p.draw_candlestick("Open", "High", "Low", "Close")
p.draw_line(boll_a.name)
p.draw_line(boll_m.name)
p.draw_line(boll_b.name)

plot.gnuplot(mp, size=(1000,600), font="Sans,8")
