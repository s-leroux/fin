# cython: boundscheck=False
# cython: cdivision=True

from cpython cimport array

from fin.mathx cimport alloc, aalloc, NaN
from fin.seq.serie cimport Serie
from fin.seq.column cimport Column
from fin.seq.column import Column

cdef extern from "<alloca.h>":
    void *alloca(size_t size)


# ======================================================================
# Allocators
# ======================================================================
cdef array.array double_array_template = array.array('d', [])
# cdef array.array int_array_template = array.array('i', [])
# cdef array.array unsigned_array_template = array.array('I', [])
cdef array.array signed_byte_array_template = array.array('b', [])

cdef inline array.array alloc_(char typecode, unsigned n):
    if typecode == b'd':
        return array.clone(double_array_template, n, zero=False)
    elif typecode == b'd':
        return array.clone(signed_byte_array_template, n, zero=False)

    raise ValueError(f"bad typecode (must be b or d, not {typecode!r})")

cdef inline const param_t*    data_(char typecode, Column col):
    if typecode == b'd':
        return <const param_t*>col.as_float_values()
    elif typecode == b'b':
        return <const param_t*>col.as_ternary_values()

    raise ValueError(f"bad typecode (must be b or d, not {typecode!r})")

# ======================================================================
# Common base classes
# ======================================================================
cdef class Functor1:
    """
    A simple functor accepting one-column argument.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, param_t* dst, const param_t* src):
        pass

    cdef make_name(self, col):
        return f"{repr(self)}, {col.name}"

    def __call__(self, Serie serie, Column src1):
        cdef unsigned rowcount = serie.rowcount
        cdef array.array dst1 = alloc_(self.dst1_tc, rowcount)

        self.eval(rowcount,
                <param_t*>dst1.data.as_voidptr,
                data_(self.src1_tc, src1),
                )

        return Column.from_float_mv(dst1, name=self.make_name(src1), type=src1._type)

cdef class Functor1_3:
    """
    A simple functor accepting a one-column argument and returning three columns.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    def __cinit__(self):
        self.src1_tc = b'd'
        self.dst1_tc = b'd'
        self.dst2_tc = b'd'
        self.dst3_tc = b'd'

    cdef void eval(self, unsigned l,
            param_t *dst1, param_t *dst2, param_t *dst3,
            const param_t *src1):
        pass

    cdef make_names(self, col1):
        return [
                "A",
                "B",
                "C"
                ]

    def __call__(self, Serie serie, Column src1):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = alloc_(self.dst1_tc, l)
        cdef array.array dst2 = alloc_(self.dst2_tc, l)
        cdef array.array dst3 = alloc_(self.dst3_tc, l)

        self.eval(l,
                <param_t*>dst1.data.as_voidptr,
                <param_t*>dst2.data.as_voidptr,
                <param_t*>dst3.data.as_voidptr,
                data_(self.src1_tc, src1),
                )

        names = self.make_names(src1);

        return (
                Column.from_float_mv(dst1, name=names[0], type=src1._type),
                Column.from_float_mv(dst2, name=names[1], type=src1._type),
                Column.from_float_mv(dst3, name=names[2], type=src1._type),
                )

cdef class Functor2:
    """
    A simple functor accepting two-column arguments.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, param_t *dst, const param_t *src1, const param_t *src2):
        pass

    cdef make_name(self, col1, col2):
        return f"{repr(self)}, {col1.name}, {col2.name}"

    def __call__(self, Serie serie, Column src1, Column src2):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = alloc_(self.dst1_tc, l)

        self.eval(l,
                <param_t*>dst1.data.as_voidptr,
                data_(self.src1_tc, src1),
                data_(self.src2_tc, src2),
                )

        return Column.from_float_mv(dst1, name=self.make_name(src1, src2), type=src1._type)

cdef class Functor2_3:
    """
    A simple functor accepting two-column arguments and returning three columns.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l,
            param_t *dst1, param_t *dst2, param_t *dst3,
            const param_t *src1, const param_t *src2):
        pass

    cdef make_names(self, col1, col2):
        return [
                "A",
                "B",
                "C"
                ]

    def __call__(self, Serie serie, Column src1, Column src2):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = alloc_(self.dst1_tc, l)
        cdef array.array dst2 = alloc_(self.dst2_tc, l)
        cdef array.array dst3 = alloc_(self.dst3_tc, l)

        self.eval(l,
                <param_t*>dst1.data.as_voidptr,
                <param_t*>dst2.data.as_voidptr,
                <param_t*>dst3.data.as_voidptr,
                data_(self.src1_tc, src1),
                data_(self.src2_tc, src2),
                )

        names = self.make_names(src1, src2);

        return (
                Column.from_float_mv(dst1, name=names[0], type=src1._type),
                Column.from_float_mv(dst2, name=names[1], type=src1._type),
                Column.from_float_mv(dst3, name=names[2], type=src1._type),
                )

cdef class Functor3:
    """
    A simple functor accepting three-column arguments.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, param_t *dst, const param_t *src1, const param_t *src2, const param_t *src3):
        pass

    cdef make_name(self, col1, col2, col3):
        return f"{repr(self)}, {col1.name}, {col2.name}, {col3.name}"

    def __call__(self, Serie serie, Column src1, Column src2, Column src3):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = alloc_(self.dst1_tc, l)

        self.eval(l,
                <param_t*>dst1.data.as_voidptr,
                data_(self.src1_tc, src1),
                data_(self.src2_tc, src2),
                data_(self.src3_tc, src3),
                )

        return Column.from_float_mv(dst1, name=self.make_name(src1, src2, src3), type=src1._type)

cdef class Functor5_4:
    """
    A functor accepting a five-column argument and returning four columns.
    """
    cdef void eval(
            self,
            unsigned l,
            param_t *dst1, param_t *dst2, param_t *dst3, param_t *dst4,
            const param_t *src1, const param_t *src2, const param_t *src3, const param_t *src4, const param_t *src5
            ):
        pass

    cdef make_names(self, col1, col2, col3, col4, col5):
        return [
                "A",
                "B",
                "C",
                "D",
                "E",
                ]

    def __call__(self, Serie serie, Column src1, Column src2, Column src3, Column src4, Column src5):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned l = rowcount
        cdef array.array dst1 = alloc_(self.dst1_tc, l)
        cdef array.array dst2 = alloc_(self.dst2_tc, l)
        cdef array.array dst3 = alloc_(self.dst3_tc, l)
        cdef array.array dst4 = alloc_(self.dst4_tc, l)

        self.eval(l,
                <param_t*>dst1.data.as_voidptr,
                <param_t*>dst2.data.as_voidptr,
                <param_t*>dst3.data.as_voidptr,
                <param_t*>dst4.data.as_voidptr,
                data_(self.src1_tc, src1),
                data_(self.src2_tc, src2),
                data_(self.src3_tc, src3),
                data_(self.src4_tc, src4),
                data_(self.src5_tc, src5),
                )

        names = self.make_names(src1, src2, src3, src4, src5);

        return [
                Column.from_float_mv(dst1, name=names[0], type=src1._type),
                Column.from_float_mv(dst2, name=names[1], type=src1._type),
                Column.from_float_mv(dst3, name=names[2], type=src1._type),
                Column.from_float_mv(dst4, name=names[3], type=src1._type),
                ]


cdef class FunctorN:
    """
    A simple functor accepting N-column argument.

    Actual calculation are delegate to the eval() method that should be
    overrided by the implementation.
    """
    cdef void eval(self, unsigned l, param_t *dst, unsigned m, (const param_t*)[] src):
        pass

    cdef make_name(self, sequences):
        return f"{repr(self)}"

    def __call__(self, Serie serie, *seqs):
        cdef unsigned rowcount = serie.rowcount
        cdef unsigned m = len(seqs)
        cdef const param_t** v= <const param_t**>alloca(m*sizeof(param_t*))

        cdef unsigned i
        for i in range(m):
            ci = <Column>seqs[i]
            assert len(ci) == rowcount
            v[i] = data_(self.src_tc[i], ci)
        cdef unsigned l = rowcount
        cdef array.array dst1 = alloc_(self.dst1_tc, l)

        self.eval(l, <param_t*>dst1.data.as_voidptr, m, v)

        return Column.from_float_mv(dst1, name=self.make_name(seqs), type=(<Column>seqs[0])._type)
