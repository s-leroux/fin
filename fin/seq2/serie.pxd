from fin.seq2.column cimport Column

cdef class Serie:
    cdef Column  _index
    cdef tuple   _columns

    cdef Serie c_add_with_integral(self, double other)
