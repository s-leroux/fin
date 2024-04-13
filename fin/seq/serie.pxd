from fin.seq.column cimport Column

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


cdef inline Column serie_get_column_by_name(Serie self, str name):
    if name == self._index.name:
        return self._index

    cdef Column column
    for column in self._columns:
        if column.name == name:
            return column

    raise KeyError(name)


# ======================================================================
# Join
# ======================================================================
cdef class Join:
    cdef Column index
    cdef tuple left
    cdef tuple right

    @staticmethod
    cdef Join create(Column index, tuple left, tuple right)

    cdef tuple as_tuple(self)

cdef Join c_inner_join(Serie serA, Serie serB, bint rename)
cdef Join c_full_outer_join(Serie serA, Serie serB, bint rename)
cdef Join c_left_outer_join(Serie serA, Serie serB, bint rename)

