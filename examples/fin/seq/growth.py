from fin.seq import plot
from fin.seq.serie import Serie
from fin.seq import fc
from fin.model import kellyx
"""
Plot the expected growth rate E log X of balancing between two investments

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/seq/growth.py
"""
exp1=((0.6, 0.5), (0.3, 2), (0.10, 10))
exp2=((0.30, 0.8), (0.40, 1.1), (0.30, 2))

WEALTH=1
o = kellyx.Experiment(exp1, exp2)

t = Serie.create(
        (fc.named("X"), fc.range(101)),
        (fc.named("Y"), fc.map(lambda x : o.growth(x/100)), "X")
    )

mp = plot.Multiplot(t, "X")
p = mp.new_plot(3)
p.draw_line("Y")

plot.gnuplot(mp, size=(1000,600), font="Sans,8")

