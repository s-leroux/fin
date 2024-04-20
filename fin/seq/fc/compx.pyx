from fin.seq.column cimport Column
from fin.seq.serie cimport Serie
from fin.seq.coltypes import Ternary

from fin cimport mem

cdef class above:
    cdef double threshold

    def __init__(self, threshold):
        self.threshold = threshold

    def __repr__(self):
        return f"ABOVE({self.threshold})"

    def __call__(self, Serie ser, Column col, *tail):
        # ------------------ prologue ------------------
        cdef unsigned l = ser.rowcount
        cdef signed char[::1] dst = mem.schar_alloc(l)
        cdef const double *src = col.as_float_values()
        # -------------- end of prologue ---------------

        self.eval(l, &dst[0], src)

        # ------------------ epilogue ------------------
        res = Column.from_ternary_mv(
                dst,
                name=f"{self}, {col.name}",
                type=Ternary()
            )
        if tail:
            return (res, self, tail)
        else:
            return res
        # -------------- end of epilogue ---------------

    cdef void eval(self, unsigned l, signed char* dst, const double* src):
        cdef unsigned i
        for i in range(l):
            dst[i] = +1 if src[i]>self.threshold else -1

