# fin
This project aims to provide a set of personal investment tools with minimum dependencies.

The project does not have a GUI. You interact with the tools by writing Python scripts. The most actively developed part of the project is the `fin.seq` package that provides time/data series manipulation functions.

# Getting started
I keep the dependencies to a minimum. Currently, outside Python 3 (≥ 3.6.9) and the standard Python library, you need:

* Python Requests (≥ 2.18.4)
* Cython3 (≥ 0.26.1)
* Gnuplot (≥ 5.2)

Some development was made regarding web crawling and data mining using BeautifulSoup, but it is currently out of the main tree.

## Prerequisites
The development is done under Linux Ubuntu Bionic.

```
apt-get install python3 cython3 python3-requests gnuplot-x11
```

## Installation
Download the project using Git, enter the directory, and run `make compile` to compile and build the Cython-generated C files, and `make tests-all` to run the all test suite:

```
git clone git@github.com:s-leroux/fin.git
cd fin
make compile
make tests-all
```

# `fin.seq`
This package allows data manipulations using the concept of series.
A serie is a set of columns associated with an index.
The index itself is a column with the special property of being ordered (in ascending order).
Series are implemented in the `fin.seq.Serie` class.

The most straightforward example is a time serie representing stock quotes.
In that case, the _date_ is the index of the serie, and the _open_,_high_, _low_, and _close_ values are stored in the individual data columns of the serie.
For example, the `fin.api` package can retrieve historical quotations from Yahoo Finance, and return the result as a serie:

```
from fin.api import yf
from fin.datetime import CalendarDateDelta, CalendarDate

client = yf.Client()

t = client.historical_data("TSLA", CalendarDateDelta(days=5), CalendarDate(2023, 7, 20))
print(t)
```
```
Date, Open, High, Low, Close, Adj Close, Volume
2023-07-17, 286.630005, 292.230011, 283.570007, 290.380005, 290.380005, 131569600
2023-07-18, 290.149994, 295.26001, 286.01001, 293.339996, 293.339996, 112434700
2023-07-19, 296.040009, 299.290009, 289.519989, 291.26001, 291.26001, 142355400
2023-07-20, 279.559998, 280.929993, 261.200012, 262.899994, 262.899994, 175158300
```

You can manually create serie using the `fin.seq.serie.Serie.create` factory method.
The first parameter defines the index, and the remaining parameters define the data columns.
Each is defined using a LISP-inspired mini-language:

Here is a short example (from `examples/fin/seq/basic.py`):
```
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
        # Create a 361-rows serie
        (fc.named("ROW NUMBER"), fc.range(361)),
        # Maps the first column to the [0, 2π] range
        (fc.named("ANGLE"), fc.map(deg2rad), "ROW NUMBER"),
        # Do the same to map than ANGLE column to sin() and cos()
        (fc.named("SIN"), fc.map(sin), "ANGLE"),
        (fc.named("COS"), fc.map(cos), "ANGLE"),
)

# Print the serie
print(t)
```

Here is the result when you run this script:
```
sh$ python3 < examples/fin/seq/basic.py | head -10
ROW NUMBER, ANGLE, SIN, COS
0, 0.0, 0.0, 1.0
1, 0.017453292519943295, 0.01745240643728351, 0.9998476951563913
2, 0.03490658503988659, 0.03489949670250097, 0.9993908270190958
3, 0.05235987755982988, 0.05233595624294383, 0.9986295347545738
4, 0.06981317007977318, 0.0697564737441253, 0.9975640502598242
5, 0.08726646259971647, 0.08715574274765817, 0.9961946980917455
6, 0.10471975511965977, 0.10452846326765346, 0.9945218953682733
7, 0.12217304763960307, 0.12186934340514748, 0.992546151641322
8, 0.13962634015954636, 0.13917310096006544, 0.9902680687415704
```

You can load that table in your favorite spreadsheet to plot the SIN/COS graph. If you have `gnuplot` installed on your system, you can also plot it directly from Python:
```
# Plot the SIN/COS function:
from fin.seq import plot
mp = plot.Multiplot(t, "SIN", mode="XY")
p = mp.new_plot()
p.draw_line("COS")

plot.gnuplot(mp, size=(800,600))
```

![A basic usage example of `fin.seq` displaying a circle](docs/images/basic.png)

## Joining two series
Series support join operations on the _index_ column.
It is the caller's responsibility to ensure the key columns are *sorted in ascending order*.
Future versions will enforce that requirement.
Until that, joining series using an unordered index should be considered an *undefined behavior*.

### Inner join
When performing an _inner join_, the result serie will contain only rows present in both series according to the index.
The _inner join_ is implemented as the `&` (*and*) operator between series:
```
from fin.seq import serie
from fin.seq import fc

s1 = serie.Serie.create(
        (fc.named("X"), fc.sequence((1,2,3,4))),
        (fc.named("Y"), fc.mul, "X", fc.constant(10)),
    )

print(s1)

# Display:
# X, Y
# 1, 10.0
# 2, 20.0
# 3, 30.0
# 4, 40.0

s2 = serie.Serie.create(
        (fc.named("X"), fc.sequence((1,4))),
        (fc.named("Z"), fc.mul, "X", fc.constant(100)),
    )

print(s2)

# Display:
# X, Z
# 1, 100.0
# 4, 400.0
# 5, 500.0

print(s1 & s2)
```

The result of the inner join operation being:

```
X, Y, Z
1, 10.0, 100.0
4, 40.0, 400.0
```

### Full outer join
When performing a _full outer join_, the result serie will contain the rows present in either (or both) series in the index order.
The _full outer join_ is implemented as the `|` (*or*) operator between series:

```
# Continuing from the previous example

print(s1 | s2)
```

```
X, Y, Z
1, 10.0, 100.0
2, 20.0, None
3, 30.0, None
4, 40.0, 400.0
5, None, 500.0
```

## Loading financial data
You can use the `fin.seq` package like a command-line spreadsheet. However, its primary purpose remains working with financial data.

Currently, the library supports the *Yahoo! Finance* and *eodhistoricaldata.com* data providers for historical quotes. 

In the next example, we will load from *Yahoo! Finance* the last 100 end-of-day quote for *Bank of America* (ticker `BAC`):
```
from fin.api import yf
from fin.seq import fc
from fin.seq import plot

# Use the Yahoo! Finance provider
provider = yf.Client()

t1 = provider.historical_data("BAC", dict(days=100))
```
The provider returns a serie (instance of `serie.Serie`) with the data, open, high, low, close, adj close, and volumes columns.
Serie are _immutable_.

However, you can create a projection with the `selection` member function.
A projection is a series whose columns are calculated from the original serie.

For example, if you are interested only in the _open_, _high_, _low_, _close_ values, and the 5-perod simple moving average (_sma_) of the _close_ prices, you can write:

```
t2 = t1.select(
        "Open",
        "High",
        "Low",
        "Close",
        (fc.sma(5), "Close"),
    )

print(t2)
```

Running from the terminal, you get:
```
Date, Open, High, Low, Close, SMA(5)
2023-12-20, 33.380001, 33.709999, 32.950001, 32.98, None
2023-12-21, 33.240002, 33.450001, 32.889999, 33.200001, None
2023-12-22, 33.209999, 33.669998, 33.200001, 33.43, None
2023-12-26, 33.450001, 33.959999, 33.369999, 33.860001, None
2023-12-27, 33.799999, 33.950001, 33.66, 33.84, 33.46200040000001
2023-12-28, 33.82, 33.970001, 33.77, 33.880001, 33.6420006
2023-12-29, 33.939999, 33.990002, 33.549999, 33.669998, 33.736000000000004
2024-01-02, 33.389999, 34.07, 33.27, 33.900002, 33.8300004
2024-01-03, 33.650002, 33.77, 33.240002, 33.529999, 33.764
```

Finally, let's plot the graph:
```
sma = t2.columns[-1]

mp = plot.Multiplot(t2, "Date")
p = mp.new_plot(3)
p.draw_candlestick("Open", "High", "Low", "Close")
p.draw_line(sma.name)

plot.gnuplot(mp, size=(1000,600), font="Sans,8")
```
Et voilà:
![A candlestick plot of the last 100 daily quotations for Bank of America](docs/images/candlesticks.png)


# `fin.model`
The ``fin`` package also contains a simple 1-variable solver (implemented in ``fin.math``) designed to work seamlessly with predefined models.

For example, using the [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion) you can find the optimum allocation for a risky investment:

```
WIN=0.20
LOSS=0.20
WIN_PROB=0.60

model = kelly.KellyCriterion(dict(
    p=WIN_PROB,
    a=WIN,
    b=LOSS,
    ))

f_star = model['f_star']
```

You can solve a model for any variable (bearing the solver's limitation).
For example, if I'm ready to raise my allocation up to 50% of the available funds, and given a +/- 20% outcome, which probability to win do I implicitly assume?

```
WIN=0.20
LOSS=0.20
ALLOC=0.50

model = kelly.KellyCriterion(dict(
    a=WIN,
    b=LOSS,
    f_star=ALLOC
    ))

print("Implied probability to win =", model['p'])
```
