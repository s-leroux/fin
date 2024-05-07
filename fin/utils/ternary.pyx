from cpython cimport array
from fin.mathx cimport balloc

from cpython.bytes cimport PyBytes_GET_SIZE, PyBytes_AsString

""" Set of helper functions to work with standard balanced ternary values.

    Here, True is +1, False is -1 and Unknown is 0. At C level ternary
    values are stored as `signed char` values. At Python level we use
    the standard constants True, False, and None.

    For ease of use, some functions may accept _ternary-strings_ as Python
    string made of the 'T', 'F', and 'N' characters.
"""

cdef array.array ternary_parse_pattern(bytes pattern):
    cdef Py_ssize_t size = PyBytes_GET_SIZE(pattern)
    cdef const char *src = PyBytes_AsString(pattern)
    cdef array.array arr = balloc(size)
    cdef signed char *dst = arr.data.as_schars
    cdef char c

    while True:
        c = src[0]
        if c == 0:
            break
        elif c == b'T':
            dst[0] = +1
        elif c == b'F':
            dst[0] = -1
        elif c == b'N':
            dst[0] = 0
        else:
            raise ValueError(f"Invalid pattern string {pattern!r}")

        dst += 1
        src += 1

    return arr
