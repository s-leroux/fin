from cpython cimport array

cdef array.array double_array_template = array.array('d', [])
# cdef array.array int_array_template = array.array('i', [])
# cdef array.array unsigned_array_template = array.array('I', [])
cdef array.array schar_array_template = array.array('b', [])

cdef double[::1] double_alloc(unsigned n):
    return array.clone(double_array_template, n, zero=False)[::1]

cdef signed char[::1] schar_alloc(unsigned n):
    return array.clone(schar_array_template, n, zero=False)[::1]
