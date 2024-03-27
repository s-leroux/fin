import sys

from cpython cimport array
import array

from fin.utils.log import console
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
cdef Serie serie_bind(Column index, tuple columns, str title):
    cdef Serie self = Serie.__new__(Serie)
    self._index = index
    self._columns = columns
    self.rowcount = len(index)
    self.title = title if title is not None else "Untitled"

    return self

cdef Serie serie_from_data(data, headings, dict kwargs):
    """
    Create a serie from raw Python data (sequences).
    """
    title = kwargs.get("title", "Untitled")
    if not len(data):
        rowcount = 0
    else:
        # Check is all columns have the same length
        it = iter(data)
        rowcount = len(next(it))
        for col in it:
            if len(col) != rowcount:
                raise ValueError(f"All columns must have the same length.")

    columns = [
        Column.from_sequence(column, name=heading) for heading, column in zip(headings, data)
            ]

    return Serie.create(*columns, title=title)

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
    for name, fchar, col in zip(heading, format, zip(*rows)):
        if fchar=='-': # IGNORE
            continue
        elif fchar=='n': # NUMERIC
            f = float
        elif fchar=='d': # ISO DATE
            f = datetime.parseisodate
        elif fchar=='s': # SECONDS SINCE UNIX EPOCH
            f = datetime.parsetimestamp
        elif fchar=='m': # MILLISECONDS SINCE UNIX EPOCH
            f = datetime.parsetimestamp_ms
        elif fchar=='i': # INTEGER
            f = int

        col = list(col)
        for index, value in enumerate(col):
            try:
                col[index] = f(value)
            except:
                e = sys.exc_info()[1] # This will also catch an exception that doesn't inherit from Exception
                console.warn(f"Can't convert {col[index]} using {f}")
                console.info(str(e))
                col[index] = None

        names.append(name)
        cols.append(col)

    result = serie_from_data(cols, names, kwargs)
#    if select:
#        result = result.select(*select)

    return result


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
        join = c_left_join(self, expr)
        if join.index != self._index:
            raise ValueError(f"Cannot insert serie: indices differ.")
        return join.right
    if t is str:
        return ( serie_get_column_by_name(self, expr), )
    if t is int or t is float:
        raise SystemError(f"Did you mean fc.constant({t!r})?")
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
                head = t[0]
                tail = t[1:]
            elif t is Serie:
                head, *tail = (<Serie>result)._columns
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
    A Serie is an index and a list of columns, all of same length.

    The index is assumed to be sorted in ascending order (strictly?).
    """
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("You must use a factory method to create a Serie instance")

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------
    @staticmethod
    def create(index, *columns, title=None):
        cdef Serie self = Serie.__new__(Serie)
        cdef tuple index_evaluation = serie_evaluate_item(self, index)

        # Validity checks for the index column:
        if len(index_evaluation) != 1:
            raise ValueError(f"Index should evaluate to a single column (here {len(index_evaluation)})")
        if not len(index_evaluation[0]):
            raise TypeError(f"Zero-length index are not supported")

        # Ok. Initialize the core properties and start "recursive" evaluation of the
        # remaining column expressions.
        self._index = index_evaluation[0]
        self.rowcount = len(self._index)
        self.title = str(title) if title is not None else "Untitled"

        self._columns = ()
        while columns:
            head, *columns = columns
            self._columns += serie_evaluate_item(self, head)

        return self
    
    @staticmethod
    def from_data(columns, headings, **kwargs):
        return serie_from_data(columns, headings, kwargs)

    @staticmethod
    def from_csv(iterator, format='', *, fieldnames=None, delimiter=",", **kwargs):
        return serie_from_csv(iterator, format, fieldnames, delimiter, kwargs)

    @staticmethod
    def bind(index, *columns, title=None):
        return serie_bind(index, columns, title)

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
        cols = [self._index.py_values] + [col.py_values for col in self._columns]
        return zip(*cols)

    @property
    def headings(self):
        """
        Return a sequence containing the column's names.
        """
        return [self._index.name] + [col.name for col in self._columns]

    @property
    def rowcount(self):
        return self.rowcount

    @property
    def title(self):
        return self.title

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

        return serie_bind(self._index, tuple(columns), self.title)

    cdef Serie c_get_item_by_index(self, int idx):
        return serie_bind(self._index, (serie_get_column_by_index(self, idx),), self.title)

    cdef Serie c_get_item_by_name(self, str name):
        return serie_bind(self._index, (serie_get_column_by_name(self, name),), self.title)

    def clear(self):
        """
        Return a serie containing only the index.

        EXPERIMENTAL. Change name?
        """
        return serie_bind(self.index, (), "Empty")

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
        return serie_bind(self._index, tuple(new), "Add")

    cdef Serie c_add_serie(self, Serie other):
        cdef Join join = c_join(self, other)
        cdef Column a, b
        cdef list new = [ a + b for a in join.left for b in join.right ]

        return serie_bind(join.index, tuple(new), "Add")

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
            return serie_bind(join.index, (join.left+join.right), f"{self.title} & {other.title}")
        elif isinstance(other, (int, float)):
            return serie_bind(
                    that._index, 
                    (*that._columns, Column.from_constant(len(that.index), other)),
                    f"{self.title} & {other}"
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

def left_join(serA, serB):
    return c_left_join(serA, serB).as_tuple()

cdef Join c_left_join(Serie serA, Serie serB):
    """
    Create a left join from two series.
    """
    cdef Column indexA = serA._index
    cdef Column indexB = serB._index

    if indexA == indexB:
        return Join.create(
                indexA,
                serA.columns,
                serB.columns
        )

    raise NotImplementedError(f"Non-trivial left join are not implemented yet.")
