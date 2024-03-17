from cpython cimport array
import array

from fin.seq2.column cimport Column

# ======================================================================
# Globals
# ======================================================================
cdef array.array    int_array       = array.array("i", [])
cdef array.array    unsigned_array  = array.array("I", [])
cdef array.array    double_array    = array.array("d", [])

# ======================================================================
# Sequence
# ======================================================================
cdef class Sequence:
    """
    A Sequence is an index and a list of columns, all of same length.

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

# ======================================================================
# Join
# ======================================================================
cdef class Join:
    cdef tuple index
    cdef unsigned[::1] mappingA
    cdef unsigned[::1] mappingB

    @staticmethod
    cdef Join create(tuple index, unsigned[::1] mappingA, unsigned[::1] mappingB):
        cdef Join join = Join.__new__(Join)
        join.index = index
        join.mappingA = mappingA
        join.mappingB = mappingB

        return join

    cdef tuple as_tuple(self):
        """
        Convert a Join structure to a tuple.

        For testing purposes.
        """
        return (self.index, self.mappingA, self.mappingB)

def join(seqA, seqB):
    return c_join(seqA, seqB)


cdef Sequence c_join(Sequence seqA, Sequence seqB):
    cdef tuple indexA = seqA._index.get_py_values()
    cdef tuple indexB = seqB._index.get_py_values()

    cdef Join join = c_index_join(indexA, indexB)
    cdef list columns = []
    cdef Column column

    for column in seqA._columns:
        columns.append(column.c_remap(len(join.mappingA), &join.mappingA[0]))
    for column in seqB._columns:
        columns.append(column.c_remap(len(join.mappingB), &join.mappingB[0]))

    return Sequence(join.index, *columns)

def index_join(indexA, indexB):
    """
    Python wrapper around `c_index_join`.

    For testing purposes.
    """
    return c_index_join(indexA, indexB).as_tuple()

cdef Join c_index_join(tuple indexA, tuple indexB):
    """
    Join seqA and seqB using their index.
    """
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

    return Join.create(tuple(joinIndex), mappingA[::1], mappingB[::1])
