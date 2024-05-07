from fin.seq.column cimport Column
from fin.seq.serie cimport Serie
from fin.seq.coltypes import Ternary

from fin cimport mem

# ======================================================================
# Logical functions
# ======================================================================
cdef class _LogicalFunction:
    """ Baseclass for N-ary logical functions.

        Sub-classes should implement the following methods:
        - `__repr__()`
        - `eval()`
    """
    def __call__(self, Serie ser, *cols):
        # ------------------ prologue ------------------
        cdef unsigned l = ser.rowcount
        cdef signed char[::1] dst = mem.schar_alloc(l)

        cdef unsigned n = len(cols)
        cdef const signed char **srcs = <const signed char**>mem.alloca(n*sizeof(signed char**))
        cdef unsigned j
        cdef Column col
        cdef str col_names = ""
        for j, col in enumerate(cols):
            srcs[j] = col.as_ternary_values()
            col_names += f", {col.name}"
        # -------------- end of prologue ---------------

        self.eval(l, &dst[0], n, srcs)

        # ------------------ epilogue ------------------
        return Column.from_ternary_mv(
                dst,
                name=f"{self}{col_names}",
                type=Ternary()
            )
        # -------------- end of epilogue ---------------

    cdef void eval(self, unsigned l, signed char* dst, unsigned n, const signed char** srcs):
        raise NotImplementedError()

cdef class All(_LogicalFunction):
    """ Check the truthiness of the arguments.

        This predicate evaluates to True if all arguments are True.
        It evaluates to False if at least one argument is False.
        Otherwise, it evaluates to None (_undefined_).

        It corresponds to the logical _and_ of the arguments.

        When called with zero arguments, it evaluates to True.
    """
    def __repr__(self):
        return f"all"

    cdef void eval(self, unsigned l, signed char* dst, unsigned n, const signed char** srcs):
        cdef signed char acc
        cdef unsigned i, j
        for i in range(l):
            acc = +1
            for j in range(n):
                if srcs[j][i] < acc:
                    acc = srcs[j][i]
                if acc < 0:
                    break
            dst[i] = acc

all = All()

cdef class Any(_LogicalFunction):
    """ Check the falseness of the arguments.

        This predicate evaluates to True if any arguments is True.
        It evaluates to False if all arguments are False.
        Otherwise, it evaluates to None (_undefined_).

        It corresponds to the logical _and_ of the arguments.

        When called with zero arguments, it evaluates to False.
    """
    def __repr__(self):
        return f"any"

    cdef void eval(self, unsigned l, signed char* dst, unsigned n, const signed char** srcs):
        cdef signed char acc
        cdef unsigned i, j
        for i in range(l):
            acc = -1
            for j in range(n):
                if srcs[j][i] > acc:
                    acc = srcs[j][i]
                if acc > 0:
                    break
            dst[i] = acc

any = Any()

