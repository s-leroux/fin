import sys
import operator
from copy import copy

from fin.seq import formatter
from fin.seq.column import Column, as_column
from fin.utils.log import console

# ======================================================================
# Exceptions
# ======================================================================
class InvalidError(Exception):
    pass

class RowCountMismatch(InvalidError):
    def __init__(self, detail, expected, actual):
        msg = """in {detail}: {expected} rows expected, {actual} given"""
        super().__init__(msg.format(detail=detail, expected=expected, actual=actual))

class DuplicateName(ValueError):
    pass

def raise_table_cast_error(something):
    console.debug(something)
    raise TypeError(f"Can't convert {type(something)} to Table")

# ======================================================================
# Table class
# ======================================================================
class Table:
    """ A Table is a list of columns, all of the same length
        (i.e.: tables are rectangular)
    """

    def __init__(self, rows, *, name="", columns={}):
        self._rows = rows
        self._name = str(name)
        self._meta = [ ]

        for k, v in columns.items():
            self.add_column(k, v)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def columns(self):
        return len(self._meta)

    def rows(self):
        return self._rows

    def name(self):
        return self._name

    def data(self, columns=None):
        """
        Return the raw data for the given columns (or all if not specificed).
        """
        if columns != None:
            return [self[name_or_index].py_values for name_or_index in columns]
        else:
            return [ it.py_values for it in self._meta ]

    def row_iterator(self, columns=None):
        """
        Return an iterator on the table rows.

        The ''column'' parameter lists the columns to select. If
        you specify ''None'' all the columns are selected.
        """
        return zip(*self.data(columns))

    def names(self):
        """
        Return the column names

        TODO: Rename this method
        """
        try:
            return [meta.name for meta in self._meta]
        except:
            for meta in self._meta:
                print(type(meta))
                print(meta.name)
            raise

    # ------------------------------------------------------------------
    # Transformations
    # ------------------------------------------------------------------
    def filter(self, fct, *cols):
        """
        Return a new table containing only rows for whom ''fct(*cols)'' evaluates to
        True.

        The returned table contains all the columns of the original table,
        not only those used for evaluation of ''fct''.
        """
        cols = self.data(cols)
        data = self.data()
        rows = [ row for row, flt in zip(zip(*data),zip(*cols)) if fct(*flt) ]

        t = Table(len(rows), name=self.name())
        for meta, column in zip(self._meta, zip(*rows)):
            meta = Column.from_sequence(meta.name, column)
            t._meta.append(meta)

        return t

    def select(self, *exprs):
        """
        Return a new table build from the evaluation of a table expression
        """
        columns = self.reval(exprs)

        t = Table(self._rows, name=self.name())
        for column in columns:
            t.add_column(column)

        return t

    def copy(self, *, name=None):
        """
        Return a copy of the table.
        """
        t = Table(self._rows, name=self.name() if name is None else name)
        t.add_columns(*self)

        return t

    def lstrip(self, columns=None):
        """
        Return a a new table with rows at the start containing None removed.

        If columns is defined is is assumed to be a sequence of column names.
        In that case, only those columns are checked.
        """
        columns = self.data(columns)
        none_row = (None,)*len(columns)
        try:
            for i, row in enumerate(zip(*columns)):
                if row != none_row:
                    break
        except TypeError:
            pass

        end = self._rows
        t = Table(end-i, name=self.name())
        for col in self._meta:
            t.add_column(col[i:end])

        return t

    def sort(self, columns=None):
        """
        Return a new table with the same data but with rows sorted according to `columns`.
        """
        if columns is None:
            columns = self.names()
        it = [*self.row_iterator()]
        for column in columns:
            it.sort(key=operator.itemgetter(self._get_column_index(column)))

        return table_from_data([*zip(*it)], self.names())

    def group(self, expr, aggregate_functions = {}):
        """
        Return a new table with consecutive rows producing the same value for expr()
        grouped together.
        """
        def default_mapping(values):
            return values[0]

        def aggregate(dest, src):
            row = [aggregate_functions.get(name, default_mapping)(column) for name, *column in zip(names, *src)]
            dest.append(row)

        names = self.names()
        rows = self.row_iterator()
        keys, = self.reval(expr)
        prev = object()
        group = []
        result = []
        for key, row in zip(keys, rows):
            if key != prev:
                prev = key
                if group:
                    aggregate(result, group)
                group = []
            group.append(row)
        if group:
            aggregate(result, group)

        return table_from_data([*zip(*result)], self.names())

    # ------------------------------------------------------------------
    # Mutative methods
    # ------------------------------------------------------------------
    def rename(self, name_or_index, newname):
        """ Change the name of a column.

            The Original column may be specified using its index or name.
            If the name is ambiguous, the behavior is unspecified.
        """
        index = self._get_column_index(name_or_index)
        self._meta[index] = self._meta[index].named(newname)

    def add_column(self, name_or_expr, expr=None):
        """
        Add a column to the table.

        When called with only one argument, it is assumed to have a `name` property.
        When called with two arguments, the first one is the name of the newly
        added column, and expr is a valid table expression whose evaluation
        becomes the new table value.
        """
        if expr is None:
            columns = self.reval(name_or_expr)
            name = None
        else:
            columns = self.reval(expr)
            name = name_or_expr

        new_cols = []
        n = len(columns)
        for column in columns:
            # Rename the column if needed
            column = as_column(column)

            if name:
                if n == 1:
                    # Override column's name
                    column = column.named(name)
                else:
                    # name act as a namespace
                    column = column.named(f"{name}:{column.name}")
            elif not column.name:
                # No default. Infer a name.
                column = column.named(f"C{len(self._meta)}")

            # Sanity checks
            if name in self.names():
                raise DuplicateName(name)
            if len(column) != self._rows:
                raise RowCountMismatch(f"column {name}", self._rows, len(column))

            # Finally, append the column
            self._meta.append(column)
            new_cols.append(column)

        return new_cols

    def add_columns(self, *col_specs):
        for col_spec in col_specs:
            if isinstance(col_spec, Column):
                self.add_column(col_spec)
            else:
                # Assume col_spec is a (name, expr) pair
                self.add_column(*col_spec)

    def del_column(self, index_or_name):
        """ Remove a column from the table, given it's index or name
        """
        index = self._get_column_index(index_or_name)
        del self._meta[index]

    def del_columns(self, *col_specs):
        """ Remove columns from the table.
        """
        for col_spec in col_specs:
            self.del_column(col_spec)

    def set_column_meta(self, index_or_name, name=None):
        """ Change the metadata associated with a column.
        """
        index = self._get_column_index(index_or_name)
        if index == 0:
            raise ValueError("Cannot alter column 0")

        meta = self._meta[index]

        if name is not None:
            meta.name=name

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def reval(self, head, *tail):
        """
        Recursive evaluation of a table expression.
        """
        while True:
            # print(f"reval {head!r} {tail!r}")

            if callable(head):
                # It's an f-expression
                if tail:
                    head = head(self._rows, *self.reval(*tail))
                    tail = ()
                else:
                    head = head(self._rows)
            else:
                # It's a list
                result = self.reval_item(head)
                if tail:
                    result += self.reval(tail)
                return result

    def reval_item(self, item):
        if type(item) == str:
            idx = self._get_column_index(item)
            return [ self._meta[idx] ]
        if isinstance(item, Column):
            return [ item ]
        if isinstance(item, dict): # collections.abc.Mapping ?
            col, =  self.reval(item["expr"])
            return [ col.named(item["name"]) ]

        try:
            it = iter(item)
        except TypeError as e:
            pass
        else:
            return self.reval(*it)

        return [ Column.from_sequence(None, [item]*self._rows) ]

    def __getitem__(self,c):
        c = self._get_column_index(c)

        return self._meta[c]

    def __iter__(self):
        return iter(self._meta)

    def _get_column_index(self, index_or_name):
        if type(index_or_name) is str:
            try:
                index_or_name = self.names().index(index_or_name)
            except ValueError:
                console.info(f"Known columns are {self.names()}")
                raise

        return int(index_or_name)

    def __str__(self):
        return formatter.Tabular().format(self)

# ======================================================================
# Helpers for table expression evaluation
# ======================================================================
add = lambda rowcount, *cols : [sum(row) for row in zip(*cols)]

# ======================================================================
# Create tables from existing data structures
# ======================================================================
def table_from_data(data, headings, *, name=""):
    if not len(data):
        rowcount = 0
    else:
        # Check is all columns have the same length
        it = iter(data)
        rowcount = len(next(it))
        for col in it:
            if len(col) != rowcount:
                raise InvalidError()

    t = Table(rowcount, name=name)
    for heading, column in zip(headings, data):
        t.add_column(Column.from_sequence(heading, column))

    return t

def table_from_rows(rows, headings, *, name=""):
    return table_from_data([*zip(*rows)], headings, name=name)

def table_from_column(column_or_name, column=None):
    """
    Create a table from a single column.
    """
    if column is None:
        column = as_column(column_or_name)
    else:
        column = as_column(column, column_or_name)

    name = column_or_name

    result = Table(len(column))
    result.add_column(name, column)

    return result

def table_from_dict(d, *, name=""):
    """
    Create a new table from existing data (*not* columns) presented
    as a dictionary of columns.
    """
    data = []
    headings = []

    for name, column in d.items():
        headings.append(name)
        data.append(column)

    return table_from_data(data, headings, name=name)

def as_table(something):
    """
    Convert common data types to tables.
    """
    if isinstance(something, Table):
        return something
    if isinstance(something, dict):
        return table_from_dict(something)

    raise_table_cast_error(something);

# ======================================================================
# Join
# ======================================================================
def join(tableA, tableB, keyA, keyB=None, *, name=None, rename=True):
    """
    Join tableA and tableB using their respective columns keyA and keyB.

    If keyB is unspecified or None, keyB is set to keyA.
    The key columns are assumed to be sorted in ascending order.
    Rows containing the None value in their key column are ignored.
    Discard the rows whose key is None and rows without a matching key in the
    other table.
    If the `rename` keyword parameter is set to `True` (the default) column's name
    in the result table are rename according to the table's name (thus avoiding
    duplicate column names in common use cases).
    """
    tableA = as_table(tableA)
    tableB = as_table(tableB)

    colsA = tableA.names()
    colsB = tableB.names()
    if name is None:
        name = f"{tableA.name()} ∩ {tableB.name()}"

    if keyB is not None and keyB != keyA:
        colsA.remove(keyA)
        colsB.remove(keyB)
        itA = tableA.row_iterator([keyA] + colsA)
        itB = tableB.row_iterator([keyB] + colsB)
    else:
        keyB = keyA
        colsA.remove(keyA)
        colsB.remove(keyA)
        itA = tableA.row_iterator([keyA] + colsA)
        itB = tableB.row_iterator([keyA] + colsB)

    try:
        kA = None
        kB = None
        result = []

        while True:
            while kA is None:
                kA, *rA = next(itA)
            while kB is None:
                kB, *rB = next(itB)
            if kA < kB:
                kA, *rA = next(itA)
            elif kB < kA:
                kB, *rB = next(itB)
            else:
                result.append([kA, kB, *rA, *rB])
                kA, *rA = next(itA)
                kB, *rB = next(itB)
    except StopIteration:
        pass

    # Rename columns in the result table
    if rename:
        nameA = tableA.name()
        nameB = tableB.name()
        if nameA:
            if keyA != keyB:
                keyA = nameA+":"+keyA
            colsA = [nameA+":"+col for col in colsA]
        if nameB:
            if keyA != keyB:
                keyB = nameB+":"+keyB
            colsB = [nameB+":"+col for col in colsB]

    # Remove redundant column if needed
    by_cols = [*zip(*result)]
    cols = [keyA, keyB, *colsA, *colsB]
    if keyA == keyB:
        del by_cols[0]
        del cols[0]

    return table_from_data(by_cols, cols, name=name)

def outer_join(tableA, tableB, keyA, keyB=None, *, name=None, propagate=False, rename=True):
    """
    Join tableA and tableB using their respective columns keyA and keyB.

    If keyB is unspecified or None, keyB is set to keyA.
    The key columns are assumed to be sorted in ascending order.
    Rows containing the None value in their key column are ignored.
    Discard the rows whose key is None.
    Keep the rows without a matching entry in the other table.
    If `propagate` is set to `True`, missing data are replaced by the last known
    values, otherwise, missing data are set to `None`.
    If the `rename` keyword parameter is set to `True` (the default) column's name
    in the result table are rename according to the table's name (thus avoiding
    duplicate column names in common use cases).
    """
    tableA = as_table(tableA)
    tableB = as_table(tableB)

    colsA = tableA.names()
    colsB = tableB.names()
    if name is None:
        name = f"{tableA.name()} ∪ {tableB.name()}"

    if keyB is not None and keyB != keyA:
        merge_keys = False
        colsA.remove(keyA)
        colsB.remove(keyB)
        itA = tableA.row_iterator([keyA] + colsA)
        itB = tableB.row_iterator([keyB] + colsB)
    else:
        merge_keys = True
        colsA.remove(keyA)
        colsB.remove(keyA)
        itA = tableA.row_iterator([keyA] + colsA)
        itB = tableB.row_iterator([keyA] + colsB)

    emptyRowA = [None]*len(colsA)
    emptyRowB = [None]*len(colsB)

    try:
        kA = None
        kB = None
        result = []

        while True:
            while kA is None:
                kA, *rA = next(itA)
            while kB is None:
                kB, *rB = next(itB)
            if kA < kB:
                result.append([kA, None, *rA, *emptyRowB])
                if propagate:
                    emptyRowA=rA
                kA = None
                kA, *rA = next(itA)
            elif kB < kA:
                result.append([None, kB, *emptyRowA, *rB])
                if propagate:
                    emptyRowB=rB
                kB = None
                kB, *rB = next(itB)
            else:
                result.append([kA, kB, *rA, *rB])
                if propagate:
                    emptyRowA=rA
                    emptyRowB=rB
                kA = None
                kB = None
                kA, *rA = next(itA)
                kB, *rB = next(itB)
    except StopIteration:
        pass

    try:
        while True:
            if kA is not None:
                result.append([kA, kB, *rA, *emptyRowB])
            if propagate:
                emptyRowA=rA
            kA, *rA = next(itA)
    except StopIteration:
        pass

    try:
        while True:
            if kB is not None:
                result.append([kA, kB, *emptyRowA, *rB])
            if propagate:
                emptyRowB=rB
            kB, *rB = next(itB)
    except StopIteration:
        pass

    # Rename columns in the result table
    if rename:
        nameA = tableA.name()
        nameB = tableB.name()
        if nameA:
            if not merge_keys:
                keyA = nameA+":"+keyA
            colsA = [nameA+":"+col for col in colsA]
        if nameB:
            if not merge_keys:
                keyB = nameB+":"+keyB
            colsB = [nameB+":"+col for col in colsB]

    # Remove redundant column if needed
    by_cols = [*zip(*result)]
    cols = [keyA, keyB, *colsA, *colsB]
    if merge_keys:
        by_cols[0] = [a or b for a,b in zip(*by_cols[0:2])]
        del by_cols[1]
        del cols[1]
    return table_from_data(by_cols, cols, name=name)

# ======================================================================
# Create tables from CSV
# ======================================================================
import csv
from fin import datetime

def table_from_csv(iterator, format='', *, fieldnames=None, delimiter=',', select=None, **kwargs):
    rows = []
    reader = csv.reader(iterator, delimiter=delimiter)
    if fieldnames is not None:
        heading = [str(fieldname) for fieldname in fieldnames]
    else:
        # default to first line
        heading = next(reader)
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

    result = table_from_data(cols, names, **kwargs)
    if select:
        result = result.select(*select)

    return result

def table_from_csv_file(fname, format='', *, name=None, delimiter=','):
    if name is None:
        name = str(fname)

    with open(fname, newline='') as csvfile:
        return table_from_csv(csvfile, format=format, name=name, delimiter=delimiter)
