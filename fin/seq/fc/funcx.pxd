# ======================================================================
# Common base classes
# ======================================================================
cdef class Functor1:
    """
    A simple functor accepting one-column argument.
    """
    cdef void eval(
            self,
            unsigned l,
            double* dst,
            const double* src
            )
    cdef make_name(self, col)

cdef class Functor1_3:
    """
    A simple functor accepting a one-column argument and returning three columns.
    """
    cdef void eval(
            self,
            unsigned l,
            double* dst1, double* dst2, double* dst3,
            const double* src1
            )
    cdef make_names(self, col1)

cdef class Functor2:
    """
    A simple functor accepting two-column arguments.
    """
    cdef void eval(
            self,
            unsigned l,
            double* dst,
            const double* src1, const double* src2
            )
    cdef make_name(self, col1, col2)

cdef class Functor2_3:
    """
    A simple functor accepting two-column arguments and returning three columns.
    """
    cdef void eval(
            self,
            unsigned l,
            double* dst1, double* dst2, double* dst3,
            const double* src1, const double* src2
            )
    cdef make_names(self, col1, col2)

cdef class Functor3:
    """
    A simple functor accepting three-column arguments.
    """
    cdef void eval(
            self,
            unsigned l,
            double* dst,
            const double* src1, const double* src2, const double* src3
            )
    cdef make_name(self, col1, col2, col3)

cdef class Functor5_4:
    """
    A functor accepting a five-column argument and returning four columns.
    """
    cdef void eval(
            self,
            unsigned l,
            double* dst1, double* dst2, double* dst3, double* dst4,
            const double* src1, const double* src2, const double* src3, const double* src4, const double* src5
            )
    cdef make_names(self, col1, col2, col3, col4, col5)

cdef class FunctorN:
    """
    A simple functor accepting N-column argument.
    """
    cdef void eval(self,
            unsigned l,
            double* dst,
            unsigned m, (const double*)[] src
            )
    cdef make_name(self, sequences)

# ======================================================================
# Row functors
# ======================================================================
cdef class RowFunctor1(Functor1):
    """
    A functor that evaluates data row-by-row and accepting a one-column argument.
    """
    cdef double eval_one_row(
            self,
            double src
            )
    cdef void eval(self, unsigned l, double* dst, const double* src)

cdef class RowFunctorN(FunctorN):
    """
    A functor that evaluates data row-by-row and accepting a N-column argument.
    """
    cdef double eval_one_row(
            self,
            unsigned m, double[] src
            )
    cdef void eval(self, unsigned l, double* dst, unsigned m, (const double*)[] src)

# ======================================================================
# Window functions
# ======================================================================
cdef class WindowFunctor1(Functor1):
    cdef unsigned n

    cdef double eval_one_window(
            self,
            unsigned n, const double *src
            )
    cdef void eval(self, unsigned l, double* dst, const double* src)

