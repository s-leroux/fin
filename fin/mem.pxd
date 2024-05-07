cdef extern from "<alloca.h>":
    void *alloca(size_t size)

cdef double[::1] double_alloc(unsigned n)
cdef signed char[::1] schar_alloc(unsigned n)
