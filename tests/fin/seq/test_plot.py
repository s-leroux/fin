import unittest

from fin.seq import plot
from fin.seq import table, column

# ======================================================================
# Utilities
# ======================================================================
class TestPrefixNumber(unittest.TestCase):
    def test_prefix_number(self):
        use_cases = (
                (1.2, "1.2"),
                (12, "12"),
                (123, "123"),
                (1234, "1.234k"),
                (12345, "12.345k"),
                (123456, "123.456k"),
                (1234567, "1.235M"),

                # corner cases:
                (152.0, "152"),
                )
        for x,expected in use_cases:
            with self.subTest(x=x):
                actual = plot.prefix_number(x)
                self.assertEqual(actual, expected)

class TestMakeTics(unittest.TestCase):
    def test_make_tics(self):
        use_cases = (
                (36,48),
                (1912,4921),
                (0, 0.055),
                )
        for a,b in use_cases:
            with self.subTest(a=a,b=b):
                actual = plot.make_tics_from_range(10, a, b)
                msg = str(actual)
                self.assertLessEqual(len(actual), 10, msg)
                self.assertGreaterEqual(len(actual), 6, msg)
                self.assertLessEqual(actual[0][0], a, msg)
                self.assertGreaterEqual(actual[1][0], a, msg)
                self.assertGreaterEqual(actual[-1][0], b, msg)
                self.assertLessEqual(actual[-2][0], b, msg)
                self.assertSequenceEqual(actual, sorted(actual), msg)

# ======================================================================
# _process
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
class TestGNUPlotDataElement(unittest.TestCase):
    def test_element_core(self):
        el = plot._GNUPlotDataElement("impulses", [1,2])
        expected = "using 1:2 with impulses notitle"

        self.assertEqual(str(el), expected)

    def test_element_title(self):
        el = plot._GNUPlotDataElement("impulses", [1,2])
        el.title = "My title"

        expected = "using 1:2 with impulses title \"My title\""

        self.assertEqual(str(el), expected)

    def test_element_core_lc_regbolor_variable(self):
        el = plot._GNUPlotDataElement("impulses", [1,2])
        el.lc_rgbcolor_variable("(column(1))")

        expected = "using 1:2:(column(1)) with impulses notitle lc rgbcolor variable"

        self.assertEqual(str(el), expected)

import io
from textwrap import dedent
class TestGNUPlot(unittest.TestCase):
    def setUp(self):
        self.t = t = table.Table(5)
        t.add_column("T", column.call(range))
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
        self.multiplot = plot.Multiplot(t, "T")

    def test_preamble(self):
        plot.gnuplot(self.multiplot, Process=self.Process)
        self.assertIn("\nreset\n", self.capture.getvalue())
        self.assertIn("\nset multiplot\n", self.capture.getvalue())

    def test_data(self):
        plot.gnuplot(self.multiplot, Process=self.Process)
        expected="""\
            $MyData << EOD
            #T D V
            0 2 1
            1 2 1
            2 2 1
            3 2 1
            4 2 1
            EOD
        """

        self.assertIn(dedent(expected), self.capture.getvalue())

    def test_plot_line(self):
        """
        The 'plot' command must be present.
        """
        myplot = self.multiplot.new_plot()
        myplot.draw_line("V")
        plot.gnuplot(self.multiplot, Process=self.Process)

        expected='\nplot $MyData using (column(0)):3 with lines title "V"\n'

        self.assertIn(expected, self.capture.getvalue())

    def test_plot_line2(self):
        """
        The 'plot' command can display two line charts.
        """
        myplot = self.multiplot.new_plot()
        myplot.draw_line("V")
        myplot.draw_line("T")
        plot.gnuplot(self.multiplot, Process=self.Process)

        expected=(
                '\n'
                'plot $MyData using (column(0)):3 with lines title "V",\\\n'
                '$MyData using (column(0)):1 with lines title "T"\n'
                )

        self.assertIn(expected, self.capture.getvalue())

    def test_plot_bar(self):
        """
        The 'plot' command must be present.
        """
        myplot = self.multiplot.new_plot()
        myplot.draw_bar("V")
        plot.gnuplot(self.multiplot, Process=self.Process)

        expected='\nplot $MyData using (column(0)):3 with boxes title "V"'

        self.assertIn(expected, self.capture.getvalue())

    def test_margins(self):
        """
        The margins must be set.
        """
        myplot = self.multiplot.new_plot(relative_height=4)
        myplot = self.multiplot.new_plot(relative_height=1)
        plot.gnuplot(self.multiplot, Process=self.Process)

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
