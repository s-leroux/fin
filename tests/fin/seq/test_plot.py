import unittest

from fin.seq import plot
from fin.seq import table

# ======================================================================
# _Process
# ======================================================================
import subprocess
class TestProcess(unittest.TestCase):
    def test_run(self):
        p = plot._Process(["cat", "-n"], stdout=subprocess.PIPE)
        p.stdin.write("Hello\n")
        self.assertEqual(p._process.communicate()[0], '     1\tHello\n')
        p.close()

    def test_context_manager(self):
        with plot._Process(["cat", "-n"], stdout=subprocess.PIPE) as p:
            p.stdin.write("Hello\n")
            self.assertEqual(p._process.communicate()[0], '     1\tHello\n')

# ======================================================================
# GNUPlot
# ======================================================================
import io
from textwrap import dedent

class TestGNUPlot(unittest.TestCase):
    def setUp(self):
        self.t = t = table.Table(5)
        t.add_column("D", 2)
        t.add_column("V", 1)

        capture = io.StringIO()
        class MyProcess:
            def __init__(self,*args):
                self.stdin = capture

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        self.capture = capture = io.StringIO()
        self.Process = MyProcess

    def test_preamble(self):
        p = plot.GNUPlot(self.t, "D", Process=self.Process)
        with p as mp:
            pass

        self.assertIn("\nreset\n", self.capture.getvalue())
        self.assertIn("\nset multiplot\n", self.capture.getvalue())

    def test_data(self):
        p = plot.GNUPlot(self.t, "D", Process=self.Process)
        with p as mp:
            pass
        
        expected="""\
            $MyData << EOD
            # D V
            0 2 1
            1 2 1
            2 2 1
            3 2 1
            4 2 1
            EOD
        """

        self.assertIn(dedent(expected), self.capture.getvalue())

    def test_plot(self):
        """
        The 'plot' command must be present.
        """
        p = plot.GNUPlot(self.t, "#", Process=self.Process)
        with p as mp:
            myplot = mp.new_plot()
            myplot.draw("V")
        
        expected='\nplot $MyData using 1:3 title "V" with lines\n'

        self.assertIn(expected, self.capture.getvalue())

    def test_plot2(self):
        """
        The 'plot' command can display two line charts.
        """
        p = plot.GNUPlot(self.t, "#", Process=self.Process)
        with p as mp:
            myplot = mp.new_plot()
            myplot.draw("V")
            myplot.draw("#")

        expected=(
                '\n'
                'plot $MyData using 1:3 title "V" with lines,\\\n'
                '$MyData using 1:1 title "#" with lines\n'
                )

        self.assertIn(expected, self.capture.getvalue())

    def test_margins(self):
        """
        The margins must be set.
        """
        p = plot.GNUPlot(self.t, "#", Process=self.Process)
        with p as mp:
            myplot = mp.new_plot(relative_height=4)
            myplot = mp.new_plot(relative_height=1)

        expected="""\
            set lmargin at screen 0.1000
            set rmargin at screen 0.9000
            set tmargin at screen 0.9000
            set bmargin at screen 0.2600
            (.|\\n)*
            set lmargin at screen 0.1000
            set rmargin at screen 0.9000
            set tmargin at screen 0.2600
            set bmargin at screen 0.1000
            """
        self.assertRegex(self.capture.getvalue(), dedent(expected))
