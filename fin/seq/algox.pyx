# cython: boundscheck=False
# cython: cdivision=True

"""
Cython implementation of common algorithms on columns.
"""
from __future__ import print_function
# Above ^^^^^^^^^^^^^^^^^^^^:
# Cython 0.26.1 does not recognize the Python3 semantic for the print()
# function without that import.
# See: https://stackoverflow.com/questions/19185338/cython-error-compiling-with-print-function-parameters

from fin.mathx cimport alloc, isnan, NaN
from fin.seq cimport column
from fin.seq import column

cdef extern from "<alloca.h>":
    void *alloca(size_t size)

# ======================================================================
# Common base classes
# ======================================================================
cdef class Functor1:
    """
    A simple functor accepting one-column argument.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, double* dst, const double* src):
        pass

    cdef make_name(self, col):
        return f"{repr(self)}, {column.get_column_name(col)}"

    def __call__(self, rowcount, sequence):
        cdef column.FColumn fcolumn = column.as_fcolumn(sequence)
        cdef double[::1] values = fcolumn.values
        cdef unsigned l = len(values)
        cdef double[::1] result = alloc(l)

        self.eval(l, &result[0], &values[0])

        return column.FColumn(self.make_name(sequence), result)

cdef class Functor2:
    """
    A simple functor accepting two-column arguments.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, double* dst, const double* src1, const double* src2):
        pass

    cdef make_name(self, col1, col2):
        return f"{repr(self)}, {column.get_column_name(col1)}, {column.get_column_name(col2)}"

    def __call__(self, rowcount, sequence1, sequence2):
        cdef column.FColumn fcolumn1 = column.as_fcolumn(sequence1)
        cdef column.FColumn fcolumn2 = column.as_fcolumn(sequence2)
        cdef const double *src1 = &fcolumn1.values[0]
        cdef const double *src2 = &fcolumn2.values[0]
        cdef unsigned l = len(fcolumn1)

        assert len(fcolumn1) == l

        cdef double[::1] result = alloc(l)
        self.eval(l, &result[0], src1, src2)

        return column.FColumn(self.make_name(sequence1, sequence2), result)

cdef class Functor2_3:
    """
    A simple functor accepting two-column arguments and returning three columns.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l,
            double* dst1, double* dst2, double* dst3,
            const double* src1, const double* src2):
        pass

    cdef make_names(self, col1, col2):
        return [
                "A",
                "B",
                "C"
                ]

    def __call__(self, rowcount, sequence1, sequence2):
        cdef column.FColumn fcolumn1 = column.as_fcolumn(sequence1)
        cdef column.FColumn fcolumn2 = column.as_fcolumn(sequence2)
        cdef const double *src1 = &fcolumn1.values[0]
        cdef const double *src2 = &fcolumn2.values[0]
        cdef unsigned l = len(fcolumn1)

        assert len(fcolumn1) == l

        cdef double[::1] dst1 = alloc(l)
        cdef double[::1] dst2 = alloc(l)
        cdef double[::1] dst3 = alloc(l)
        self.eval(l, &dst1[0], &dst2[0], &dst3[0], src1, src2)
        names = self.make_names(sequence1, sequence2);

        return [
                column.FColumn(names[0], dst1),
                column.FColumn(names[1], dst2),
                column.FColumn(names[2], dst3),
                ]

cdef class Functor3:
    """
    A simple functor accepting three-column arguments.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, double* dst, const double* src1, const double* src2, const double* src3):
        pass

    cdef make_name(self, col1, col2, col3):
        return f"{repr(self)}, {column.get_column_name(col1)}, {column.get_column_name(col2)}, {column.get_column_name(col3)}"

    def __call__(self, rowcount, sequence1, sequence2, sequence3):
        cdef column.FColumn fcolumn1 = column.as_fcolumn(sequence1)
        cdef column.FColumn fcolumn2 = column.as_fcolumn(sequence2)
        cdef column.FColumn fcolumn3 = column.as_fcolumn(sequence3)
        cdef const double *src1 = &fcolumn1.values[0]
        cdef const double *src2 = &fcolumn2.values[0]
        cdef const double *src3 = &fcolumn3.values[0]
        cdef unsigned l = len(fcolumn1)

        assert len(fcolumn1) == l

        cdef double[::1] result = alloc(l)
        self.eval(l, &result[0], src1, src2, src3)

        return column.FColumn(self.make_name(sequence1, sequence2, sequence3), result)

cdef class FunctorN:
    """
    A simple functor accepting N-column argument.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, double* dst, unsigned m, (const double*)[] src):
        pass

    cdef make_name(self, sequences):
        return f"{repr(self)}"

    def __call__(self, rowcount, *sequences):
        cdef list seqs = [column.as_fcolumn(s) for s in sequences]
        cdef unsigned m = len(seqs)
        cdef const double** v= <const double**>alloca(m*sizeof(double*))

        cdef unsigned i
        for i in range(m):
            ci = <column.FColumn>seqs[i]
            assert len(ci) == rowcount
            v[i] = &ci.values[0]
        cdef unsigned l = rowcount
        cdef double[::1] result = alloc(l)

        self.eval(l, &result[0], m, v)

        return column.FColumn(self.make_name(sequences), result)

cdef class RowFunctor1(Functor1):
    """
    A simple functor accepting one column argument.

    Output values are evaluated one by one calling repeatidly `eval_one_row`.
    This method should be overrided by the actual implementation.
    """
    cdef double eval_one_row(self, double src):
        return NaN

    cdef void eval(self, unsigned l, double* dst, const double* src):
        cdef unsigned i = 0
        for i in range(l):
            dst[i] = self.eval_one_row(src[i])

cdef class RowFunctorN(FunctorN):
    """
    A simple functor accepting N column arguments.

    Output values are evaluated one by one calling repeatidly `eval_one_row`.
    This method should be overrided by the actual implementation.
    """
    cdef double eval_one_row(self, unsigned m, double[] src):
        return NaN

    cdef void eval(self, unsigned l, double* dst, unsigned m, (const double*)[] src):
        cdef double[::1] buffer = alloc(m)
        cdef double* base = &buffer[0]

        cdef unsigned i = 0
        cdef unsigned j = 0
        for i in range(l):
            for j in range(m):
                base[j] = src[j][i]
            dst[i] = self.eval_one_row(m, base)

cdef class WindowFunctor1(Functor1):
    cdef unsigned n

    def __init__(self, n):
        self.n = n

    cdef double eval_one_window(self, unsigned n, const double *src):
        return NaN

    cdef void eval(self, unsigned l, double* dst, const double* src):
        cdef unsigned n = self.n
        cdef unsigned i = n-1
        cdef unsigned j = 0
        while i < l:
            dst[i] = self.eval_one_window(n, &src[j])
            i += 1
            j += 1

# ======================================================================
# Test functions
# ======================================================================
cdef class _Sum(WindowFunctor1):
    cdef double eval_one_window(self, unsigned n, const double *src):
        cdef double acc = 0.0
        cdef unsigned i
        for i in range(n):
            acc += src[i]
        return acc

# ======================================================================
# Arithmetic
# ======================================================================
cdef class add(RowFunctorN):
    """
    Row-by-row addition over n-columns.

    Formally:
    * (add, ) => 0
    * (add, X) => X
    * (add, X, Y) => (X+Y)
    * (add, X, Y, Z) => (add, (add, X, Y), Z)
    """
    cdef double eval_one_row(self, unsigned m, double[] src):
        cdef double acc = 0.0
        cdef unsigned i
        for i in range(m):
            acc += src[i]

        return acc

cdef class sub(RowFunctorN):
    """
    Row-by-row substraction over n-columns.

    Formally:
    * (sub, ) => 0
    * (sub, X) => -X
    * (sub, X, Y) => (X-Y)
    * (sub, X, Y, Z) => (sub, (sub, X, Y), Z)
    """
    cdef double eval_one_row(self, unsigned m, double[] src):
        if m == 0:
            return 0.0

        cdef double acc = src[0]
        if m == 1:
            return -acc

        cdef unsigned i
        for i in range(1, m):
            acc -= src[i]

        return acc

cdef class mul(RowFunctorN):
    """
    Row-by-row multiplication over n-columns.

    Formally:
    * (mul, ) => 1
    * (mul, X) => X
    * (mul, X, Y) => (X*Y)
    * (mul, X, Y, Z) => (mul, (mul, X, Y), Z)
    """
    cdef double eval_one_row(self, unsigned m, double[] src):
        cdef double acc = 1
        cdef unsigned i
        for i in range(m):
            acc *= src[i]

        return acc

cdef class div(RowFunctorN):
    """
    Row-by-row division over n-columns.

    Formally:
    * (div, ) => NaN
    * (div, X) => 1/X
    * (div, X, Y) => (X/Y)
    * (div, X, Y, Z) => (div, (div, X, Y), Z)
    """
    cdef double eval_one_row(self, unsigned m, double[] src):
        if m == 0:
            return NaN

        cdef double acc = src[0]
        if m == 1:
            return 1.0/acc

        cdef unsigned i
        for i in range(1,m):
            acc /= src[i]

        return acc

cdef class Ratio(Functor2):
    """
    Evaluate the line-by-line ratio of two columns.

    Formally, y_i = to a_i/b_i.
    """
    cdef void eval(self, unsigned l, double* dst, const double* src1, const double* src2):
        cdef unsigned i
        for i in range(l):
            dst[i] = src1[i]/src2[i]

# Instanciate the `ratio` singleton.
ratio = Ratio()

# ======================================================================
# Math and stats
# ======================================================================
cdef class variance(Functor1):
    """
    Compute the Variance over a n-period window.

    This is an implementation of the naive algorithm which is not numerically
    stable in the general case, but this should be sufficient for financial data.

    We use the Bessel's correction since we use sampled data.
    """
    cdef double a
    cdef double b
    cdef unsigned n

    def __init__(self, unsigned n):
        self.a = 1.0/(n-1.0)
        self.b = self.a/n
        self.n = n

    cdef make_name(self, col):
        return f"{repr(self)}, {column.get_column_name(col)}"

    cdef void eval(self, unsigned l, double* dst, const double* src):
        cdef double a = self.a
        cdef double b = self.b
        cdef unsigned n = self.n

        cdef double sigma_ui = 0.0
        cdef double sigma_ui2 = 0.0
        cdef unsigned nones = 0
        cdef unsigned i = 0

        # degenerate case
        if l < n:
            return

        # general case
        while i < n-1:
            v = src[i]
            if not isnan(v):
                sigma_ui += v
                sigma_ui2 += v*v
            else:
                nones += 1

            i += 1

        while i < l:
            v = src[i]
            if not isnan(v):
                sigma_ui += v
                sigma_ui2 += v*v
            else:
                nones += 1

            dst[i] = NaN if nones else a*sigma_ui2 - b*sigma_ui*sigma_ui

            i += 1

            v = src[i-n]
            if not isnan(v):
                sigma_ui -= v
                sigma_ui2 -= v*v
            else:
                nones -= 1

# ======================================================================
# Moving averages and smoothing functions
# ======================================================================
cdef class sma(Functor1):
    """
    Compute the Simple Moving Average over a n-period window.
    """
    cdef unsigned n

    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return f"SMA({self.n})"

    cdef void eval(self, unsigned l, double* dst, double* src):
        cdef unsigned n = self.n

        cdef double[::1] buffer = alloc(n)
        cdef unsigned idx=0

        cdef double acc = 0.0
        cdef unsigned nans = n
        cdef double old, new
        cdef unsigned i
        for i in range(l):
            old = buffer[idx]
            if isnan(old):
                nans -= 1
            else:
                acc -= old

            buffer[idx] = new = src[i]
            idx += 1
            if idx == n:
                idx = 0

            if isnan(new):
                nans += 1
            else:
                acc += new

            dst[i] = NaN if nans else acc/n

cdef class ema(Functor1):
    """
    Compute the Exponential Moving Average over a n-period window.

    The smoothing factor is assumed to be `2/(1+n)` where `n` is the window size.
    """
    cdef unsigned n
    cdef double alpha

    def __init__(self, n):
        self.n = n
        self.alpha = 2.0/(1+n)

    def __repr__(self):
        return f"EMA({self.n})"

    cdef void eval(self, unsigned l, double* dst, double* src):
        cdef unsigned n = self.n
        cdef double alpha = self.alpha

        cdef double acc = NaN
        cdef unsigned history = 0
        cdef double curr
        cdef unsigned i
        for i in range(l):
            curr = src[i]
            if isnan(acc):
                history = 0
                acc = curr
            elif isnan(curr):
                history = 0
                acc = NaN
            else:
                acc += (curr-acc)*alpha
                history += 1

            dst[i] = NaN if history<n else acc


cdef class wilders(Functor1):
    """
    Compute the Wilder's Smoothing.

    Except for the initialization stage, a `n` periode Wilder's Smoothing is equivalent
    to a `2n-1` Exponential Moving Average.
    """
    cdef unsigned n
    cdef double alpha

    def __init__(self, n):
        self.n = n
        self.alpha = 1.0/n

    def __repr__(self):
        return f"WILDERS({self.n})"

    cdef void eval(self, unsigned l, double* dst, double* src):
        cdef unsigned n = self.n
        cdef double alpha = self.alpha

        cdef double acc = 0.0
        cdef unsigned history = 0
        cdef double curr
        cdef unsigned i
        for i in range(l):
            curr = src[i]
            if isnan(curr):
                history = 0
                acc = 0.0
            else:
                if history<n:
                    acc += curr*alpha
                else:
                    acc += (curr-acc)*alpha
                history += 1

            dst[i] = NaN if history<n else acc

# ======================================================================
# Technical Indicators
# ======================================================================
cdef class Tr(Functor3):
    """
    Compute the True Range

    On day `i`, the True Range is the greatest of:
    * `high[i]-low[i]`
    * `abs(high[i]-close[i-1])`
    * `abs(low[i]-close[i-1])`
    """

    def __repr__(self):
        return f"TR"

    cdef void eval(self, unsigned l, double* dst, double* high, double* low, double* close):
        cdef double yc = NaN # Yesterday's close
        cdef double th # today's high
        cdef double tl # today's low

        cdef double hc
        cdef double lc

        cdef double tr

        cdef unsigned i
        for i in range(l):
            th = high[i]
            tl = low[i]

            tr = th-tl
            if not isnan(yc):
                hc = abs(th-yc)
                lc = abs(tl-yc)

                if hc > tr:
                    tr = hc
                if lc > tr:
                    tr = lc

            dst[i] = tr
            yc = close[i]

tr = Tr()

class atr(Functor3):
    """
    Compute the Average True Range.

    The Average True Range is the smoothed value of the True Range indicator.
    
    This indicator uses the Wilder's Smoothing.
    Potentially this could be parameterized.
    """
    def __init__(self, n):
        self.n = n
        self.tr = tr
        self.smooth = wilders(n)

    def __repr__(self):
        return f"ATR({self.n})"

    def __call__(self, rowcount, high, low, close):
        tr = self.tr(rowcount, high, low, close)
        atr = self.smooth(rowcount, tr)
        return atr

cdef class band(Functor2_3):
    """
    Compute a band arround a middle value.
    """
    cdef make_names(self, col1, col2):
        basename = col1.name
        return [
                f"{basename}:B",
                f"{basename}",
                f"{basename}:A",
                ]

    cdef void eval(self, unsigned l,
            double* dst1, double* dst2, double* dst3,
            const double* src1, const double* src2):
        cdef unsigned i
        for i in range(l):
            dst1[i] = src1[i]-src2[i]
            dst2[i] = src1[i]
            dst3[i] = src1[i]+src2[i]

