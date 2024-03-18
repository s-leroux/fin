from cpython cimport array
import array

from fin.seq2.column cimport Column
from fin.seq2.table import Table

# ======================================================================
# Globals
# ======================================================================
cdef array.array    int_array       = array.array("i", [])
cdef array.array    unsigned_array  = array.array("I", [])
cdef array.array    double_array    = array.array("d", [])

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

        columns = tuple([c if isinstance(c, Column) else Column.from_sequence(c) for c in columns])

        self._index = index
        self._columns = columns

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
        tbl = Table()
        tbl.append(self)

        return str(tbl)

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

    return Join.create(Column.from_sequence(joinIndex), tuple(leftColumns), tuple(rightColumns))
