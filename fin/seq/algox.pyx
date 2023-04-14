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
    A simple functor accepting one column argument.

    Actual calculation are delegate to the eval() method that should be
    overrided by the actual implementation.
    """
    cdef void eval(self, unsigned l, double* dst, const double* src):
        pass

    cdef make_name(self, col):
        return None

    def __call__(self, rowcount, sequence):
        cdef column.FColumn fcolumn = column.as_fcolumn(sequence)
        cdef double[::1] values = fcolumn.values
        cdef unsigned l = len(values)
        cdef double[::1] result = alloc(l)

        self.eval(l, &result[0], &values[0])

        return column.FColumn(self.make_name(sequence), result)

cdef class Functor2:
    """
    A simple functor accepting two column arguments.

    Actual calculation are delegate to the eval() method that should be
    overrided by the actual implementation.
    """
    cdef void eval(self, unsigned l, double* dst, const double* src1, const double* src2):
        pass

    cdef make_name(self, col1, col2):
        return None

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

cdef class FunctorN:
    """
    A simple functor accepting N column argument.

    Actual calculation are delegate to the eval() method that should be
    overrided by the actual implementation.
    """
    cdef void eval(self, unsigned l, double* dst, unsigned m, (const double*)[] src):
        pass

    cdef make_name(self, sequences):
        return None

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
# Moving averages
# ======================================================================
cdef class sma(Functor1):
    """
    Compute the Simple Moving Average over a n-period window.
    """
    cdef unsigned n

    def __init__(self, n):
        self.n = n

    cdef make_name(self, col):
        return f"SMA({self.n}), {column.get_column_name(col)}"

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

