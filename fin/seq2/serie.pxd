from fin.seq2.column cimport Column

# ======================================================================
# Serie class
# ======================================================================
cdef class Serie:
    cdef Column  _index
    cdef tuple   _columns
    cdef unsigned rowcount
    cdef str      name

    # ------------------------------------------------------------------
    # Arithmetic operators
    # ------------------------------------------------------------------
    cdef Serie c_add_scalar(self, double other)
    cdef Serie c_add_serie(self, Serie other)

    # ------------------------------------------------------------------
    # Subscript
    # ------------------------------------------------------------------
    cdef Serie c_get_items(self, tuple idx)
    cdef Serie c_get_item_by_index(self, int idx)
    cdef Serie c_get_item_by_name(self, str name)
