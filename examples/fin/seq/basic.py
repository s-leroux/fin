from fin.seq import serie
from fin.seq import fc

from math import pi, sin, cos

"""
Basic usage of the `fin.seq` package

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/basic.py
"""

def deg2rad(deg):
    return 2*pi*deg/360

t = serie.Serie.create(
        # Create a 351-rows serie
        (fc.named("ROW NUMBER"), fc.range(361)),
        # Maps the first column to the [0, 2π] range
        (fc.named("ANGLE"), fc.map(deg2rad), "ROW NUMBER"),
        # Do the same to map than ANGLE column to sin() and cos()
        (fc.named("SIN"), fc.map(sin), "ANGLE"),
        (fc.named("COS"), fc.map(cos), "ANGLE"),
)

# Print the table
print(t)

# Plot the SIN/COS function:
from fin.seq import plot
mp = plot.Multiplot(t, "SIN", mode="XY")
p = mp.new_plot()
p.draw_line("COS")

plot.gnuplot(mp, size=(800,600))
