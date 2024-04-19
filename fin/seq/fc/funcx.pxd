# ======================================================================
# Common base classes
# ======================================================================
ctypedef union param_t:
    double  [1]as_doubles
    signed char [1]as_schar

cdef class Functor1:
    """
    A simple functor accepting one-column argument.
    """
    cdef char   src1_tc
    cdef char   dst1_tc

    cdef void eval(
            self,
            unsigned l,
            param_t* dst,
            const param_t* src
            )
    cdef make_name(self, col)

cdef class Functor1_3:
    """
    A simple functor accepting a one-column argument and returning three columns.
    """
    cdef char   src1_tc
    cdef char   dst1_tc
    cdef char   dst2_tc
    cdef char   dst3_tc

    cdef void eval(
            self,
            unsigned l,
            param_t *dst1, param_t *dst2, param_t *dst3,
            const param_t *src1
            )
    cdef make_names(self, col1)

cdef class Functor2:
    """
    A simple functor accepting two-column arguments.
    """
    cdef char   src1_tc
    cdef char   src2_tc
    cdef char   dst1_tc

    cdef void eval(
            self,
            unsigned l,
            param_t *dst,
            const param_t *src1, const param_t *src2
            )
    cdef make_name(self, col1, col2)

cdef class Functor2_3:
    """
    A simple functor accepting two-column arguments and returning three columns.
    """
    cdef char   src1_tc
    cdef char   src2_tc
    cdef char   dst1_tc
    cdef char   dst2_tc
    cdef char   dst3_tc

    cdef void eval(
            self,
            unsigned l,
            param_t *dst1, param_t *dst2, param_t *dst3,
            const param_t *src1, const param_t *src2
            )
    cdef make_names(self, col1, col2)

cdef class Functor3:
    """
    A simple functor accepting three-column arguments.
    """
    cdef char   src1_tc
    cdef char   src2_tc
    cdef char   src3_tc
    cdef char   dst1_tc

    cdef void eval(
            self,
            unsigned l,
            param_t *dst,
            const param_t *src1, const param_t *src2, const param_t *src3
            )
    cdef make_name(self, col1, col2, col3)

cdef class Functor5_4:
    """
    A functor accepting a five-column argument and returning four columns.
    """
    cdef char   src1_tc
    cdef char   src2_tc
    cdef char   src3_tc
    cdef char   src4_tc
    cdef char   src5_tc
    cdef char   dst1_tc
    cdef char   dst2_tc
    cdef char   dst3_tc
    cdef char   dst4_tc

    cdef void eval(
            self,
            unsigned l,
            param_t *dst1, param_t *dst2, param_t *dst3, param_t *dst4,
            const param_t *src1, const param_t *src2, const param_t *src3, const param_t *src4, const param_t *src5
            )
    cdef make_names(self, col1, col2, col3, col4, col5)

cdef class FunctorN:
    """
    A simple functor accepting N-column argument.
    """
    cdef char   *src_tc
    cdef char   dst1_tc

    cdef void eval(self,
            unsigned l,
            param_t *dst,
            unsigned m, (const param_t*)[] src
            )
    cdef make_name(self, sequences)

