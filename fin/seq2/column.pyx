from cpython cimport array
from cpython.object cimport Py_EQ, Py_NE
from fin.mathx cimport NaN, isnan

import array

# ======================================================================
# Globals
# ======================================================================
cdef unsigned   _id = 0

# ======================================================================
# Errors
# ======================================================================
class ColumnSizeMismatchError(ValueError):
    def __init__(self, colA, colB):
        super().__init__(f"Column size mismatch ({len(colA)} and {len(colB)})")

# ======================================================================
# Utilities
# ======================================================================
cpdef Column as_column(obj):
    try:
        return <Column?>obj
    except TypeError:
        return Column.from_sequence(obj)

cdef Column new_column_with_meta(Column other):
    cdef Column result = Column()
    # _id is filled by __cinit__
    result._name = other._name
    result._formatter = other._formatter

    return result

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
cdef Column add_column_scalar(Column column, double scalar):
    """
    Column to scalar addition.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef Column result = new_column_with_meta(column)
    result._name = f"({column.get_name()}+{scalar})"

    cdef array.array values = column.get_f_values()
    result._f_values = add_vector_scalar(
            len(values),
            values.data.as_doubles,
            scalar
    )

    return result

cdef Column add_column_column(Column a, Column b):
    """
    Column to column addition.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef array.array arrA = a.get_f_values()
    cdef array.array arrB = b.get_f_values()
    cdef unsigned lenA = len(arrA)
    cdef unsigned lenB = len(arrB)

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a)
    result._name = f"({a.get_name()}+{b.get_name()})"
    if result._formatter is None:
        result._formatter = b._formatter

    result._f_values = add_vector_vector(
            lenA,
            arrA.data.as_doubles,
            arrB.data.as_doubles
    )

    return result

cdef array.array add_vector_scalar(unsigned count, const double* values, double other):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = values[i] + other

    return arr

cdef array.array add_vector_vector(unsigned count, const double* a, const double* b):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = a[i] + b[i]

    return arr

# ----------------------------------------------------------------------
# Multiplication
# ----------------------------------------------------------------------
cdef Column mul_column_scalar(Column column, double scalar):
    """
    Column to scalar multiplication.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef Column result = new_column_with_meta(column)
    result._name = f"({column.get_name()}*{scalar})"

    cdef array.array values = column.get_f_values()
    result._f_values = mul_vector_scalar(
            len(values),
            values.data.as_doubles,
            scalar
    )

    return result

cdef Column mul_column_column(Column a, Column b):
    """
    Column to column multiplication.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef array.array arrA = a.get_f_values()
    cdef array.array arrB = b.get_f_values()
    cdef unsigned lenA = len(arrA)
    cdef unsigned lenB = len(arrB)

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a)
    result._name = f"({a.get_name()}*{b.get_name()})"
    if result._formatter is None:
        result._formatter = b._formatter

    result._f_values = mul_vector_vector(
            lenA,
            arrA.data.as_doubles,
            arrB.data.as_doubles
    )

    return result

cdef array.array mul_vector_scalar(unsigned count, const double* values, double other):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = values[i] * other

    return arr

cdef array.array mul_vector_vector(unsigned count, const double* a, const double* b):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = a[i] * b[i]

    return arr

# ----------------------------------------------------------------------
# Division
# ----------------------------------------------------------------------
cdef Column div_column_scalar(Column column, double scalar):
    """
    Column to scalar division.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef Column result = new_column_with_meta(column)
    result._name = f"({column.get_name()}/{scalar})"

    cdef array.array values = column.get_f_values()
    result._f_values = div_vector_scalar(
            len(values),
            values.data.as_doubles,
            scalar
    )

    return result

cdef Column div_column_column(Column a, Column b):
    """
    Column to column multiplication.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef array.array arrA = a.get_f_values()
    cdef array.array arrB = b.get_f_values()
    cdef unsigned lenA = len(arrA)
    cdef unsigned lenB = len(arrB)

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a)
    result._name = f"({a.get_name()}/{b.get_name()})"
    if result._formatter is None:
        result._formatter = b._formatter

    result._f_values = div_vector_vector(
            lenA,
            arrA.data.as_doubles,
            arrB.data.as_doubles
    )

    return result

cdef array.array div_vector_scalar(unsigned count, const double* values, double other):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = values[i] / other

    return arr

cdef array.array div_vector_vector(unsigned count, const double* a, const double* b):
    cdef array.array arr = array.clone(_double_array_template, count, zero=False)
    cdef unsigned i

    for i in range(count):
        arr.data.as_doubles[i] = a[i] / b[i]

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
    def __cinit__(self):
        global _id

        self._id = _id
        _id += 1

    def __init__(self, *, name=None, formatter=None):
        if name is not None:
            self._name = str(name)
        if formatter is not None:
            self._formatter = formatter

    # ------------------------------------------------------------------
    # Factiry methods
    # ------------------------------------------------------------------
    @staticmethod
    def from_sequence(sequence, **kwargs):
        """
        Create a Column from a sequence of Python ojects.
        """
        cdef Column column = Column(**kwargs)
        column._py_values = tuple(sequence)

        return column

    @staticmethod
    def from_float_array(arr, **kwargs):
        """
        Create a Column from an array of floats.

        This is an efficient "zero-copy" operation.
        You MUST treat the original array's content as an immutable object.
        """
        cdef Column column = Column(**kwargs)
        column._f_values = arr # type checking is implicitly done here

        return column

    @staticmethod
    def from_callable(fct, *columns, **kwargs):
        name = kwargs.get("name")
        formatter = kwargs.get("formatter")

        if name is None:
            try:
                params = [ column.name for column in columns ]
                name = f"{fct}({', '.join(params)})"
            except AttributeError:
                # A column is not an instance of Column!
                name = "?"

        if formatter is None:
            for column in columns:
                try:
                    formatter = column.formatter
                    if formatter is not None:
                        break
                except AttributeError:
                    # A column is not an instance of Column!
                    pass

        return Column.from_sequence(
                [fct(*row) for row in zip(*columns)],
                name = name,
                formatter = formatter,
        )

    # ------------------------------------------------------------------
    # Access to the polymorphic underlying representation
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    @property
    def name(self):
        return self.get_name()

    cdef str get_name(self):
        if self._name is None:
            self._name = f":{self._id:06}"

        return self._name

    @property
    def formatter(self):
        return self.get_formatter()

    cdef object get_formatter(self):
        return self._formatter


    def metadata(self, name, default=None):
        if self._metadata is None:
            return default

        return self._metadata.get(name, default)

    def set_metadata(self, **kwargs):
        if self._metadata is None:
            self._metadata = kwargs
        else:
            self._metadata.update(kwargs)

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
        parts = [ repr(self.py_values) ]
        if self._name:
            parts.append(f"name={self._name!r}")
        if self._formatter:
            parts.append(f"formatter={self._formatter!r}")

        return f"Column({', '.join(parts)})"

    def __len__(self):
        if self._f_values:
            return len(self._f_values)
        if self._py_values:
            return len(self._py_values)

        raise NotImplementedError()

    def __getitem__(self, x):
        if type(x) is slice:
            column = new_column_with_meta(self)
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

    # ------------------------------------------------------------------
    # Copy
    # ------------------------------------------------------------------
    cdef Column c_remap(self, unsigned count, const unsigned* mapping):
        """
        Create a copy of the column with values picked from the index specificed in `mapping`.
        """
        cdef Column result = new_column_with_meta(self)
        if self._f_values is not None:
            result._f_values = remap_from_f_values(self._f_values.data.as_doubles, count, mapping)
        elif self._py_values is not None:
            result._py_values = remap_from_py_values(self._py_values, count, mapping)
        else:
            raise NotImplementedError()

        return result

    def rename(self, newName):
        return self.c_rename(newName)

    cdef Column c_rename(self, str newName):
        cdef Column result = new_column_with_meta(self)
        result._f_values = self._f_values
        result._py_values = self._py_values

        result._name = newName

        return result

    # ------------------------------------------------------------------
    # Addition
    # ------------------------------------------------------------------
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return add_column_scalar(self, other)
        elif isinstance(other, Column):
            return add_column_column(self, other)
        else:
            return NotImplemented

    cdef Column c_add_scalar(self, double scalar):
        return add_column_scalar(self, scalar)

    # ------------------------------------------------------------------
    # Subtraction
    # ------------------------------------------------------------------
    def __sub__(self, other):
        return self + -other

    cdef Column c_sub_scalar(self, double scalar):
        return add_column_scalar(self, -scalar)

    # ------------------------------------------------------------------
    # Multiplication
    # ------------------------------------------------------------------
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return mul_column_scalar(self, other)
        elif isinstance(other, Column):
            return mul_column_column(self, other)
        else:
            return NotImplemented

    cdef Column c_mul_scalar(self, double scalar):
        return mul_column_scalar(self, scalar)

    # ------------------------------------------------------------------
    # Division
    # ------------------------------------------------------------------
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return div_column_scalar(self, other)
        elif isinstance(other, Column):
            return div_column_column(self, other)
        else:
            return NotImplemented

    cdef Column c_div_scalar(self, double scalar):
        return div_column_scalar(self, scalar)

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

        cdef Column result = new_column_with_meta(self)
        result._name = f"-{self.get_name()}"
        result._f_values = neg(count, values.data.as_doubles)

        return result


    def remap(self, mapping):
        cdef array.array arr = array.array("I", mapping)

        return self.c_remap(len(mapping), arr.data.as_uints)
