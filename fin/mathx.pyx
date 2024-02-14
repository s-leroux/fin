from cpython cimport array
from fin.mathx cimport NaN

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN = float("NaN")
cdef array.array double_array_template = array.array('d', [])

cdef inline double[::1] alloc(unsigned n, double init_value = NaN):
    """
    Allocate a contiguous array of n double initialized to NaN.
    Return a vie on the array.
    """
    cdef double[::1] arr = array.clone(double_array_template, n, zero=False)[::1]
    cdef unsigned i
    for i in range(n):
        arr[i] = init_value

    return arr

