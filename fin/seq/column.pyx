from cpython cimport array
from cpython.object cimport Py_EQ, Py_NE
from fin.mathx cimport NaN, isnan

import array
from fin.seq import coltypes
from fin.seq cimport coltypes

from fin cimport mem

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

cdef Column new_column_with_meta(Column other, length, type=None, name=None):
    cdef Column result = Column()
    # _id is filled by __cinit__
    result.length = length
    result._name = name if name is not None else other._name
    result._type = coltypes.parse_type_atom(type) if type is not None else other._type

    return result

# ======================================================================
# Low-level operations
# ======================================================================
ctypedef signed char schar

# ----------------------------------------------------------------------
# Conversion
# ----------------------------------------------------------------------
cpdef double[::1] f_values_from_py_values(Tuple sequence):
    cdef unsigned n = len(sequence)
    cdef unsigned i
    cdef double[::1] arr = mem.double_alloc(n)

    for i in range(n):
        arr[i] = NaN if sequence[i] is None else sequence[i]

    return arr

cpdef Tuple py_values_from_f_values(double[::1] arr):
    cdef unsigned n = len(arr)
    cdef const double* src = &arr[0]
    cdef list lst = []

    cdef unsigned i
    for i in range(n):
        lst.append(None if isnan(src[i]) else src[i])

    return Tuple.create(n, lst)

cpdef signed char[::1] t_values_from_py_values(Tuple sequence):
    """ Convert a column to a list of values in ternary logic.

        Here, false is -1, unknown is 0 and true is +1

        See https://en.wikipedia.org/wiki/Three-valued_logic
        and https://homepage.cs.uiowa.edu/~dwjones/ternary/logic.shtml
    """
    cdef unsigned n = len(sequence)
    cdef unsigned i
    cdef signed char[::1] arr = mem.schar_alloc(n)
    cdef signed char tmp
    cdef object obj

    for i in range(n):
        obj = sequence[i]
        if obj is None:
            tmp = 0
        elif obj:
            tmp = 1
        else:
            tmp = -1

        arr[i] = tmp

    return arr

cpdef Tuple py_values_from_t_values(signed char[::1] arr):
    cdef unsigned n = len(arr)
    cdef const signed char* src = &arr[0]
    cdef list lst = []

    cdef unsigned i
    for i in range(n):
        if src[i] == 0:
            lst.append(None)
        elif src[i] > 0:
            lst.append(True)
        else:
            lst.append(False)

    return Tuple.create(n, lst)

# ----------------------------------------------------------------------
# Addition
# ----------------------------------------------------------------------
cdef Column add_column_scalar(Column column, double scalar):
    """
    Column to scalar addition.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef Column result = new_column_with_meta(column, column.length, type="n")
    result._name = f"({column.get_name()}+{scalar})"

    result._f_values = add_vector_scalar(
            column.length,
            column.as_float_values(),
            scalar
    )

    return result

cdef Column add_column_column(Column a, Column b):
    """
    Column to column addition.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef unsigned lenA = a.length
    cdef unsigned lenB = b.length

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a, lenA, type="n")
    result._name = f"({a.get_name()}+{b.get_name()})"

    result._f_values = add_vector_vector(
            lenA,
            a.as_float_values(),
            b.as_float_values(),
    )

    return result

cdef double[::1] add_vector_scalar(unsigned count, const double* values, double other):
    cdef double[::1] arr = mem.double_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = values[i] + other

    return arr

cdef double[::1] add_vector_vector(unsigned count, const double* a, const double* b):
    cdef double[::1] arr = mem.double_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = a[i] + b[i]

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
    cdef Column result = new_column_with_meta(column, column.length, type="n")
    result._name = f"({column.get_name()}*{scalar})"

    result._f_values = mul_vector_scalar(
            column.length,
            column.as_float_values(),
            scalar
    )

    return result

cdef Column mul_column_column(Column a, Column b):
    """
    Column to column multiplication.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef unsigned lenA = a.length
    cdef unsigned lenB = b.length

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a, lenA, type="n")
    result._name = f"({a.get_name()}*{b.get_name()})"

    result._f_values = mul_vector_vector(
            lenA,
            a.as_float_values(),
            b.as_float_values(),
    )

    return result

cdef double[::1] mul_vector_scalar(unsigned count, const double* values, double other):
    cdef double[::1] arr = mem.double_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = values[i] * other

    return arr

cdef double[::1] mul_vector_vector(unsigned count, const double* a, const double* b):
    cdef double[::1] arr = mem.double_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = a[i] * b[i]

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
    cdef Column result = new_column_with_meta(column, column.length, type="n")
    result._name = f"({column.get_name()}/{scalar})"

    result._f_values = div_vector_scalar(
            column.length,
            column.as_float_values(),
            scalar
    )

    return result

cdef Column div_column_column(Column a, Column b):
    """
    Column to column multiplication.

    This method performs an implicit conversion to float values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef unsigned lenA = a.length
    cdef unsigned lenB = b.length

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a, lenA, type="n")
    result._name = f"({a.get_name()}/{b.get_name()})"

    result._f_values = div_vector_vector(
            lenA,
            a.as_float_values(),
            b.as_float_values(),
    )

    return result

cdef double[::1] div_vector_scalar(unsigned count, const double* values, double other):
    cdef double[::1] arr = mem.double_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = values[i] / other

    return arr

cdef double[::1] div_vector_vector(unsigned count, const double* a, const double* b):
    cdef double[::1] arr = mem.double_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = a[i] / b[i]

    return arr

# ----------------------------------------------------------------------
# Unary negation
# ----------------------------------------------------------------------
cdef double[::1] neg(unsigned count, const double* values):
    cdef double[::1] arr = mem.double_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = -values[i]

    return arr

# ----------------------------------------------------------------------
# Bitwise and
# ----------------------------------------------------------------------
cdef Column and_column_column(Column a, Column b):
    """
    Column to column logical and.

    This method performs an implicit conversion to ternary values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef unsigned lenA = a.length
    cdef unsigned lenB = b.length

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a, lenA)
    result._name = f"({a.get_name()}&{b.get_name()})"
    if result._type is None:
        result._type = b._type

    result._t_values = and_vector_vector(
            lenA,
            a.as_ternary_values(),
            b.as_ternary_values(),
    )

    return result

cdef signed char[::1] and_vector_vector(unsigned count, const signed char* a, const signed char* b):
    cdef signed char[::1] arr = mem.schar_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = a[i] if a[i] < b[i] else b[i]
        # In balanced ternary logic, and() is the same as min()

    return arr

# ----------------------------------------------------------------------
# Bitwise or
# ----------------------------------------------------------------------
cdef Column or_column_column(Column a, Column b):
    """
    Column to column logical or.

    This method performs an implicit conversion to ternary values.

    TODO: If implicit conversion raise an error, fallback to cell-by-cell addition.
    """
    cdef unsigned lenA = a.length
    cdef unsigned lenB = b.length

    if lenB != lenA:
        raise ColumnSizeMismatchError(a, b)

    cdef Column result = new_column_with_meta(a, lenA)
    result._name = f"({a.get_name()}|{b.get_name()})"
    if result._type is None:
        result._type = b._type

    result._t_values = or_vector_vector(
            lenA,
            a.as_ternary_values(),
            b.as_ternary_values(),
    )

    return result

cdef signed char[::1] or_vector_vector(unsigned count, const signed char* a, const signed char* b):
    cdef signed char[::1] arr = mem.schar_alloc(count)
    cdef unsigned i

    for i in range(count):
        arr[i] = a[i] if a[i] > b[i] else b[i]
        # In balanced ternary logic, or() is the same as max()

    return arr

# ----------------------------------------------------------------------
# Column remapping
# ----------------------------------------------------------------------
ctypedef fused integral_column_t:
    signed char
    double

cdef integral_column_t[::1] remap_values(integral_column_t *values, unsigned count, const unsigned* mapping):
    """
    Remap an array of double using the indices provided in `mapping`.

    The result array is newly allocated here and returned as a Cython `array.array`.

    Low-level function.
    """
    cdef integral_column_t[::1] result
    cdef integral_column_t undefined

    if integral_column_t is double:
        result = mem.double_alloc(count)
        undefined = NaN
    else:
        result = mem.schar_alloc(count)
        undefined = 0

    cdef integral_column_t *dst = &result[0]
    cdef unsigned i
    cdef unsigned idx
    cdef unsigned MISSING=-1
    # XXX Above:
    # replace by a global constant when it will be properly supported by Cython

    for i in range(count):
        idx = mapping[i]
        dst[i] = values[idx] if idx != MISSING else undefined

    return result


cdef double[::1] get_f_values(Column self):
    """
    Return the content of the column as an array of floats.
    """
    if self._f_values is not None:
        return self._f_values

    # Not cached and no direct conversion implemented. Fallback to the slow path.
    if self._py_values is None:
        self.get_py_values()

    self._f_values = f_values_from_py_values(self._py_values)
    return self._f_values

cdef signed char[::1] get_t_values(Column self):
    """
    Return the content of the column as an array of ternary values.
    """
    if self._t_values is not None:
        return self._t_values

    # Not cached and no direct conversion implemented. Fallback to the slow path.
    if self._py_values is None:
        self.get_py_values()

    self._t_values = t_values_from_py_values(self._py_values)
    return self._t_values

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
        self._t_values = None
        self._f_values = None

    def __init__(self, *, name=None, type=None):
        if name is not None:
            self._name = str(name)
        if type is not None:
            self._type = coltypes.parse_type_atom(type)
        else:
            self._type = coltypes.Other()

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------
    @staticmethod
    def from_constant(count, k, name=None,**kwargs):
        """
        Create a Column from a constant value.
        """
        if name is None:
            name = str(k)

        cdef Column column = Column(name=name, **kwargs)
        column._py_values = Tuple.from_constant(count, k)
        column.length = count

        return column

    @staticmethod
    def from_sequence(sequence, **kwargs):
        """
        Create a Column from a sequence of Python objects.
        """
        cdef Column column = Column(**kwargs)
        column._py_values = Tuple.from_sequence(sequence)
        column.length = len(column._py_values)

        return column

    @staticmethod
    def from_float_mv(double[::1] arr, **kwargs):
        """
        Create a Column from an array of floats.

        This is an efficient "zero-copy" operation.
        You MUST treat the original array's content as an immutable object.
        """
        cdef Column column = Column(**kwargs)
        column._f_values = arr
        column.length = arr.shape[0]

        return column

    @staticmethod
    def from_ternary_mv(signed char[::1] arr, **kwargs):
        """
        Create a Column from an array of signed chars.

        This is an efficient "zero-copy" operation.
        You MUST treat the original array's content as an immutable object.
        """
        cdef Column column = Column(**kwargs)
        column._t_values = arr
        column.length = arr.shape[0]

        return column

    @staticmethod
    def from_callable(fct, *columns, name=None, type=None, **kwargs):
        if name is None:
            try:
                params = [ column.name for column in columns ]
                name = f"{fct}({', '.join(params)})"
            except AttributeError:
                # A column is not an instance of Column!
                name = "?"

        if type is None:
            for column in columns:
                try:
                    type = column.type
                    if type is not None:
                        break
                except AttributeError:
                    # A column is not an instance of Column!
                    pass

        return Column.from_sequence(
                [fct(*row) for row in zip(*columns)],
                name = name,
                type = type,
                **kwargs
        )

    # ------------------------------------------------------------------
    # Access to the polymorphic underlying representation
    # ------------------------------------------------------------------
    @property
    def py_values(self):
        return self.get_py_values()

    cdef Tuple get_py_values(self):
        """
        Return the content of the column as a sequence of Python objects.
        """
        if self._py_values is not None:
            return self._py_values

        # else
        if self._f_values is not None:
            self._py_values = py_values_from_f_values(self._f_values)
            return self._py_values

        # else
        if self._t_values is not None:
            self._py_values = py_values_from_t_values(self._t_values)
            return self._py_values

        # else
        raise NotImplementedError()

    @property
    def f_values(self):
        return get_f_values(self)

    cdef const double* as_float_values(self) except NULL:
        if self._f_values is None:
            get_f_values(self) # This may raise an exception!

        return &self._f_values[0]

    @property
    def t_values(self):
        return get_t_values(self)

    cdef const signed char* as_ternary_values(self) except NULL:
        if self._t_values is None:
            get_t_values(self) # This may raise an exception!

        return &self._t_values[0]


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

    def format(self, context):
        return self._type.format(context, self)

    @property
    def type(self):
        return self.get_type()

    cdef object get_type(self):
        return self._type


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
        if isinstance(other, Column) and isinstance(self, Column):
            if op == Py_EQ:
                return self.py_values == other.py_values
            if op == Py_NE:
                return self.py_values != other.py_values

        return NotImplemented

    def __repr__(self):
        parts = [ repr(self.py_values) ]
        if self._name:
            parts.append(f"name={self._name!r}")
        if self._type:
            parts.append(f"type={self._type!r}")

        return f"Column({', '.join(parts)})"

    def __len__(self):
        return self.length

    def __getitem__(self, x):
        cdef slice  sl
        if type(x) is slice:
            sl = <slice>x
            if sl.step is not None and sl.step != 1:
                raise ValueError(f"Only contiguous slices are supported ({sl})")

            column = new_column_with_meta(self, 0)
            # XXX Do we really need to slice all representations?
            if self._f_values is not None:
                column._f_values = self._f_values[sl.start:sl.stop]
                column.length = len(column._f_values)
            if self._t_values is not None:
                column._t_values = self._t_values[sl.start:sl.stop]
                column.length = len(column._t_values)
            if self._py_values is not None:
                column._py_values = self._py_values.slice(x.start, x.stop)
                column.length = len(column._py_values)
            return column

        if self._py_values is not None:
            return self._py_values[<Py_ssize_t>x]
        if self._f_values is not None:
            return self._f_values[<Py_ssize_t>x]
        if self._t_values is not None:
            return self._t_values[<Py_ssize_t>x]

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
        cdef Column result = new_column_with_meta(self, count)
        if self._f_values is not None:
            result._f_values = remap_values[double](&self._f_values[0], count, mapping)
        if self._t_values is not None:
            result._t_values = remap_values[schar](&self._t_values[0], count, mapping)
        if self._py_values is not None:
            result._py_values = self._py_values.remap(count, mapping)

        return result

    def rename(self, newName):
        return self.c_rename(newName)

    cdef Column c_rename(self, str newName):
        cdef Column result = new_column_with_meta(self, self.length)
        result._t_values = self._t_values
        result._f_values = self._f_values
        result._py_values = self._py_values

        result._name = newName

        return result

    def shift(self, n):
        """
        Create a new column whose values are shifted.
        """
        return self.c_shift(n)

    cdef Column c_shift(self, int n):
        cdef Column result = new_column_with_meta(self, self.length)
        result._py_values = self.get_py_values().shift(n)

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
        cdef double[::1] values = get_f_values(self)
        cdef unsigned count = len(values)

        cdef Column result = new_column_with_meta(self, self.length)
        result._name = f"-{self.get_name()}"
        result._f_values = neg(count, &values[0])

        return result

    # ------------------------------------------------------------------
    # Bitwise and
    # ------------------------------------------------------------------
    def __and__(self, other):
        if isinstance(other, Column):
            return and_column_column(self, other)
        else:
            return NotImplemented

    # ------------------------------------------------------------------
    # Bitwise or
    # ------------------------------------------------------------------
    def __or__(self, other):
        if isinstance(other, Column):
            return or_column_column(self, other)
        else:
            return NotImplemented


    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------
    def remap(self, mapping):
        cdef array.array arr = array.array("i", mapping)
        # Above: use a *signed* int array to accomodate for the -1u
        # magic value ("MISSING" constant).

        return self.c_remap(len(mapping), arr.data.as_uints)

