import unittest

from fin.seq import table
from fin.seq import column
from fin.seq import expr

LEN=10
NAME="My name"
F = lambda rowcount, c1 : column.Column((a*10 for a in c1))
FN = lambda rowcount, *cols : column.Column(None, (sum(v) for v in zip(*cols)))

# ======================================================================
# Expr
# ======================================================================
class TestExpr(unittest.TestCase):
    def setUp(self):
        t = self.table = table.Table(LEN)
        t.add_column(column.Column("A", [*range(0,LEN)]))
        t.add_column(column.Column("B", [*range(10, LEN+10)]))
        t.add_column(column.Column("C", [*range(20, LEN+20)]))

    def eval(self, e):
        result = self.table.reval(e)

        # Test fiew core properties
        for e in result:
            self.assertEqual(len(e), LEN)
            self.assertIsInstance(e, column.Column)

        return result

    def test_data(self):
        """
        The `c` expression produces a Column instance from a sequence.
        """
        SEQ=[*range(100, 100+LEN)]
        col, = self.eval(expr.c(SEQ, name=NAME))

        self.assertSequenceEqual(col, SEQ)
        self.assertEqual(col.name, NAME)

    def test_constant(self):
        """
        The `constant` expression produces a sequence of identical values.
        """
        N = 5
        col, = self.eval(expr.constant(N, name=NAME))

        self.assertSequenceEqual(col, [N]*LEN)
        self.assertEqual(col.name, NAME)

    def test_apply(self):
        """
        The `apply` expression applies a function on the remaining args.
        """
        col, = self.eval((expr.apply(FN, name=NAME), "A", "B"))

        self.assertSequenceEqual(col, (10, 12, 14, 16, 18, 20, 22, 24, 26, 28))
        self.assertEqual(col.name, NAME)

    def test_call(self):
        """
        The `call` expression calls a function with the given args, but with the
        table rowcount injected.
        """
        FN = lambda rowcount, x : range(x, x+rowcount)
        col, = self.eval((expr.call(FN, 10, name=NAME)))

        self.assertSequenceEqual(col, range(10, 10+LEN))
        self.assertEqual(col.name, NAME)

    def test_spread(self):
        """
        The `spread` expression apply function to each argument in its turn.
        """
        FN = lambda rowcount, c : expr.c([v+100 for v in c])
        c1,c2 = self.eval((expr.spread(FN), "A", "B"))

        self.assertSequenceEqual(c1, range(100, 100+LEN))
        self.assertSequenceEqual(c2, range(110, 110+LEN))

