from fin.seq2.column cimport Column

cdef class Sequence:
    cdef Column  _index
    cdef tuple   _columns
