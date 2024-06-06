"""
Plot 2D curves using GNUPlot
"""
import os
from fin.seq.serie import Serie
from fin.seq import presentation
from fin.seq.column import Column
import asyncio
import math
import collections
from numbers import Number

PIPE = asyncio.subprocess.PIPE
GNUPLOT_CMD=os.environ.get("FIN_GNUPLOT", "gnuplot -p").split()

# ======================================================================
# Utilities
# ======================================================================
SI_PREFIXES = {
        1000: "k",
        1000000: "M",
        }

def prefix_number(x):
    if x == 0:
        return "0"

    if x < 0:
        sign = -1
        x = -x
    else:
        sign = 1

    exp = 1000**math.floor(math.log(x, 1000))
    pref = SI_PREFIXES.get(exp, None)

    if not pref:
        return format(x*sign, "g")

    return f"{round(x/exp, 3)}{pref}"

# ======================================================================
# managing tics
# ======================================================================
class Tics:
    def __init__(self, items=()):
        self._tics = ()
        if items:
            self.extend(items)

    def extend(self, items):
        items = [item for item in items if item is not None]
        items = set((item, format(item, "-10.04f")) if isinstance(item, Number) else item for item in items)
        items = items.union(self._tics)

        self._tics = sorted(items)

    def __len__(self):
        return len(self._tics)

    def __iter__(self):
        return iter(self._tics)

    def __getitem__(self, key):
        return self._tics[key]

    def __repr__(self):
        return f"Tics({tuple(self._tics)})"

def make_tics_from_sequence(n, sequence):
    """
    Return a n-item sample of the sequence as (index, value) pairs.
    """
    result = [(0, sequence[0])]
    l = len(sequence)

    if n > 2:
        i = inc = math.ceil(l/(n-1))
        while i < l-1:
            result.append((i, sequence[i]))
            i += inc

    result.append((l-1, sequence[-1]))
    return Tics(result)

def make_tics_from_range(n, a, b):
    """
    Return a list of tics covering the range [a, b].
    """
    assert a<b

    # First, find a scale matching the range amplitude
    delta = b-a
    scale = 10**math.floor(math.log(delta/n, 10))

    # Adjust the extrema to the scale:
    a = (a//scale)*scale
    b = (b//scale+1)*scale

    inc = math.ceil((b-a)/(n-1)/scale)*scale
    result = []
    acc = a
    while True:
        result.append((acc, prefix_number(acc)))
        if acc > b:
            break

        acc += inc

    return Tics(result)

    
# ======================================================================
# Plot elements
# ======================================================================
class _Element:
    def __init__(self, element):
        self._element = element

class _1DElement(_Element):
    pass

class _OHLCElement(_Element):
    pass

# ======================================================================
# A plot
# ======================================================================
class _Plot:
    def __init__(self, plot, serie):
        self._plot = plot
        self._serie = serie

        plot["elements"] = []
        plot["poi"] = Tics()

    def accept(self, visitor):
        visitor.visit_plot(self)

    def add_poi(self, *items):
        self._plot["poi"].extend(items)

    def draw_1d_element(self, kind, data_column, color_column):
        """
        Add a new line drawing on a plot.
        """
        column = self._serie[data_column]
        element = {
                "kind": kind,
                "data": [ data_column ],
                "color": color_column,
                }
        self._plot["elements"].append(element)
        # self.add_poi(*column.min_max(), column[-1])

        return _1DElement(element)

    def draw_ohlc_element(self, kind, open_price_column, high_price_column, low_price_column, close_price_column, color_column=None):
        """
        Add an open/high/low/close 4D element to the plot.
        """
        # open = self._serie[open_price_column]
        # high = self._serie[high_price_column]
        # low = self._serie[low_price_column]
        # close = self._serie[close_price_column]
        element = {
                "kind": kind,
                "data": [
                    open_price_column,
                    high_price_column,
                    low_price_column,
                    close_price_column
                    ],
                "color": color_column,
                }
        self._plot["elements"].append(element)
        # self.add_poi(*close.min_max(), column[-1])

        return _OHLCElement(element)

    def draw_line(self, data_column, color_column=None):
        """
        Add a new line drawing on a plot.
        """
        return self.draw_1d_element("line", data_column, color_column)

    def draw_bar(self, data_column, color_column=None):
        """
        Add a new bargraph on the plot.
        """
        return self.draw_1d_element("bar", data_column, color_column)

    def draw_impulse(self, data_column, color_column=None):
        """
        Add a new impulse graph on the plot.
        """
        return self.draw_1d_element("impulse", data_column, color_column)

    def draw_point(self, data_column, color_column=None):
        """
        Add a new point graph on the plot.
        """
        return self.draw_1d_element("point", data_column, color_column)

    def draw_candlestick(self, open_price_column, low_price_column, high_price_column, close_price_column):
        """
        Add a new bargraph on the plot.
        """
        return self.draw_ohlc_element("candlestick", open_price_column, low_price_column, high_price_column, close_price_column)

# ======================================================================
# A Multiplot instance
# ======================================================================
class Multiplot:
    """
    Interface to a multiplot.

    A multiplot is made of 1-to-n plots. All plots are based on the same serie
    and uses the same x-axis.
    """
    LABEL = "LABEL"
    XY = "XY"

    def __init__(self, serie, x_axis_column, *, mode=None):
        if mode is None:
            mode = Multiplot.LABEL

#        if type(x_axis_column) is Serie:
#            cols = x_axis_column.data
#            if len(cols) != 1:
#                raise ValueError(f"Multi-column are not allowed here")
#            x_axis_column = x_axis_column[1]
#
#        if type(x_axis_column) is not Column:
#            raise TypeError(f"Column or serie expected. Found {x_axis_column!r}")

        self._serie = serie

        self._plot = {
                "mode": mode,
                "title": serie.name or "Untitled",
                "x": x_axis_column,
                "plots": [],
                }

    @property
    def plot(self):
        return self._plot

    def accept(self, visitor):
        visitor.visit_multiplot(self)

    def set_title(self, title):
        self._plot["title"] = title

    def new_plot(self, relative_height=1):
        plot = {
                "height": relative_height,
                }

        self._plot["plots"].append(plot)
        return _Plot(plot, self._serie)

# ======================================================================
# GNUPlot
# ======================================================================
import subprocess
import sys

class _Process:
    def __init__(self, args, *, stdout=sys.stdout, stderr=sys.stderr):
        self.returncode = None
        self._process = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stderr=stderr,
                stdout=stdout,
                encoding="utf8",
                )
        self.stdin = self._process.stdin

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._process.stdin.close()
        self.returncode = self._process.wait()

"""
Maps plot element's "kinds" to the corresponding GNUPlot plotting style.

TODO: Possibly, this could map to a specific object or class to handle that corresponding
plotting style.
"""
_GNUPLOT_KIND_TO_STYLE={
        "bar": "boxes",
        "candlestick": "candlesticks",
        "impulse": "impulses",
        "line": "lines",
        "point": "points",
        }

class _GNUPlotDataElement:
    """
    Helper class to build gnuplot data plot elements.

    See http://www.bersch.net/gnuplot-doc/plot.html
    """
    def __init__(self, kind, entries):
        """
        Build a new gnuplot data element of the gieven kind with the specified
        entries.

        Entries are given as an iterable of key in the data source.
        Each key can be a (1-based) index, a column's label or a valid parenthesed
        gnuplot expression.

        """
        self._kind = kind
        self._entries = list(entries)
        self._color = None
        self._attr = {}
        self.title = None
        self.lc = None # linecolor
        self.fs = None # fillstyle

    def lc_rgbcolor_variable(self, expr):
        self.lc = "rgbcolor variable"
        self._color = expr

    def __str__(self):
        """
        Convert the receiver to a string representing a valid data plot element
        """
        kind = self._kind
        entries = ":".join(map(str, self._entries))
        if self._color is not None:
            entries += f":{self._color}"
        parts = []
        parts.append(f"using {entries} with {_GNUPLOT_KIND_TO_STYLE[kind]}")

        if self.title is not None:
            parts.append(f"title \"{self.title}\"")
        else:
            parts.append("notitle")
        if self.lc:
            parts.append(f"lc {self.lc}")
        if self.fs:
            parts.append(f"fs {self.fs}")

        return " ".join(parts)

class _GNUPlotVisitor:
    """
    The class that handle conversion from the data model to a GNUPlot script.
    """
    def __init__(self, write, *, term="wxt", size=(640,384), font="Sans,10"):
        self._write = write
        self._term = term
        self._font = font
        self._width, self._height = size

    def plot(self, mp):
        write = self._write
        self._serie = serie = mp._serie

        multiplot = self._multiplot = mp.plot
        self._serie = serie

        # write the preamble
        write("\n")
        write("reset\n")
        write(f"set term {self._term} size {self._width},{self._height} font \"{self._font}\"\n")
        write("set style textbox opaque\n")
        write("set boxwidth 0.5\n")
        write("set multiplot\n")
        write("set key left top\n")

        write("RED=0x800000\n")
        write("GREEN=0x008000\n")

        # xtics
        mode = multiplot["mode"]
        if mode == Multiplot.LABEL:
            write(f"set xrange [0:{serie.rowcount+1}]\n")
            x_column = serie[multiplot["x"]].data[0]
            x_tics = make_tics_from_sequence(5, x_column)
        elif mode == Multiplot.XY:
            x_tics = None
        else:
            raise NotImplementedError()

        # Grid
        write("set grid xtics ytics\n")

        # write the data
        data = presentation.Presentation("CSV", delimiter=" ")(serie)
        write("$MyData << EOD\n#")
        write(data)
        write("EOD\n")

        # write the plots
        total_height = 0
        for plot in multiplot["plots"]:
            total_height += plot["height"]
        current_height = total_height
        n = len(multiplot["plots"])
        i = 0
        for plot in multiplot["plots"]:
            i += 1

            # Plot boundaries
            prev_height = current_height
            current_height -= plot["height"]

            top = 0.80*prev_height/total_height + 0.10
            bottom = 0.80*current_height/total_height + 0.10

            # POI
            poi = plot["poi"]

            # Auto-append the min, max and last value of the last column of each element
            for element in plot["elements"]:
                column = serie[element["data"][-1]].data[0]
                poi.extend([*column.min_max(), column[-1]])

            if len(poi):
                write(f"set tmargin at screen {top:1.4f}\n")
                write(f"set bmargin at screen {bottom:1.4f}\n")
                write(f"set lmargin at screen 0.9000\n")
                write(f"set rmargin at screen 0.9900\n")
                write(f"unset label\n")
                for p in poi:
                    write(f"set label \"{p[1]}\" at graph 1.00, first {p[0]} offset graph 0.1, 0 point ps 1 pt 1 right boxed\n")

            # Set plot area
            write(f"set lmargin at screen 0.1000\n")
            write(f"set rmargin at screen 0.9000\n")
            write(f"set tmargin at screen {top:1.4f}\n")
            write(f"set bmargin at screen {bottom:1.4f}\n")

            # Plot title
            if i == 1:
                title = multiplot["title"]
                if title:
                    write(f"set title \"{title}\" noenhanced\n")
            else:
                write("set title\n")

            # xtics
            if x_tics:
                if i < n:
                    x_tics_labels = [f"\"\" {i}" for i, v in x_tics]
                else:
                    x_tics_labels = [f"\"{v}\" {i}" for i, v in x_tics]

                write(f'set xtics axis ({",".join(x_tics_labels)})\n')

            # Draw the plot
            self._plot_plot(write, serie, plot)

    def _plot_plot(self, write, serie, plot):
        self._plot = plot
        elements = plot["elements"]

        # early abort if the plot is empty
        if not elements:
            return

        # Vertical autoscaling
        the_min = float("inf")
        the_max = float("-inf")
        for element in elements:
            for column_name in element["data"]:
                mi, ma = serie[column_name].data[0].min_max()
                if mi < the_min:
                    the_min = mi
                if ma > the_max:
                    the_max = ma

        # case of columns containing only None values
        if the_max < the_min:
            the_min = the_max = 0.00

        # case of contant values
        if the_min == the_max:
            the_min -= 1
            the_max += 1

        tics = list(make_tics_from_range(7, the_min, the_max))
        a, tics, b = tics[0], tics[1:-1], tics[-1]

        write(f"set yrange [{a[0]}:{b[0]}]\n")
        tics = [f"\"{i[1]}\" {i[0]}" for i in tics]
        write(f"set ytics ({','.join(tics)})\n")


        write("plot ")
        sep = ""
        for element in elements:
            write(sep)
            self._plot_element(write, serie, element)
            sep = ",\\\n"
        write("\n")

    def _plot_element(self, write, serie, element):
        kind = element["kind"]
        color, x, *data = self._get_field_numbers(
                element["color"],
                self._multiplot["x"],
                *element["data"]
                )

        mode = self._multiplot["mode"]
        if mode == Multiplot.LABEL:
            command = _GNUPlotDataElement(kind, ["(column(0))", *data])
        elif mode == Multiplot.XY:
            command = _GNUPlotDataElement(kind, [x, *data])
        else:
            raise NotImplementedError()

        command.title = element["data"][-1]
        if color is not None:
            command.lc_rgbcolor_variable(f"(${color}>0?GREEN:RED)")
        else:
            # Automatic color
            # Only implemented for candlesticks
            if kind == "candlestick":
                command.lc_rgbcolor_variable(f"(${data[3]}>${data[0]}?GREEN:RED)")
                command.fs = "solid"

        # ???
        # for k,v in kwargs.items():
        #    setattr(command, k, v)
        
        # For candlesticks:
        # command.lc_rgbcolor_variable(f"(${entries[3]}>${entries[0]}?GREEN:RED)")
        # command.title = "" # ???
        # command.fs = "solid"

        write("$MyData ")
        write(str(command))

    def _get_field_numbers(self, *field_names):
        """
        Map column names to their index+1 (gnuplot columns are 1-based)
        """
        serie = self._serie
        headings = serie.headings
        return [1+headings.index(field_name) if field_name is not None else None for field_name in field_names]

    def _make_fields(self, *field_names):
        return ":".join(map(str, self._get_field_numbers(*field_names)))

def gnuplot(multiplot, *, log=None, Process=_Process, cmd=GNUPLOT_CMD, **kwargs):
    with Process(cmd) as p:
        stdin_write = p.stdin.write
        if log is not None:
            def writer(str):
                log(str)
                stdin_write(str)
        else:
            writer = stdin_write
        visitor = _GNUPlotVisitor(writer, **kwargs)
        visitor.plot(multiplot)
