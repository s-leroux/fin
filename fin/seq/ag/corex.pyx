# cython: boundscheck=False
# cython: cdivision=True

from fin.seq import coltypes

cdef class CAggregateFunction:
    def type_for(self, column):
        return column.type

    def __call__(self, Column col,  begin=0, end=None):
        if end is None:
            end = col.length

        return self.call(col, begin, end)

    cdef call(self, Column col, unsigned begin, unsigned end):
        if begin > end:
            raise ValueError(f"Wrong order ({begin} > {end})")
        if end > col.length:
            raise IndexError(f"Index out of bounds ({end} > {col.length})")

        return self.eval(col, begin, end)

    cdef eval(self, Column col, unsigned begin, unsigned end):
        raise NotImplementedError

cdef class _First(CAggregateFunction):
    cdef eval(self, Column col, unsigned begin, unsigned end):
        if begin >= end:
            raise IndexError("The empty range has no first item")

        return col.get_py_values()[begin]

cdef class _Count(CAggregateFunction):
    def type_for(self, column):
        return coltypes.Integer()

    cdef eval(self, Column col, unsigned begin, unsigned end):
        return end-begin

cdef class _Sum(CAggregateFunction):
    def type_for(self, column):
        return coltypes.Float()

    cdef eval(self, Column col, unsigned begin, unsigned end):
        cdef const double *src = col.as_float_values()
        cdef unsigned i
        cdef double acc = 0.0

        for i in range(begin, end):
            acc += src[i]

        return acc

cdef class _Avg(CAggregateFunction):
    def type_for(self, column):
        return coltypes.Float()

    cdef eval(self, Column col, unsigned begin, unsigned end):
        cdef const double *src = col.as_float_values()
        cdef unsigned i
        cdef double acc = 0.0
        
        for i in range(begin, end):
            acc += src[i]

        return acc/(end-begin)
        
first = _First()
count = _Count()
sum = _Sum()
avg = _Avg()
