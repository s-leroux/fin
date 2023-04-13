from fin.seq import table
from fin.seq import algo
from fin.seq import expr

from math import pi, sin, cos

"""
Basic usage of the `fin.seq` package

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/basic.py
"""

# Create an empty table with provision for 361 rows:
t = table.Table(361)

# Create a column with values from 0 to 360
t.add_column("ROW NUMBER", expr.ramp())

# Create a second column that maps the first to the [0, 2π] range
def deg2rad(deg):
    return 2*pi*deg/360

t.add_column("ANGLE", (expr.map(deg2rad), "ROW NUMBER"))

# Do the same to map than ANGLE column to sin() and cos()
t.add_column("SIN", (expr.map(sin), "ANGLE"))
t.add_column("COS", (expr.map(cos), "ANGLE"))

# Print the table
print(t)

# Plot the SIN/COS function:
from fin.seq import plot
mp = plot.Multiplot(t, "SIN", mode="XY")
p = mp.new_plot()
p.draw_line("COS")

plot.gnuplot(mp, size=(800,600))
