from cpython cimport array
from fin.mathx cimport NaN, isnan

import array

# ======================================================================
# Utilities
# ======================================================================
def get_column_name(col):
    try:
        return col.name
    except AttributeError:
        return None

cdef from_sequence(sequence):
    return (x if x is not None else NaN for x in sequence)

cdef to_sequence(double[::1] view):
    return [ None if isnan(x) else x for x in view]

def as_column(obj):
    try:
        return obj.as_column()
    except AttributeError:
        return Column(None, obj)

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

cpdef FColumn as_fcolumn(sequence):
    try:
        return <FColumn?>sequence
    except TypeError:
        return fcolumn_from_sequence(get_column_name(sequence), sequence)

class Column(AnyColumn):

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
