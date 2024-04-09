from cpython cimport array
from cpython.object cimport Py_EQ, Py_NE
import array

from fin.utils.log import console

from fin.seq import coltypes
from fin.mathx cimport ualloc
from fin.seq.column cimport Column
from fin.seq.presentation import Presentation

# ======================================================================
# Globals
# ======================================================================
cdef array.array    int_array       = array.array("i", [])
cdef array.array    unsigned_array  = array.array("I", [])
cdef array.array    double_array    = array.array("d", [])

cdef str SERIE_DEFAULT_NAME = ""

cdef IGNORE = object()

# ======================================================================
# Low-level helpers
# ======================================================================
cdef parse_types(object types):
    if not isinstance(types, str):
        return types

    cdef str fstring = <str>types
    types = []

    for fchar in fstring:
        if fchar=='-': # IGNORE
            type = IGNORE
        elif fchar=='n': # NUMERIC
#            f = float
            type = coltypes.Float()
        elif fchar=='d': # ISO DATE
#            f = datetime.parseisodate
            type = coltypes.Date(from_string=datetime.parseisodate)
        elif fchar=='s': # SECONDS SINCE UNIX EPOCH
#            f = datetime.parsetimestamp
            type = coltypes.DateTime(from_string=datetime.parsetimestamp)
        elif fchar=='m': # MILLISECONDS SINCE UNIX EPOCH
#            f = datetime.parsetimestamp_ms
            type = coltypes.DateTime(from_string=datetime.parsetimestamp_ms)
        elif fchar=='i': # INTEGER
#            f = int
            type = coltypes.Integer()
        else:
            raise ValueError(f"Invalid column type specifier {fchar!r} found in {format!r}")

        types.append(type)

    return types

# ----------------------------------------------------------------------
# Factory functions
# ----------------------------------------------------------------------
cdef Serie serie_bind(Column index, tuple columns, str name):
    cdef Serie self = Serie.__new__(Serie)
    self._index = index
    self._columns = (index, *columns)
    self.rowcount = len(index)
    self.name = name if name is not None else SERIE_DEFAULT_NAME

    return self

cdef Serie serie_from_data(data, headings, types, dict kwargs):
    """
    Create a serie from raw Python data (sequences).

    The first data column is assumed to be the index.
    """
    name = kwargs.get("name", SERIE_DEFAULT_NAME)
    types = parse_types(types)

    # `data` can be an iterator: compute the columns first so we can later call `len()`
    columns = [
        Column.from_sequence(column, name=heading, type=type) for heading, type, column in zip(headings, types, data) if type is not IGNORE
            ]

    if not len(columns):
        rowcount = 0
    else:
        # Check is all columns have the same length
        it = iter(columns)
        rowcount = len(next(it))
        for col in it:
            if len(col) != rowcount:
                raise ValueError(f"All columns must have the same length.")

    return Serie.create(*columns, name=name)

cdef Serie serie_from_rows(headings, types, rows, dict kwargs):
    return serie_from_data(zip(*rows), headings, types, kwargs)

import csv
from fin import datetime
cdef Serie serie_from_csv(iterator, str format, fieldnames, str delimiter, dict kwargs):
    """
    Create a new serie by iterating over CSV data rows.
    """
    rows = []
    reader = csv.reader(iterator, delimiter=delimiter)
    if fieldnames is not None:
        heading = [str(fieldname) for fieldname in fieldnames]
    else:
        # default to first line
        heading = [fieldname.strip() for fieldname in next(reader)]
    rows = list(reader)
    cols = []
    names = []

    for name, col in zip(heading, zip(*rows)):
        names.append(name)
        cols.append(col)

    result = serie_from_data(cols, names, format, kwargs)
#    if select:
#        result = result.select(*select)

    return result


# ----------------------------------------------------------------------
# Projections
# ----------------------------------------------------------------------
cdef Serie serie_select(Serie self, tuple exprs, str name):
    """
    Build a new serie with by evaluating column expressions in the context of the receiver.

    The newly created series has the same number of rows than the receiver and
    they share the same index.
    """

    cdef tuple columns = serie_evaluate_items(self, exprs);

    return serie_bind(self._index, columns, name)

cdef Serie serie_lstrip(Serie self, tuple exprs):
    """
    Return a a new table with rows at the start containing None removed.

    If exprs is empty, the column selection defaults to all columns *except* the
    index if present in the data columns.
    """
    cdef tuple columns

    if len(exprs) == 0:
        columns = tuple([column for idx, column in enumerate(self._columns) if idx != 0])
    else:
        columns = serie_evaluate_items(self, exprs)

    none_row = (None,)*len(columns)
    try:
        for i, row in enumerate(zip(*columns)):
            if row != none_row:
                break
    except TypeError:
        pass

    end = self.rowcount
    return serie_bind(
            self._columns[0][i:end],
            tuple(column[i:end] for idx, column in enumerate(self._columns) if idx != 0),
            self.name
            )

cdef int columns_get_strips(tuple columns, unsigned* buffer) except -1:
    """ Fill a buffer with the index of the next strip of data.

        A strip is a sequence of identical rows. The index column is *not*
        considered when comparing strips since by definition all the index
        values are unique.

        The buffer is assumed to be large enough to hold all the strip limit indices.
        At worst, there is `(rowcount+1)` indices.
    """
    rows = zip(*[col.py_values for col in columns])

    cdef unsigned idx = 0
    cdef tuple prev = None
    cdef tuple row

    for row in rows:
        if prev is None:
            prev = row
        elif row != prev:
            prev = row
            buffer[0] = idx
            buffer += 1

        idx += 1

    buffer[0] = idx

cdef Serie serie_group_by(Serie self, expr, tuple aggregate_expr):
    # Build the group column(s)
    cdef tuple group_cols = serie_evaluate_item(self, expr)

    # Build the projection for aggregate functions parameters
    cdef list aggregate_fcts = []
    cdef list aggregate_sub_series = []
    for aggregate_fct, *aggregate_params in aggregate_expr:
        aggregate_fcts.append(aggregate_fct)
        aggregate_sub_series.append(serie_evaluate_items(self, tuple(aggregate_params)))

    # Keep track of headings and types
    headings = [ ]
    types = [ ]
    cdef Column column
    for aggregate_sub_serie in aggregate_sub_series:
        for column in aggregate_sub_serie:
            headings.append(column._name)
            types.append(column._type)

    # Iterate over rows to group identical values:
    cdef array.array arr = ualloc(self.rowcount+1)
    cdef unsigned *ptr = arr.data.as_uints
    columns_get_strips(group_cols, ptr)

    cdef list rows = []
    cdef list row
    cdef unsigned start = 0
    while start < self.rowcount:
        end = ptr[0]

        row = [ ]
        for aggregate_fct, aggregate_sub_serie in zip(aggregate_fcts, aggregate_sub_series):
            row += aggregate_fct(*[column.py_values[start:end] for column in aggregate_sub_serie])
        rows.append(row)

        start = end
        ptr += 1

    return serie_from_rows(headings, types, rows, {})

cdef serie_sort_by(Serie self, tuple exprs):
    cdef tuple indices = serie_evaluate_items(self, exprs)
    if len(indices) != 1: # Only 1-column index are supported for now
        raise ValueError(f"The index can only have one column")
    cdef Column new_index = indices[0]

    sort_order = sorted(range(self.rowcount), key=new_index.__getitem__)

    return serie_bind(
            new_index.remap(sort_order),
            tuple(column.remap(sort_order) for column in self._columns),
            self.name
            )

# ----------------------------------------------------------------------
# Accessors
# ----------------------------------------------------------------------
cdef inline Column serie_get_column_by_index(Serie self, int idx):
    cdef int col_count
    if idx < 0:
        col_count = len(self._columns)
        idx += col_count
        if idx < 0:
            raise IndexError(f"Column index {idx} out of range")

    return self._columns[idx]

cdef inline Column serie_get_column_by_name(Serie self, str name):
    cdef Column column
    for column in self._columns:
        if column.name == name:
            return column

    raise KeyError(name)

cdef inline serie_row_iterator(Serie self):
    cdef list cols = [col.py_values for col in self._columns]
    return zip(*cols)

cdef inline tuple wrap_in_tuple(tuple_or_column):
    if type(tuple_or_column) is tuple:
        return tuple_or_column

    return ( tuple_or_column, )

cdef tuple serie_evaluate_item(Serie self, expr):
    """
    Evaluate a column expression in the context of the receiver.

    The return type is either a Column object or a tuple of Column.

    The rules:
    Column -> noop
    str -> context[name]
    tuple -> tuple[0](*map(tuple[1:], serie_evaluate))
    otherwise -> recursive evaluation (assume sequence)
    """
    # print(f"serie_evaluate_item {expr!r}")
    cdef type t = type(expr)

    if t is Column:
        return ( expr, )
    if t is Serie:
        join = c_left_outer_join(self, expr, False)
        if join.index != self._index:
            raise ValueError(f"Cannot insert serie: indices differ.")
        return join.right
    if t is str:
        return ( serie_get_column_by_name(self, expr), )
    if t is int or t is float:
        raise TypeError(f"Did you mean fc.constant({t!r})?")
    if callable(expr):
        # Only nullary callable are allowed here
        return wrap_in_tuple(expr(self))

    return serie_evaluate_expr(self, *expr) # implicit test for iter(expr)

def serie_evaluate_expr(Serie self, head, *tail):
    # print(f"serie_evaluate_expr {head!r}, {tail!r}")

    while True:
        if callable(head):
            if tail:
                tail = serie_evaluate_expr(self, tail)
                result = head(self, *tail)
            else:
                result = head(self)

            t = type(result)
            if t is Column:
                head = result
                tail = ()
            elif t is tuple:
                head = result[0]
                tail = result[1:]
            elif t is Serie:
                head, *tail = (<Serie>result)._columns[1:]
            else:
                raise TypeError(f"Column functions should return a Column or a tuple of Columns ({type(result)}) found)")
        else:
            # The first non-callable break the cycle of recursive evaluations
            return serie_evaluate_items(self, (head, *tail))

cdef inline tuple serie_evaluate_items(Serie self, tuple items):
    # print(f"serie_evaluate_items {items!r}")

    cdef list result = [ ]
    for item in items:
        result += serie_evaluate_item(self, item)

    return tuple(result)

# ======================================================================
# Serie
# ======================================================================
cdef class Serie:
    """
    A Serie is a list of columns, all of same length.

    The index is assumed to be sorted in ascending order (strictly?).
    """
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("You must use a factory method to create a Serie instance")

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------
    @staticmethod
    def create(first_expr, *exprs, name=None):
        """ Create a new Serie instance.

            The first argument is an expression that evaluates to the serie index.
            The index is also usedd as the first data column.
        """
        cdef Serie self = Serie.__new__(Serie)
        self.rowcount = 0
        cdef tuple indices = serie_evaluate_item(self, first_expr)
        if len(indices) != 1:
            raise ValueError(f"The index can only have one column")
        cdef Column index = indices[0]

        # Initialize the core properties and start "recursive" evaluation of the
        # remaining column expressions.
        self._index = index
        self.rowcount = len(index)
        self.name = str(name) if name is not None else SERIE_DEFAULT_NAME

        self._columns = ( index, )
        while exprs:
            head, *exprs = exprs
            self._columns += serie_evaluate_item(self, head)

        return self

    @staticmethod
    def from_data(columns, headings, types=None, **kwargs):
        if types is None:
            types = (None,)*len(headings)

        return serie_from_data(columns, headings, types, kwargs)

    @staticmethod
    def from_rows(headings, type, rows, **kwargs):
        return serie_from_rows(headings, type, rows, kwargs)
    # XXX Above: fix from_data() and from_rows() to have the parameters in the same order

    @staticmethod
    def from_csv(iterator, format='', *, fieldnames=None, delimiter=",", **kwargs):
        return serie_from_csv(iterator, format, fieldnames, delimiter, kwargs)

    @staticmethod
    def bind(index, *columns, name=None):
        return serie_bind(index, columns, name)

    # ------------------------------------------------------------------
    # Predicates
    # ------------------------------------------------------------------
    def select(self, *columns, name=None):
        return serie_select(self, columns, name)

    def lstrip(self, *columns):
        return serie_lstrip(self, columns)

    def group_by(self, expr, *aggregate_fct):
        return serie_group_by(self, expr, aggregate_fct)

    def sort_by(self, expr, *exprs):
        return serie_sort_by(self, (expr, *exprs))

    # ------------------------------------------------------------------
    # Column expression evaluation
    # ------------------------------------------------------------------
    def evaluate(self, *expr):
        """
        Evaluate an expression as a column in the context of the receiver.
        """
        return serie_evaluate_expr(self, *expr)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def index(self):
        return self._index

    @property
    def columns(self):
        return self._columns

    @property
    def rows(self):
        """
        Return an *iterator* over the serie rows.
        """
        return serie_row_iterator(self)

    @property
    def headings(self):
        """
        Return a sequence containing the column's names.
        """
        return [col.name for col in self._columns]

    @property
    def rowcount(self):
        return self.rowcount

    @property
    def name(self):
        return self.name

    def __repr__(self):
        """
        Convert to string.

        Return a programmer-useful representation of the serie.

        EXPERIMENTAL: The output format is subject to changes.
        """
        return f"{self.__class__.__qualname__}(rowcount={self.rowcount!r}, name={self.name!r}, headings={self.headings!r})"

    def __str__(self):
        """
        Convert to string.

        Rely on the serie formatting utility.
        """
        pres = Presentation(heading=True)
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

        return serie_bind(self._index, tuple(columns), self.name)

    cdef Serie c_get_item_by_index(self, int idx):
        return serie_bind(self._index, (serie_get_column_by_index(self, idx),), self.name)

    cdef Serie c_get_item_by_name(self, str name):
        return serie_bind(self._index, (serie_get_column_by_name(self, name),), self.name)

    def clear(self):
        """
        Return a serie containing only the index.

        EXPERIMENTAL. Change name?
        """
        return serie_bind(self.index, (), "Empty")

    def get_strips(self):
        """ For testing purposes only!
        """
        cdef array.array arr = ualloc(self.rowcount+1)
        columns_get_strips(self._columns[1:], arr.data.as_uints)

        return arr

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------
    def __richcmp__(self, other, int op):
        if op == Py_NE:
            return not(self == other)
        if op != Py_EQ or type(other) is not Serie:
            return NotImplemented # XXX Shouldn't we raise an exception here?

        # Identity
        if self is other:
            return True

        # Equality
        serA = <Serie>self
        serB = <Serie>other
        if serA.rowcount != serB.rowcount:
            return False
        if serA.name != serB.name:
            return False

        return serA._columns == serB._columns


    # ------------------------------------------------------------------
    # Arithmetic operators
    # ------------------------------------------------------------------
#    def __add__(self, other):
#        """
#        Addition.
#        """
#        if isinstance(other, (int, float)):
#            return (<Serie>self).c_add_scalar(other)
#        elif isinstance(other, Serie):
#            return (<Serie>self).c_add_serie(other)
#        else:
#            return NotImplemented
#
#    cdef Serie c_add_scalar(self, double other):
#        cdef Column column
#        new = [column.c_add_scalar(other) for column in self._columns]
#        return serie_bind(self._index, tuple(new), "Add")
#
#    cdef Serie c_add_serie(self, Serie other):
#        cdef Join join = c_inner_join(self, other, rename=False)
#        cdef Column a, b
#        cdef list new = [ a + b for a in join.left for b in join.right ]
#
#        return serie_bind(join.index, tuple(new), "Add")

    # ------------------------------------------------------------------
    # Joins operators
    # ------------------------------------------------------------------
    def __and__(self, other):
        """
        Inner join operator.
        """
        cdef Join join
        cdef Serie that = self

        if isinstance(other, Serie):
            join = c_inner_join(that, other, True)
            return serie_bind(join.index, (*join.left, *join.right), f"{self.name} & {other.name}")
        elif isinstance(other, (int, float)):
            return serie_bind(
                    that._index,
                    (*that._columns, Column.from_constant(len(that.index), other)),
                    f"{self.name} & {other}"
            )
        else:
            return NotImplemented

    def __or__(self, other):
        """
        Full outer join operator.
        """
        cdef Join join
        cdef Serie that = self

        if isinstance(other, Serie):
            join = c_full_outer_join(that, other, True)
            return serie_bind(join.index, (*join.left, *join.right), f"{self.name} | {other.name}")
        elif isinstance(other, (int, float)):
            # XXX Is this correct for `serie FULL OUTER JOIN constant`?
            return serie_bind(
                    that._index,
                    (*that._columns, Column.from_constant(len(that.index), other)),
                    f"{self.name} | {other}"
            )
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

def inner_join(serA, serB, *, rename=True):
    return c_inner_join(serA, serB, rename).as_tuple()

join=inner_join # Compatibility with previous implementations. DEPRECATED.

def full_outer_join(serA, serB, *, rename=True):
    return c_full_outer_join(serA, serB, rename).as_tuple()

def left_outer_join(serA, serB, *, rename=True):
    return c_left_outer_join(serA, serB, rename).as_tuple()

ctypedef unsigned (*join_build_mapping_t)(
        unsigned lenA, tuple indexA,
        unsigned lenB, tuple indexB,
        unsigned *mappingA,
        unsigned *mappingB)

cdef unsigned inner_join_build_mapping(
        unsigned lenA, tuple indexA,
        unsigned lenB, tuple indexB,
        unsigned *mappingA,
        unsigned *mappingB):
    """
    Build the translation table for the inner join of indexA and indexB.

    The buffer mappingA and mappingB are *assumed* to be large enough
    to store the required amount of data.

    Return the actual number of row in the resulting join.
    """
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
            mappingA[n] = posA
            mappingB[n] = posB
            n += 1
            posA += 1
            posB += 1
            if posA == lenA or posB == lenB:
                break

    return n

cdef unsigned full_outer_join_build_mapping(
        unsigned lenA, tuple indexA,
        unsigned lenB, tuple indexB,
        unsigned *mappingA,
        unsigned *mappingB):
    """
    Build the translation table for the full outer join of indexA and indexB.

    The buffer mappingA and mappingB are *assumed* to be large enough
    to store the required amount of data.

    Return the actual number of row in the resulting join.
    """
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
            mappingA[n] = posA
            mappingB[n] = -1
            n += 1
            posA += 1
            if posA == lenA:
                break
        elif indexB[posB] < indexA[posA]:
            mappingA[n] = -1
            mappingB[n] = posB
            n += 1
            posB += 1
            if posB == lenB:
                break
        else:
            mappingA[n] = posA
            mappingB[n] = posB
            n += 1
            posA += 1
            posB += 1
            if posA == lenA or posB == lenB:
                break

    while posA < lenA:
        if indexA[posA] is not None:
            mappingA[n] = posA
            mappingB[n] = -1
            n += 1
        posA += 1

    while posB < lenB:
        if indexB[posB] is not None:
            mappingA[n] = -1
            mappingB[n] = posB
            n += 1
        posB += 1


    return n

cdef unsigned left_outer_join_build_mapping(
        unsigned lenA, tuple indexA,
        unsigned lenB, tuple indexB,
        unsigned *mappingA,
        unsigned *mappingB):
    """
    Build the translation table for the left outer join of indexA and indexB.

    The buffer mappingA and mappingB are *assumed* to be large enough
    to store the required amount of data.

    Return the actual number of row in the resulting join.
    """
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
            mappingA[n] = posA
            mappingB[n] = -1
            n += 1
            posA += 1
            if posA == lenA:
                break
        elif indexB[posB] < indexA[posA]:
            posB += 1
            if posB == lenB:
                break
        else:
            mappingA[n] = posA
            mappingB[n] = posB
            n += 1
            posA += 1
            posB += 1
            if posA == lenA or posB == lenB:
                break

    while posA < lenA:
        if indexA[posA] is not None:
            mappingA[n] = posA
            mappingB[n] = -1
            n += 1
        posA += 1

    # No need to consume the remaining items in indexB

    return n

cdef list join_engine_remap_columns(list columns, unsigned n, unsigned* mapping):
    cdef Column column

    return [ column.c_remap(n, mapping) for column in columns ]

cdef Join c_inner_join(Serie serA, Serie serB, bint rename):
    return join_engine(inner_join_build_mapping, serA, serB, rename)

cdef Join c_full_outer_join(Serie serA, Serie serB, bint rename):
    return join_engine(full_outer_join_build_mapping, serA, serB, rename)

cdef Join c_left_outer_join(Serie serA, Serie serB, bint rename):
    return join_engine(left_outer_join_build_mapping, serA, serB, rename)

cdef Join join_engine(
        join_build_mapping_t join_build_mapping,
        Serie serA, Serie serB,
        bint rename):
    """
    Create a join from two series.
    """
    cdef tuple indexA = serA._index.get_py_values()
    cdef tuple indexB = serB._index.get_py_values()

    cdef unsigned lenA = len(indexA)
    cdef unsigned lenB = len(indexB)

    # In the worst case, a join can have lenA+lenB rows (case of a full outer join with
    # completely disjoined indices).
    cdef unsigned lenMapping = lenA+lenB
    cdef array.array mappingA = array.clone(unsigned_array, lenMapping, zero=False)
    cdef array.array mappingB = array.clone(unsigned_array, lenMapping, zero=False)

    cdef unsigned n = join_build_mapping(
            lenA, indexA,
            lenB, indexB,
            mappingA.data.as_uints, mappingB.data.as_uints,
        )

    # shrink array to their correct length:
    array.resize(mappingA, n)
    array.resize(mappingB, n)

    # Build the index
    cdef unsigned i
    cdef list joinIndex = [
            # A bit of hack here: -1u ("MISSING") is the greatest unsigned int so
            # .... < lenA will catch both the out-of-bound and the missing cases
            indexA[mappingA[i]] if mappingA[i] < lenA else indexB[mappingB[i]]
            for i in range(n)
        ]
    cdef Column column

    # Rename the columns if:
    # 1. `rename` is true
    # 2. the serie has a non-empty name
    cdef str prefix
    cdef list colA = list(serA._columns[1:])
    cdef list colB = list(serB._columns[1:])
    if rename:
        prefix = serA.name
        if len(prefix) > 0:
            prefix += ":"
            colA = [
                    column.c_rename(prefix + column.name) for column in colA
                    ]

        prefix = serB.name
        if len(prefix) > 0:
            prefix += ":"
            colB = [
                    column.c_rename(prefix + column.name) for column in colB
                    ]
    # Build the left and right series
    cdef list leftColumns = join_engine_remap_columns(colA, n, mappingA.data.as_uints)
    cdef list rightColumns = join_engine_remap_columns(colB, n, mappingB.data.as_uints)

    return Join.create(
            Column.from_sequence(
                joinIndex,
                name=serA._index.name,
                type=serA._index.type,
                convert=False
            ),
            tuple(leftColumns),
            tuple(rightColumns)
    )
