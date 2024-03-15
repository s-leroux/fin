from cpython cimport array
import array

from fin.seq2.column cimport Column

# ======================================================================
# Globals
# ======================================================================
cdef array.array    int_array       = array.array("i", [])
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
        self._name= "Sequence"
        self._index = index
        self._columns = columns

    def name(self):
        return self._name

# ======================================================================
# Join
# ======================================================================
cdef join(Column seqA, Column seqB, name=None):
    if name is None:
        name = f"{seqA.name()} ∩ {seqB.name()}"

    cdef tuple indexA = seqA.get_py_values()
    cdef tuple indexB = seqB.get_py_values()

    mapping = index_join(indexA, indexB)

def index_join(indexA, indexB):
    return c_index_join(indexA, indexB)

cdef c_index_join(tuple indexA, tuple indexB):
    """
    Join seqA and seqB using their index.
    """
    cdef unsigned lenA = len(indexA)
    cdef unsigned lenB = len(indexB)

    # At worst, we will have min(lenA, lenB) rows in the inner join
    cdef unsigned lenMapping = lenA if lenA < lenB else lenB
    cdef array.array mappingA = array.clone(int_array, lenMapping, zero=False)
    cdef array.array mappingB = array.clone(int_array, lenMapping, zero=False)

    cdef unsigned i = 0
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
            mappingA.data.as_uints[i] = posA
            mappingB.data.as_uints[i] = posB
            i += 1
            posA += 1
            posB += 1
            if posA == lenA or posB == lenB:
                break

    # shrink array to their correct length:
    array.resize(mappingA, i)
    array.resize(mappingB, i)

    return (mappingA, mappingB)
