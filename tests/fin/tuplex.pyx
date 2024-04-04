from fin cimport tuplex

def test_from_doubles():
    cdef double[1000] values = list(range(1000))
    return tuplex.from_doubles(1000, values)

