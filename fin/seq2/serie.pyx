from cpython cimport array
import array

from fin.seq2.column cimport Column
from fin.seq2.presentation import Presentation

# ======================================================================
# Globals
# ======================================================================
cdef array.array    int_array       = array.array("i", [])
cdef array.array    unsigned_array  = array.array("I", [])
cdef array.array    double_array    = array.array("d", [])

# ======================================================================
# Low-level helpers
# ======================================================================
cdef inline Column serie_get_column_by_index(Serie self, int idx):
    cdef int col_count
    if idx < 0:
        col_count = len(self._columns)
        idx += col_count+1
        if idx < 0:
            raise IndexError("serie index out of range")

    if idx == 0:
        return self._index
    else:
        return self._columns[idx-1]

cdef inline Column serie_get_column_by_name(Serie self, str name):
    if name == self._index.name:
        return self._index

    cdef Column column
    for column in self._columns:
        if column.name == name:
            return column

    raise KeyError(name)

# ======================================================================
# Serie
# ======================================================================
cdef class Serie:
    """
    A Serie is an index and a list of columns, all of same length.

    The index is assumed to be sorted in ascending order (strictly?).
    """
    def __init__(self, index, *columns):
        if not isinstance(index, Column):
            index = Column.from_sequence(index)

        columns = tuple([
            c if isinstance(c, Column) else 
            Column.from_callable(c, index) if callable(c) else
            Column.from_sequence(c) for c in columns
        ])

        self._index = index
        self._columns = columns

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def index(self):
        return self._index

    @property
    def columns(self):
        return self._columns

    def __str__(self):
        """
        Convert to string.

        Rely on the serie formatting utility.
        """
        pres = Presentation(heading=False)

        return pres(self)

    # ------------------------------------------------------------------
    # Subscript
    # ------------------------------------------------------------------
    def __getitem__(self, selector):
        t = type(selector)
        if t is tuple:
            return self.c_get_items(selector)
        elif t is int:
            return self.c_get_item_by_index(selector)
        elif t is str:
            return self.c_get_item_by_name(selector)
        else:
            raise TypeError(f"serie indices cannot be {t}")

    cdef Serie c_get_items(self, tuple seq):
        # Should we implement this using a recursive-descend parser to allow nested tuples?
        cdef list columns = []
        cdef object i
        cdef type t

        for i in seq:
            t = type(i)
            if t is int:
                columns.append(serie_get_column_by_index(self, i))
            elif t is str:
                columns.append(serie_get_column_by_name(self, i))
            else:
                raise TypeError(f"serie indices cannot be {t}")

        return Serie(self._index, *columns)

    cdef Serie c_get_item_by_index(self, int idx):
        return Serie(self._index, serie_get_column_by_index(self, idx))

    cdef Serie c_get_item_by_name(self, str name):
        return Serie(self._index, serie_get_column_by_name(self, name))


    # ------------------------------------------------------------------
    # Arithmetic operators
    # ------------------------------------------------------------------
    def __add__(self, other):
        """
        Addition.
        """
        if isinstance(other, (int, float)):
            return (<Serie>self).c_add_scalar(other)
        elif isinstance(other, Serie):
            return (<Serie>self).c_add_serie(other)
        else:
            return NotImplemented

    cdef Serie c_add_scalar(self, double other):
        cdef Column column
        new = [column.c_add_scalar(other) for column in self._columns]
        return Serie(self._index, *new)

    cdef Serie c_add_serie(self, Serie other):
        cdef Join join = c_join(self, other)
        cdef Column a, b
        cdef list new = [ a + b for a in join.left for b in join.right ]

        return Serie(join.index, *new)

    # ------------------------------------------------------------------
    # Joins
    # ------------------------------------------------------------------
    def __and__(self, other):
        """
        Join operator.
        """
        cdef Join join
        cdef Serie that = self

        if isinstance(other, Serie):
            join = c_join(that, other)
            return Serie(join.index, *(join.left+join.right))
        elif isinstance(other, (int, float)):
            return Serie(that._index, *that._columns, Column.from_constant(len(that.index), other))
        else:
            return NotImplemented

# ======================================================================
# Join
# ======================================================================
cdef class Join:
    cdef Column index
    cdef tuple left
    cdef tuple right

    @staticmethod
    cdef Join create(Column index, tuple left, tuple right):
        cdef Join join = Join.__new__(Join)
        join.index = index
        join.left = left
        join.right = right

        return join

    cdef tuple as_tuple(self):
        """
        Convert a Join structure to a tuple.

        For testing purposes.
        """
        return (self.index, self.left, self.right)

def join(serA, serB):
    return c_join(serA, serB).as_tuple()

cdef Join c_join(Serie serA, Serie serB):
    """
    Create a join from two series.
    """
    cdef tuple indexA = serA._index.get_py_values()
    cdef tuple indexB = serB._index.get_py_values()

    cdef unsigned lenA = len(indexA)
    cdef unsigned lenB = len(indexB)

    # At worst, we will have min(lenA, lenB) rows in the inner join
    cdef unsigned lenMapping = lenA if lenA < lenB else lenB
    cdef array.array mappingA = array.clone(unsigned_array, lenMapping, zero=False)
    cdef array.array mappingB = array.clone(unsigned_array, lenMapping, zero=False)

    cdef unsigned n = 0
    cdef unsigned posA = 0
    cdef unsigned posB = 0

    while True:
        while indexA[posA] is None and posA < lenA:
            posA += 1
        if posA == lenA:
            break

        while indexB[posB] is None and posB < lenB:
            posB += 1
        if posB == lenB:
            break

        if indexA[posA] < indexB[posB]:
            posA += 1
            if posA == lenA:
                break
        elif indexB[posB] < indexA[posA]:
            posB += 1
            if posB == lenB:
                break
        else:
            mappingA.data.as_uints[n] = posA
            mappingB.data.as_uints[n] = posB
            n += 1
            posA += 1
            posB += 1
            if posA == lenA or posB == lenB:
                break

    # shrink array to their correct length:
    array.resize(mappingA, n)
    array.resize(mappingB, n)

    # Build the index
    cdef unsigned i
    cdef list joinIndex = [indexA[mappingA[i]] for i in range(n)]
    cdef Column column

    # Build the left and right series
    cdef list leftColumns = [
            column.c_remap(len(mappingA), mappingA.data.as_uints) for column in serA._columns
    ]
    cdef list rightColumns = [
            column.c_remap(len(mappingB), mappingB.data.as_uints) for column in serB._columns
    ]

    return Join.create(
            Column.from_sequence(joinIndex, name=serA._index.name, formatter=serA._index.formatter),
            tuple(leftColumns),
            tuple(rightColumns)
    )
