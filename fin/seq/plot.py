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
    def __init__(self, data_column):
        self._data_column = data_column

    def accept(self, visitor):
        visitor.visit_line_chart(self)

class Bar:
    def __init__(self, data_column):
        self._data_column = data_column

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
class _Multiplot:
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
        write = self._write

        fields = self._make_fields(
                self._multiplot._x_axis_column,
                chart._data_column
                )
        label = chart._data_column

        write(f'$MyData using {fields} title "{label}" with lines')

    def visit_bar_chart(self, chart):
        write = self._write

        fields = self._make_fields(
                self._multiplot._x_axis_column,
                chart._data_column
                )

        label = chart._data_column

        write(f'$MyData using {fields} title "{label}" with boxes fs solid 0.9')

    def visit_impulse_chart(self, chart):
        write = self._write

        x, y, flag = self._get_field_numbers(
                self._multiplot._x_axis_column,
                chart._data_column,
                chart._flag_column,
                )

        label = chart._data_column
        if flag:
            write(f'$MyData using {x}:{y}:(${flag}>0?GREEN:RED) title "{label}" with impulses lc rgbcolor variable')
        else:
            write(f'$MyData using {x}:{y} title "{label}" with impulses')

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

class GNUPlot:
    """
    A driver that sends data to a GNUPlot process.

    This class is designed to be used as a context manager.
    """
    def __init__(
            self,
            table,
            x_axis_column,
            *,
            log=None,
            Process=_Process
            ):
        self._table = table.copy()
        self._x_axis_column = x_axis_column
        self._Process = Process
        self._log = log # For testing purposes

    def __enter__(self):
        self._multiplot = _Multiplot(self._table, self._x_axis_column)
        return self._multiplot

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._Process(['gnuplot', '-p']) as p:
            log = self._log
            stdin_write = p.stdin.write
            if log is not None:
                def writer(str):
                    log(str)
                    stdin_write(str)
            else:
                writer = stdin_write
            visitor = _GNUPlotVisitor(writer)
            self._multiplot.accept(visitor)

