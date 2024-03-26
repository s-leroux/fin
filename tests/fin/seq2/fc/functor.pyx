from fin.seq2.fc cimport functorx

# ======================================================================
# Functor test functions
# ======================================================================
cdef class Functor1Example(functorx.Functor1):
    cdef void eval(self, unsigned n, double* dst, const double* src):
        cdef unsigned i
        for i in range(n):
            dst[i] = src[i]

