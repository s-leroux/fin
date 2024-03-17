from cpython cimport array
from cpython.object cimport Py_EQ, Py_NE
from fin.mathx cimport NaN, isnan

import array

# ======================================================================
# Errors
# ======================================================================
class ColumnSizeMismatchError(ValueError):
    def __init__(self, colA, colB):
        super().__init__(f"Column size mismatch ({len(colA)} and {len(colB)})")

# ======================================================================
# Utilities
# ======================================================================
cdef from_sequence(sequence):
    return (x if x is not None else NaN for x in sequence)

cdef to_sequence(double[::1] view):
    return [ None if isnan(x) else x for x in view]

cpdef Column as_column(obj):
    try:
        return <Column?>obj
    except TypeError:
        return Column.from_sequence(obj)

# ======================================================================
# Low-level operations
# ======================================================================
cdef array.array _double_array_template = array.array("d")

# ----------------------------------------------------------------------
# Conversion
# ----------------------------------------------------------------------
cpdef array.array f_values_from_py_values(tuple sequence):
    cdef unsigned n = len(sequence)
    cdef unsigned i
    cdef array.array arr = array.clone(_double_array_template, n, zero=False)

    for i in range(n):
        arr.data.as_doubles[i] = NaN if sequence[i] is None else sequence[i]
    
    return arr

cpdef tuple py_values_from_f_values(array.array arr):
    cdef unsigned n = len(arr)
    cdef const double* src = arr.data.as_doubles
    cdef list lst = arr.tolist()

    cdef unsigned i
    for i in range(n):
        if isnan(src[i]):
            lst[i] = None

    return tuple(lst) # Enforce immutability

# ----------------------------------------------------------------------
# Addition
# ----------------------------------------------------------------------
cdef array.array add_scalar(unsigned count, const double* values, double other):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = values[i] + other

    return arr

cdef array.array add_vector(unsigned count, const double* a, const double* b):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = a[i] + b[i]

    return arr

# ----------------------------------------------------------------------
# Unary negation
# ----------------------------------------------------------------------
cdef array.array neg(unsigned count, const double* values):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = -values[i]

    return arr

# ----------------------------------------------------------------------
# Column remapping
# ----------------------------------------------------------------------
cdef array.array remap_from_f_values(double* values, unsigned count, const unsigned* mapping):
    """
    Remap an array of double using the indices provided in `mapping`.

    The result array is newly allocated here and returned as a Cython `array.array`.

    Low-level function.
    """
    cdef array.array result = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        result.data.as_doubles[i] = values[mapping[i]]

    return result

cdef tuple remap_from_py_values(tuple values, unsigned count, const unsigned* mapping):
    """
    Remap an array of Python objects using the indices provided in `mapping`.

    The result tuple is newly allocated here and returned as a Python object.

    Low-level function.
    """
    cdef list  result = [None,]*count
    cdef unsigned i

    for i in range(count):
        result[i] = values[mapping[i]]

    return tuple(result)
    

# ======================================================================
# Column class
# ======================================================================
cdef class Column:
    """
    A column.

    Columns are immutable ojects (or at least the should be treated that way).
    A column may have several representations, for example as a tuple of Python objects,
    and as an array of floats.

    This is this class responsability to ensure the different representations are consistent
    and created on demand.
    """
    def __init__(self):
        pass

    @staticmethod
    def from_sequence(sequence):
        """
        Create a Column from a sequence of Python ojects.
        """
        cdef Column column = Column()
        column._py_values = tuple(sequence)

        return column

    @staticmethod
    def from_float_array(arr):
        """
        Create a Column from an array of floats.

        This is an efficient "zero-copy" operation.
        You MUST treat the original array's content as an immutable object.
        """
        cdef Column column = Column()
        column._f_values = arr # type checking is implicitly done here

        return column

    @property
    def py_values(self):
        return self.get_py_values()

    cdef tuple get_py_values(self):
        """
        Return the content of the column as a sequence of Python objects.
        """
        if self._py_values:
            return self._py_values

        # else
        if self._f_values:
            self._py_values = py_values_from_f_values(self._f_values)
            return self._py_values

        # else
        raise NotImplementedError()

    @property
    def f_values(self):
        return self.get_f_values()

    cdef array.array get_f_values(self):
        """
        Return the content of the column as an array of floats.
        """
        if self._f_values:
            return self._f_values

        # else
        if self._py_values:
            self._f_values = f_values_from_py_values(self._py_values)
            return self._f_values

        # else
        raise NotImplementedError()

    def min_max(self):
        """
        Return the minimum and maximum values in the column.
        None values are ignored.
        """
        values = [v for v in self.py_values if v is not None]
        return min(values), max(values)

    def __richcmp__(self, other, int op):
        """
        Compare if two columns are equal.
        """
        if isinstance(other, Column):
            if op == Py_EQ:
                return self.py_values == other.py_values
            if op == Py_NE:
                return self.py_values != other.py_values

        raise NotImplementedError()

    def __repr__(self):
        return f"Column({self.py_values!r})"

    def __len__(self):
        if self._f_values:
            return len(self._f_values)
        if self._py_values:
            return len(self._py_values)

        raise NotImplementedError()

    def __getitem__(self, x):
        if type(x) is slice:
            column = Column()
            # XXX Do we really need to slice all representations?
            if self._f_values is not None:
                column._f_values = self._f_values[x]
            if self._py_values is not None:
                column._py_values = self._py_values[x]
            return column

        if self._py_values is not None:
            return self._py_values[x]
        if self._f_values is not None:
            return self._f_values[x]

        raise NotImplementedError()

    def __iter__(self):
        """
        Return an iterator over the column as a sequence of Python objects.

        By convention we always iterate over `self.py_values` in order to
        ensure consistent results (especially regarding the None <-> nan implied conversion).

        EXPERIMENTAL.
        """
        return iter(self.py_values)

    cdef Column c_remap(self, unsigned count, const unsigned* mapping):
        """
        Create a copy of the column with values picked from the index specificed in `mapping`.
        """
        cdef Column result = Column()
        if self._f_values is not None:
            result._f_values = remap_from_f_values(self._f_values.data.as_doubles, count, mapping)
        elif self._py_values is not None:
            result._py_values = remap_from_py_values(self._py_values, count, mapping)
        else:
            raise NotImplementedError()

        return result

    # ------------------------------------------------------------------
    # Addition
    # ------------------------------------------------------------------
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return (<Column>self).c_add_scalar(other) # Cast required here. Bug with Cython 0.26 ?
        elif isinstance(other, Column):
            return (<Column>self).c_add_column(other)
        else:
            return NotImplemented

    cdef Column c_add_scalar(self, double scalar):
        """
        Column to scalar addition.

        This method performs an implicit conversion to float values.

        TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
        """
        cdef Column result = Column()
        cdef array.array values = self.get_f_values()
        result._f_values = add_scalar(
                len(values),
                values.data.as_doubles,
                scalar
        )

        return result

    cdef Column c_add_column(self, Column value):
        """
        Column to column addition.

        This method performs an implicit conversion to float values.

        TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
        """
        cdef array.array arrA = self.get_f_values()
        cdef array.array arrB = value.get_f_values()
        cdef unsigned lenA = len(arrA)
        cdef unsigned lenB = len(arrB)

        if lenB != lenA:
            raise ColumnSizeMismatchError(self, value)

        cdef Column result = Column()
        result._f_values = add_vector(
                lenA,
                arrA.data.as_doubles,
                arrB.data.as_doubles
        )

        return result

    # ------------------------------------------------------------------
    # Subtraction
    # ------------------------------------------------------------------
    def __sub__(self, other):
        return self + -other

    # ------------------------------------------------------------------
    # Unary negation
    # ------------------------------------------------------------------
    def __neg__(self):
        """
        Unary negation.

        This method performs an implicit conversion to float values.

        TODO: If implicit conversion raise an error, fallback to cell-by-cell negation.
        """
        cdef array.array values = self.get_f_values()
        cdef unsigned count = len(values)

        cdef Column result = Column()
        result._f_values = neg(count, values.data.as_doubles)

        return result


    def remap(self, mapping):
        cdef array.array arr = array.array("I", mapping)

        return self.c_remap(len(mapping), arr.data.as_uints)
