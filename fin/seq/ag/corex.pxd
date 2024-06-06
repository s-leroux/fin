from fin.seq.column cimport Column

cdef class CAggregateFunction:
    cdef call(self, Column col, unsigned begin, unsigned end)
    cdef eval(self, Column col, unsigned begin, unsigned end)

