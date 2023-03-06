"""
Plot 2D curves using GNUPlot
"""
from fin.seq import formatter
import asyncio

PIPE = asyncio.subprocess.PIPE

# ======================================================================
# Plot elements
# ======================================================================
class Line:
    def __init__(self, data_column, flag_column=None):
        self._data_column = data_column
        self._flag_column = flag_column

    def accept(self, visitor):
        visitor.visit_line_chart(self)

class Bar:
    def __init__(self, data_column, flag_column=None):
        self._data_column = data_column
        self._flag_column = flag_column

    def accept(self, visitor):
        visitor.visit_bar_chart(self)

class Impulse:
    def __init__(self, data_column, flag_column=None):
        self._data_column = data_column
        self._flag_column = flag_column

    def accept(self, visitor):
        visitor.visit_impulse_chart(self)

class Candlestick:
    def __init__(self, open_price_column, low_price_column, high_price_column, close_price_column):
        self._open_price_column = open_price_column
        self._low_price_column = low_price_column
        self._high_price_column = high_price_column
        self._close_price_column = close_price_column

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

    def accept(self, visitor):
        visitor.visit_plot(self)

    def draw_line(self, data_column):
        """
        Add a new line drawing on a plot.
        """
        self._elements.append(
                Line(data_column)
                )

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
    def __init__(self, table, x_axis_column):
        self._table = table
        self._x_axis_column = x_axis_column

        self._plots = []

        self._title = None

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
        self.lc = None

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

        if self.title:
            parts.append(f"title \"{self.title}\"")
        if self.lc:
            parts.append(f"lc {self.lc}")

        return " ".join(parts)

class _GNUPlotVisitor:
    """
    The class that handle conversion from the data model to a GNUPlot script.
    """
    def __init__(self, write):
        self._write = write

    def visit_multiplot(self, mp):
        write = self._write
        table = mp._table

        self._multiplot = mp
        self._table = table

        # write the preamble
        write("\n")
        write("reset\n")
        write("set multiplot\n")
        write("set key left top\n")

        write("RED=0x800000\n")
        write("GREEN=0x008000\n")

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

            # Plot format
            if i < n:
                write("set format x \"\"\n")
            else:
                write("set format x\n")
                write("set xtics axis\n")

            # Drae the plot
            plot.accept(self)

    def visit_plot(self, plot):
        write = self._write

        self._plot = plot

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
        write = self._write
        flag, *entries = self._get_field_numbers(
                chart._flag_column,
                self._multiplot._x_axis_column,
                chart._data_column,
                )

        element = _GNUPlotDataElement(kind, entries)
        element.title = chart._data_column
        if flag:
            element.lc_rgbcolor_variable(f"(${flag}>0?GREEN:RED)")

        for k,v in kwargs.items():
            setattr(element, k, v)

        write("$MyData ")
        write(str(element))

    def visit_candlestick_chart(self, chart):
        write = self._write

        fields = self._get_field_numbers(
                self._multiplot._x_axis_column,
                chart._open_price_column,
                chart._low_price_column,
                chart._high_price_column,
                chart._close_price_column
                )
        field_spec = (
                f"{fields[0]}:{fields[1]}:{fields[2]}:{fields[3]}:{fields[4]}"
                f":(${fields[4]}>${fields[1]}?GREEN:RED)"
                )

        label = "" # ???
        write(f'$MyData using {field_spec} title "{label}" with candlesticks lc rgbcolor variable')

    def _get_field_numbers(self, *field_names):
        table = self._table
        return [1+table._get_column_index(field_name) if field_name is not None else None for field_name in field_names]

    def _make_fields(self, *field_names):
        return ":".join(map(str, self._get_field_numbers(*field_names)))

def gnuplot(multiplot, *, log=None, Process=_Process):
    with Process(['gnuplot', '-p']) as p:
        stdin_write = p.stdin.write
        if log is not None:
            def writer(str):
                log(str)
                stdin_write(str)
        else:
            writer = stdin_write
        visitor = _GNUPlotVisitor(writer)
        multiplot.accept(visitor)
