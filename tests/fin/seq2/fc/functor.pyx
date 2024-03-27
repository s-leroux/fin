from fin.seq2.fc cimport functorx

# ======================================================================
# Functor test functions
# ======================================================================
cdef class Functor1Example(functorx.Functor1):
    cdef void eval(
            self,
            unsigned n,
            double* dst1,
            const double* src1,
            ):
        cdef unsigned i
        for i in range(n):
            # Simple copy
            dst1[i] = src1[i]

cdef class Functor2Example(functorx.Functor2):
    cdef void eval(
            self,
            unsigned n,
            double* dst1,
            const double* src1,
            const double* src2,
            ):
        cdef unsigned i
        for i in range(n):
            # Sum
            dst1[i] = src1[i] + src2[i]

cdef class Functor3Example(functorx.Functor3):
    cdef void eval(
            self,
            unsigned n,
            double* dst1,
            const double* src1,
            const double* src2,
            const double* src3,
            ):
        cdef unsigned i
        for i in range(n):
            # Sum
            dst1[i] = src1[i] + src2[i] + src3[i]

