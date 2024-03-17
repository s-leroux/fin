from fin.seq2.column cimport Column

cdef class Serie:
    cdef Column  _index
    cdef tuple   _columns
