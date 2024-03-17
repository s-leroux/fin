from fin.seq2.column cimport Column

# ======================================================================
# Serie class
# ======================================================================
cdef class Serie:
    cdef Column  _index
    cdef tuple   _columns

    cdef Serie c_add_scalar(self, double other)
    cdef Serie c_add_serie(self, Serie other)
