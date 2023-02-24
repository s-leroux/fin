"""
Plot 2D curves using GNUPlot
"""
from fin.seq import formatter
import asyncio

PIPE = asyncio.subprocess.PIPE

# ======================================================================
# Plot elements
# ======================================================================
class WithLines:
    def __init__(self, data_index, label):
        self._data_index = data_index
        self._label = label

    def get_command(self, x_axis_index):
        x = x_axis_index+1       # GNUPlot index are 1-based!
        y = self._data_index+1
        label = self._label
        return f'$MyData using {x}:{y} title "{label}" with lines'

# ======================================================================
# A plot
# ======================================================================
class _Plot:
    def __init__(self, relative_height, table, x_axis_index):
        self.relative_height = relative_height
        self._table = table
        self._x_axis_index = x_axis_index
        self._elements = []

    def draw(self, column_index_or_name):
        """
        Add a new drawing in a plot.
        """
        column_index = self._table._get_column_index(column_index_or_name)
        label = self._table.names()[column_index]
        self._elements.append(
                WithLines(column_index, label)
                )

    def write_to(self, writer):
        writer("plot ")
        sep = ""
        for element in self._elements:
            writer(sep)
            writer(element.get_command(self._x_axis_index))
            sep = ",\\\n"
        writer("\n")

# ======================================================================
# A Multiplot instance
# ======================================================================
class _Multiplot:
    """
    Interface to a multiplot.

    A multiplot is made of 1-to-n plots. All plots are based on the same table
    and uses the same x-axis.
    """
    def __init__(self, table, x_axis_index_or_name):
        self._table = table
        self._x_axis_index = table._get_column_index(x_axis_index_or_name)

        self._plots = []

    def write_to(self, writer):
        """
        Send the batch commands to the GNUPlot process.
        """
        self._write_preamble_to(writer)
        self._write_data_to(writer)
        self._write_plots_to(writer)

    def new_plot(self, relative_height=1):
        plot = _Plot(relative_height, self._table, self._x_axis_index)
        self._plots.append(plot)

        return plot

    def _write_preamble_to(self, writer):
        writer("\n")
        writer("reset\n")
        writer("set multiplot\n")

    def _write_data_to(self, writer):
        data = formatter.CSV(delimiter=" ").format(self._table)
        writer("$MyData << EOD\n")
        writer(data)
        writer("EOD\n")

    def _write_plots_to(self, writer):
        total_height = 0
        for plot in self._plots:
            total_height += plot.relative_height
        current_height = total_height
        for plot in self._plots:
            prev_height = current_height
            current_height -= plot.relative_height

            top = 0.80*prev_height/total_height + 0.10
            bottom = 0.80*current_height/total_height + 0.10
            writer(f"set lmargin at screen 0.1000\n")
            writer(f"set rmargin at screen 0.9000\n")
            writer(f"set tmargin at screen {top:1.4f}\n")
            writer(f"set bmargin at screen {bottom:1.4f}\n")
            plot.write_to(writer)

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

class GNUPlot:
    """
    A driver that sends data to a GNUPlot process.

    This class is designed to be used as a context manager.
    """
    def __init__(
            self,
            table,
            x_axis_index_or_name,
            *,
            log=None,
            Process=_Process
            ):
        self._table = table
        self._x_axis_index_or_name = x_axis_index_or_name
        self._Process = Process
        self._log = log # For testing purposes

    def __enter__(self):
        self._multiplot = _Multiplot(self._table, self._x_axis_index_or_name)
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
            self._multiplot.write_to(writer)

