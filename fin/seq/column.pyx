from cpython cimport array
from cpython.object cimport Py_EQ, Py_NE
from fin.mathx cimport NaN, isnan

import array

# ======================================================================
# Utilities
# ======================================================================
cpdef str get_column_name(col):
    try:
        return col.name
    except AttributeError:
        return None

cdef from_sequence(sequence):
    return (x if x is not None else NaN for x in sequence)

cdef to_sequence(double[::1] view):
    return [ None if isnan(x) else x for x in view]

cpdef Column as_column(obj):
    try:
        return <Column?>obj
    except TypeError:
        return Column.from_sequence(get_column_name(obj), obj)

# ======================================================================
# Column class
# ======================================================================
cdef class AnyColumn:
    def as_column(self):
        return self

    def min_max(self):
        """
        Return the minimum and maximum values in the column.
        None values are ignored.
        """
        values = [v for v in self.values if v is not None]
        return min(values), max(values)

cdef class FColumn(AnyColumn):
    """
    A Fast float column.

    This is an intermediate representation of a column used to speedup calculations.
    """
    def __init__(self, name, double[::1] values):
        self.values = values
        self.name = name

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        """
        Make the column iterable.
        """
        return iter(to_sequence(self.values))

    def __getitem__(self, index):
        return self.values[index]

    def __repr__(self):
        values_str = ", ".join(map(str, self.values))
        return f"FColumn({self.name}, ({values_str}))"

    def named(self, name):
        return FColumn(name, self.values)

    def slice(self, start, end=None):
        """
        Return a new column containing a copy of the data in the range [start;end)

        Negative values for `start` or `end` are not allowed.
        """
        if end is None:
            end = len(self.values)

        assert end >= start >= 0

        return FColumn(self.name, self.values[start:end])

cpdef FColumn fcolumn_from_slice(name, double[::1] slice):
    return FColumn(name, slice)

cpdef FColumn fcolumn_from_sequence(name, sequence):
    lst = [x if x is not None else NaN for x in sequence]
    cdef array.array arr = array.array("d", lst)
    cdef double[::1] values = arr[::1]
    return FColumn(name or get_column_name(sequence), values)

cdef array.array _double_array_template = array.array("d")

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

cdef class Column:
    """
    A column.

    Column are immutable ojects (or at least the should be treated that way).
    A column may have several representations, for example as a tuple of Python objects,
    and as an array of floats.

    This is this class responsability to ensure the different representations are consistent
    and created on demand.
    """
    def __init__(self, name):
        self._name = name

    @staticmethod
    def from_sequence(name, sequence):
        """
        Create a Column from a sequence of Python ojects.
        """
        cdef Column column = Column(name)
        column._py_values = tuple(sequence)

        return column

    @staticmethod
    def from_float_array(name, arr):
        """
        Create a Column from an array of floats.

        This is an efficient "zero-copy" operation.
        You MUST treat the original array's content as an immutable object.
        """
        cdef Column column = Column(name)
        column._f_values = arr

        return column

    @property
    def name(self):
        return self._name

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
        return f"Column({self.name!r}, {self.py_values!r})"

    def __len__(self):
        if self._py_values:
            return len(self._py_values)
        if self._f_values:
            return len(self._f_values)

        raise NotImplementedError()

    def __getitem__(self, x):
        if type(x) is slice:
            column = Column(self.name)
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

    def named(self, name):
        """
        Return a copy of the column with a different name.
        """
        column = Column(name)
        column._py_values = self._py_values
        column._f_values = self._f_values

        return column

class OldColumn(AnyColumn):

    # __slots__ = (
    #         "values",
    #         "name",
    #         )
    # Above: ^^^^^^^^^
    # __slots__ break when inheriting from a cdef class (using Cython 0.26.1)

    def __init__(self, name, sequence):
        self.name = name
        if type(sequence) is not tuple:
            sequence = tuple(sequence)
        self.values = sequence

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]

    def __eq__(self, other):
        if not isinstance(other, Column):
            return False

        if self.values != other.values:
            return False
        if self.name != other.name:
            return False

        return True

    def __repr__(self):
        return "Column(\"{}\", {})".format(self.name, self.values)

    def named(self, name):
        return Column(name, self.values)

    def slice(self, start, end=None):
        """
        Return a new column containing a copy of the data in the range [start;end)

        Negative values for `start` or `end` are not allowed.
        """
        if end is None:
            end = len(self.values)

        assert end >= start >= 0

        return Column(self.name, self.values[start:end])

    def alter(self, **kwargs):
        """
        Create a new column with the same values but altered metadata.
        """
        name = kwargs.get("name", None) or self.name

        return Column(name, self.values)

    def type(self):
        """
        Return the type of data stored in the column.

        Currently, the type is extrapolated from the actual data.
        If the content of a column is homogeneous (all values of the same type or None),
        that type is returned. Otherwise, None is returned.
        """
        t = None
        it = iter(self.values)
        for v in it:
            if v is not None:
                t = type(v)
                break
        else:
            return None

        for v in it:
            if v is not None:
                if type(v) is not t:
                    return None

        return t
