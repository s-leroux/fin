# cython: boundscheck=False
# cython: cdivision=True

import array
from cpython cimport array

from fin.mathx cimport alloc, aalloc, NaN
from fin.seq.serie cimport Serie
from fin.seq.column cimport Column
from fin.seq.column import Column

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
        return f"{repr(self)}, {col.name}"

    def __call__(self, Serie serie, Column src1):
        cdef unsigned rowcount = serie.rowcount
        cdef array.array dst1 = aalloc(rowcount)

        self.eval(rowcount,
                &dst1.data.as_doubles[0],
                &src1.get_f_values().data.as_doubles[0]
                )

        return Column.from_float_array(dst1, name=self.make_name(src1))

cdef class Functor1_3:
    """
    A simple functor accepting a one-column argument and returning three columns.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l,
            double* dst1, double* dst2, double* dst3,
            const double* src1):
        pass

    cdef make_names(self, col1):
        return [
                "A",
                "B",
                "C"
                ]

    def __call__(self, Serie serie, Column src1):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = aalloc(l)
        cdef array.array dst2 = aalloc(l)
        cdef array.array dst3 = aalloc(l)

        self.eval(l,
                &dst1.data.as_doubles[0],
                &dst2.data.as_doubles[0],
                &dst3.data.as_doubles[0],
                &src1.get_f_values().data.as_doubles[0]
                )

        names = self.make_names(src1);

        return (
                Column.from_float_array(dst1, name=names[0]),
                Column.from_float_array(dst2, name=names[1]),
                Column.from_float_array(dst3, name=names[2]),
                )

cdef class Functor2:
    """
    A simple functor accepting two-column arguments.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, double* dst, const double* src1, const double* src2):
        pass

    cdef make_name(self, col1, col2):
        return f"{repr(self)}, {col1.name}, {col2.name}"

    def __call__(self, Serie serie, Column src1, Column src2):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = aalloc(l)

        self.eval(l,
                &dst1.data.as_doubles[0],
                &src1.get_f_values().data.as_doubles[0],
                &src2.get_f_values().data.as_doubles[0],
                )

        return Column.from_float_array(dst1, name=self.make_name(src1, src2))

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

    def __call__(self, Serie serie, Column src1, Column src2):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = aalloc(l)
        cdef array.array dst2 = aalloc(l)
        cdef array.array dst3 = aalloc(l)

        self.eval(l,
                &dst1.data.as_doubles[0],
                &dst2.data.as_doubles[0],
                &dst3.data.as_doubles[0],
                &src1.get_f_values().data.as_doubles[0],
                &src2.get_f_values().data.as_doubles[0],
                )

        names = self.make_names(src1, src2);

        return [
                Column.from_float_array(dst1, name=names[0]),
                Column.from_float_array(dst2, name=names[1]),
                Column.from_float_array(dst3, name=names[2]),
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
        return f"{repr(self)}, {col1.name}, {col2.name}, {col3.name}"

    def __call__(self, Serie serie, Column src1, Column src2, Column src3):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = aalloc(l)

        self.eval(l,
                &dst1.data.as_doubles[0],
                &src1.get_f_values().data.as_doubles[0],
                &src2.get_f_values().data.as_doubles[0],
                &src3.get_f_values().data.as_doubles[0],
                )

        return Column.from_float_array(dst1, name=self.make_name(src1, src2, src3))

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

    def __call__(self, Serie serie, *seqs):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned m = len(seqs)
        cdef const double** v= <const double**>alloca(m*sizeof(double*))

        cdef unsigned i
        for i in range(m):
            ci = <Column>seqs[i]
            assert len(ci) == rowcount
            v[i] = &ci.get_f_values().data.as_doubles[0]
        cdef unsigned l = rowcount
        cdef array.array dst1 = aalloc(l)

        self.eval(l, &dst1.data.as_doubles[0], m, v)

        return Column.from_float_array(dst1, name=self.make_name(seqs))

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

