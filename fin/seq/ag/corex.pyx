# cython: boundscheck=False
# cython: cdivision=True

from fin.seq import coltypes

cdef class CAggregateFunction:
    """ Base class for Cython-defined aggregate functions.

        See also PyAggregateFunction for Python-defined aggregate functions.

        Call flow:
            Python code -> __call__() -> call() -> eval() [Cython impl.]
            Python code -> __call__() -> call() -> eval() -> py_eval [Python impl.]
            Cython code -> call() -> eval() [Cython impl.]
            Cython code -> call() -> eval() -> py_eval [Python impl.]
    """
    def type_for(self, column):
        return column.type

    def __call__(self, Column col,  begin=0, end=None):
        if end is None:
            end = col.length

        return self.call(col, begin, end)

    cdef call(self, Column col, unsigned begin, unsigned end):
        """ Entry point for calling the aggregate function from user code.

            This performs basic type and bounds checking, then defer to self.eval().
            You probably don't have to override this method.
        """
        if begin > end:
            raise ValueError(f"Wrong order ({begin} > {end})")
        if end > col.length:
            raise IndexError(f"Index out of bounds ({end} > {col.length})")

        return self.eval(col, begin, end)

    cdef eval(self, Column col, unsigned begin, unsigned end):
        """ Evaluate the aggregate function for column's row range.

            Override this method for custom Cython-defined aggregate functions.
            To for custom Python-defined aggregate functions, see the the PyAggregateFunction class.
            You don't have to perform bound checking here as this was done in self.call().
        """
        raise NotImplementedError

cdef class PyAggregateFunction(CAggregateFunction):
    """ Base class for Python-defined aggregate functions.
    """
    cdef eval(self, Column col, unsigned begin, unsigned end):
        # return getattr(self, "eval")(self, col, begin, end) # XXX Does this work?
        return self.py_eval(col, begin, end) # XXX Does this work?

    def py_eval(self, col, begin, end):
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
