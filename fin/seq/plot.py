"""
Plot 2D curves using GNUPlot
"""
from fin.seq import formatter
import asyncio
import math
import collections
from numbers import Number

PIPE = asyncio.subprocess.PIPE

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
class Line:
    def __init__(self, data_column, flag_column=None):
        self._data_column = data_column
        self._flag_column = flag_column

    def data_columns(self):
        return ( self._data_column, )

    def accept(self, visitor):
        visitor.visit_line_chart(self)

class Bar:
    def __init__(self, data_column, flag_column=None):
        self._data_column = data_column
        self._flag_column = flag_column

    def data_columns(self):
        return ( self._data_column, )

    def accept(self, visitor):
        visitor.visit_bar_chart(self)

class Impulse:
    def __init__(self, data_column, flag_column=None):
        self._data_column = data_column
        self._flag_column = flag_column

    def data_columns(self):
        return ( self._data_column, )

    def accept(self, visitor):
        visitor.visit_impulse_chart(self)

class Candlestick:
    def __init__(self, open_price_column, low_price_column, high_price_column, close_price_column):
        self._open_price_column = open_price_column
        self._low_price_column = low_price_column
        self._high_price_column = high_price_column
        self._close_price_column = close_price_column

    def data_columns(self):
        return (
                self._open_price_column,
                self._low_price_column,
                self._high_price_column,
                self._close_price_column,
                )

    def accept(self, visitor):
        visitor.visit_candlestick_chart(self)

# ======================================================================
# A plot
# ======================================================================
class _Plot:
    def __init__(self, relative_height, table):
        self.relative_height = relative_height
        self._table = table
        self._elements = []
        self.poi = Tics()

    def accept(self, visitor):
        visitor.visit_plot(self)

    def add_poi(self, *items):
        self.poi.extend(items)

    def draw_line(self, data_column):
        """
        Add a new line drawing on a plot.
        """
        self._elements.append(
                Line(data_column)
                )

        column = self._table[data_column]
        self.add_poi(*column.min_max(), column[-1])

    def draw_bar(self, data_column):
        """
        Add a new bargraph on the plot.
        """
        self._elements.append(
                Bar(data_column)
                )

    def draw_impulse(self, data_column, flag_color=None):
        """
        Add a new impulse graph on the plot.
        """
        self._elements.append(
                Impulse(data_column, flag_color)
                )

    def draw_candlestick(self, open_price_column, low_price_column, high_price_column, close_price_column):
        """
        Add a new bargraph on the plot.
        """
        self._elements.append(
                Candlestick(open_price_column, low_price_column, high_price_column, close_price_column)
                )

# ======================================================================
# A Multiplot instance
# ======================================================================
class Multiplot:
    """
    Interface to a multiplot.

    A multiplot is made of 1-to-n plots. All plots are based on the same table
    and uses the same x-axis.
    """
    LABEL = "LABEL"

    def __init__(self, table, x_axis_column, *, mode=None):
        if mode is None:
            mode = Multiplot.LABEL

        self._table = table
        self._x_axis_column = x_axis_column
        self.mode = mode

        self._plots = []

        self._title = table.name()

    def accept(self, visitor):
        visitor.visit_multiplot(self)

    def set_title(self, title):
        self._title = title

    def new_plot(self, relative_height=1):
        plot = _Plot(relative_height, self._table)
        self._plots.append(plot)

        return plot

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
        self._attr = {}
        self.title = None
        self.lc = None # linecolor
        self.fs = None # fillstyle

    def lc_rgbcolor_variable(self, entry):
        self.lc = "rgbcolor variable"
        self._entries.append(entry)

    def __str__(self):
        """
        Convert the receiver to a string representing a valid data plot element
        """
        kind = self._kind
        entries = ":".join(map(str, self._entries))
        parts = []
        parts.append(f"using {entries} with {kind}")

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

    def visit_multiplot(self, mp):
        write = self._write
        table = mp._table

        self._multiplot = mp
        self._table = table

        # write the preamble
        write("\n")
        write("reset\n")
        write(f"set term {self._term} size {self._width},{self._height} font \"{self._font}\"\n")
        write("set style textbox opaque\n")
        write("set multiplot\n")
        write("set key left top\n")

        write("RED=0x800000\n")
        write("GREEN=0x008000\n")

        # xtics
        if mp.mode == Multiplot.LABEL:
            write(f"set xrange [0:{table.rows()+1}]\n")
            x_column = table[mp._x_axis_column]
            x_tics = make_tics_from_sequence(5, x_column)
        else:
            raise NotImplementedError()

        # Grid
        write("set grid xtics ytics\n")

        # write the data
        data = formatter.CSV(delimiter=" ").format(table)
        write("$MyData << EOD\n#")
        write(data)
        write("EOD\n")

        # write the plots
        total_height = 0
        for plot in mp._plots:
            total_height += plot.relative_height
        current_height = total_height
        n = len(mp._plots)
        i = 0
        for plot in mp._plots:
            i += 1

            # Plot boundaries
            prev_height = current_height
            current_height -= plot.relative_height

            top = 0.80*prev_height/total_height + 0.10
            bottom = 0.80*current_height/total_height + 0.10
            # POI
            if len(plot.poi):
                write(f"set tmargin at screen {top:1.4f}\n")
                write(f"set bmargin at screen {bottom:1.4f}\n")
                write(f"set lmargin at screen 0.9000\n")
                write(f"set rmargin at screen 0.9900\n")
                write(f"unset label\n")
                for poi in plot.poi:
                    write(f"set label \"{poi[1]}\" at graph 1.00, first {poi[0]} offset graph 0.1, 0 point ps 1 pt 1 right boxed\n")
                # write(f"replot\n")
            write(f"set lmargin at screen 0.1000\n")
            write(f"set rmargin at screen 0.9000\n")
            write(f"set tmargin at screen {top:1.4f}\n")
            write(f"set bmargin at screen {bottom:1.4f}\n")

            # Plot title
            if i == 1:
                title = mp._title
                if title:
                    write(f"set title \"{title}\" noenhanced\n")
            else:
                write("set title\n")

            # xtics
            if i < n:
                x_tics_labels = [f"\"\" {i}" for i, v in x_tics]
            else:
                x_tics_labels = [f"\"{v}\" {i}" for i, v in x_tics]

            write(f'set xtics axis ({",".join(x_tics_labels)})\n')

            # Draw the plot
            plot.accept(self)



    def visit_plot(self, plot):
        write = self._write

        self._plot = plot

        # early abort if the plot is empty
        if not plot._elements:
            return

        # Veertical autoscaling
        the_min = float("inf")
        the_max = float("-inf")
        for element in plot._elements:
            for column_name in element.data_columns():
                mi, ma = self._table[column_name].min_max()
                if mi < the_min:
                    the_min = mi
                if ma > the_max:
                    the_max = ma

        # case of colmn containing only None values
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
        for element in plot._elements:
            write(sep)
            element.accept(self)
            sep = ",\\\n"
        write("\n")

    def visit_line_chart(self, chart):
        return self._visit_xy_chart("lines", chart)

    def visit_bar_chart(self, chart):
        return self._visit_xy_chart("boxes", chart, fs="solid 0.9")

    def visit_impulse_chart(self, chart):
        return self._visit_xy_chart("impulses", chart)

    def _visit_xy_chart(self, kind, chart, **kwargs):
        flag, x, y = self._get_field_numbers(
                chart._flag_column,
                self._multiplot._x_axis_column,
                chart._data_column,
                )

        if self._multiplot.mode == Multiplot.LABEL:
            element = _GNUPlotDataElement(kind, ["(column(0))", y])
        else:
            raise NotImplementedError()

        element.title = chart._data_column
        if flag:
            element.lc_rgbcolor_variable(f"(${flag}>0?GREEN:RED)")

        for k,v in kwargs.items():
            setattr(element, k, v)

        write = self._write
        write("$MyData ")
        write(str(element))

    def visit_candlestick_chart(self, chart):
        x, *entries = self._get_field_numbers(
                self._multiplot._x_axis_column,
                chart._open_price_column,
                chart._low_price_column,
                chart._high_price_column,
                chart._close_price_column
                )
        if self._multiplot.mode == Multiplot.LABEL:
            element = _GNUPlotDataElement("candlesticks", ["(column(0))", *entries])
        else:
            raise NotImplementedError()

        element.lc_rgbcolor_variable(f"(${entries[3]}>${entries[0]}?GREEN:RED)")
        element.title = "" # ???
        element.fs = "solid"

        write = self._write
        write("$MyData ")
        write(str(element))

    def _get_field_numbers(self, *field_names):
        table = self._table
        return [1+table._get_column_index(field_name) if field_name is not None else None for field_name in field_names]

    def _make_fields(self, *field_names):
        return ":".join(map(str, self._get_field_numbers(*field_names)))

def gnuplot(multiplot, *, log=None, Process=_Process, **kwargs):
    with Process(['gnuplot', '-p']) as p:
        stdin_write = p.stdin.write
        if log is not None:
            def writer(str):
                log(str)
                stdin_write(str)
        else:
            writer = stdin_write
        visitor = _GNUPlotVisitor(writer, **kwargs)
        multiplot.accept(visitor)
