from fin.seq import serie, plot
"""
Plot intraday date from a CSV file

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/intraday.py
"""
FNAME="tests/_fixtures/BTCUSDT.csv"
with open(FNAME, "r") as f:
    fieldnames = ( "Date", "Open", "High", "Low", "Close", "Volume" )
    t = serie.Serie.from_csv(f, "mnnnnn", fieldnames=fieldnames)

mp = plot.Multiplot(t, "Date")
p = mp.new_plot(3)
p.draw_candlestick("Open", "High", "Low", "Close")

plot.gnuplot(mp, size=(1000,600), font="Sans,8")
