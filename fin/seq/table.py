from copy import copy

from fin.seq import driver

class InvalidError(Exception):
    pass

class RowCountMismatch(InvalidError):
    def __init__(self, detail, expected, actual):
        msg = """in {detail}: {expected} rows expected, {actual} given"""
        super().__init__(msg.format(detail=detail, expected=expected, actual=actual))

class DuplicateName(ValueError):
    pass

def C(column):
    if isinstance(column, Table.Column):
        return column

    # otherwise, we assume it's a generator
    return Table.Column(None, column)

# ======================================================================
# Table class
# ======================================================================
class Table:
    """ A Table is a list of columns, all of the same length
        (i.e.: tables are rectangular)
    """
    class Column:
        __slots__ = (
                "value",
                "name",
                )

        def __init__(self, name, value):
            self.name = name
            self.value = list(value)

        def __len__(self):
            return len(self.value)

        def __getitem__(self, index):
            return self.value[index]

        def __eq__(self, other):
            if not isinstance(other, Table.Column):
                return False

            if self.value != other.value:
                return False
            if self.name != other.name:
                return False

            return True

        def __repr__(self):
            return "Column(\"{}\", {})".format(self.name, self.value)

    def __init__(self, rows):
        self._rows = rows
        col0 = Table.Column("#", list(range(rows)))
        self._meta = [ col0 ]

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def columns(self):
        return len(self._meta)

    def rows(self):
        return self._rows

    def data(self, columns=None):
        """
        Return the raw data for the given columns (or all if not specificed).
        """
        if columns != None:
            return [self[name_or_index] for name_or_index in columns]
        else:
            return [ it.value for it in self._meta ]

    def row_iterator(self, columns=None):
        """
        Return an iterator on the table rows.

        The ''column'' parameter lists the columns to select. If
        you specify ''None'' all the columns are selected.
        """
        return zip(*self.data(columns))

    def names(self):
        """ Return the column names
        """
        return [meta.name for meta in self._meta]

    # ------------------------------------------------------------------
    # Transformations
    # ------------------------------------------------------------------
    def filter(self, fct, *cols):
        """
        Return a new table containing only rows for whom ''fct'' evaluates to
        True.

        The returned table contains all the columns of the original table,
        not only those used for evaluation of ''fct''.
        """
        cols = self.data(cols)
        data = self.data()[1:] # ignore the row-number column
        rows = [ row for row, flt in zip(zip(*data),zip(*cols)) if fct(*flt) ]

        t = Table(len(rows))
        for meta, column in zip(self._meta[1:], zip(*rows)):
            meta = copy(meta)
            meta.value = column
            t._meta.append(meta)

        return t

    def select(self, *exprs):
        """
        Return a new table build from the evaluation of a table expression
        """
        columns = self.reval(exprs)

        t = Table(self._rows)
        for column in columns:
            t.add_column(column.name, column)

        return t

    # ------------------------------------------------------------------
    # Mutative methods
    # ------------------------------------------------------------------
    def rename(self, name_or_index, newname):
        """ Change the name of a column.

            The Original column may be specified using its index or name.
            If the name is ambiguous, the behavior is unspecified.
        """
        index = self._get_column_index(name_or_index)
        if index == 0:
            raise ValueError("Cannot rename column 0")

        self._meta[index].name = newname

    def add_column(self, name, *exprs):
        if name is None:
            name = "C" + str(len(self._meta))
        if name in self.names():
            raise DuplicateName(name)

        column, *remainer = self.reval(*exprs)
        if len(remainer):
            raise ValueError("Too many columns")
        if len(column) != self._rows:
            raise RowCountMismatch("column " + name, self._rows, len(column))

        meta = Table.Column(name, column)
        self._meta.append(meta)

    def add_columns(self, *col_specs):
        for col_spec in col_specs:
            self.add_column(*col_spec)

    def del_column(self, index_or_name):
        """ Remove a column from the table, given it's index or name
        """
        index = self._get_column_index(index_or_name)
        if index == 0:
            raise ValueError("Cannot remove column 0")

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

        All user-provided functions are assumed to return a column
        as a list of values.
        """
        if callable(head):
            # It's an f-expression
            if tail:
                return [ C(head(self._rows, *self.reval(*tail))) ]
            else:
                return [ C(head(self._rows)) ]
        else:
            # It's a list
            result = self.reval_item(head)

            for param in tail:
                result += self.reval_item(param)
            return result

    def reval_item(self, item):
        if type(item) == str:
            idx = self._get_column_index(item)
            return [ self._meta[idx] ]
        if isinstance(item, Table.Column):
            return [ item ]

        try:
            it = iter(item)
        except TypeError as e:
            pass
        else:
            return self.reval(*it)

        return [ C([item] * self._rows) ]

    def __getitem__(self,c):
        c = self._get_column_index(c)

        return self._meta[c]

    def _get_column_index(self, index_or_name):
        if type(index_or_name) is str:
            index_or_name = self.names().index(index_or_name)

        return int(index_or_name)

    def __str__(self):
        return driver.Tabular().format(self)

# ======================================================================
# Helper for table expression evaluation
# ======================================================================
def column(col):
    """
    Return a column expression that evaluates to ''col''.
    """
    return lambda rowcount : col

add = lambda rowcount, *cols : [sum(row) for row in zip(*cols)]

# ======================================================================
# Create tables from existing sequences
# ======================================================================
def table_from_data(data, headings):
    if not len(data):
        rowcount = 0
    else:
        # Check is all columns have the same length
        it = iter(data)
        rowcount = len(next(it))
        for col in it:
            if len(col) != rowcount:
                raise InvalidError()

    t = Table(rowcount)
    for heading, column in zip(headings, data):
        t.add_column(heading, lambda rc : column)

    return t

# ======================================================================
# Create tables from CSV
# ======================================================================
def join(tableA, tableB, keyA, keyB=None):
    """
    Join tableA and tableB using their respective columns keyA and keyB.

    If keyB is unspecified or None, keyB is set to keyA.
    The key columns are assumed to be sorted in ascending order.
    Rows contening the None value in their key column are ignored.
    """
    colsA = tableA.names()
    colsA.remove("#")
    colsB = tableB.names()
    colsB.remove("#")
    if keyB is not None and keyB != keyA:
        itA = tableA.row_iterator([keyA] + colsA)
        itB = tableB.row_iterator([keyB] + colsB)
    else:
        itA = tableA.row_iterator([keyA] + colsA)
        colsB.remove(keyA)
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
                #print(rA + rB)
                result.append(rA + rB)
                kA, *rA = next(itA)
                kB, *rB = next(itB)
    except StopIteration:
        pass

    return table_from_data(list(zip(*result)), colsA + colsB)

# ======================================================================
# Create tables from CSV
# ======================================================================
import csv
from fin import datetime

def table_from_csv(iterator, format='', delimiter=','):
    rows = []
    reader = csv.reader(iterator, delimiter=delimiter)
    heading = next(reader)
    rows = list(reader)
    cols = []
    names = []
    for name, fchar, col in zip(heading, format, zip(*rows)):
        if fchar=='-': # IGNORE
            continue
        elif fchar=='n': # NUMERIC
            f = float
        elif fchar=='d': # DATE
            f = datetime.parseisodate
        elif fchar=='i': # INTEGER
            f = int

        col = list(col)
        for index, value in enumerate(col):
            try:
                col[index] = f(value)
            except:
                col[index] = None

        names.append(name)
        cols.append(col)

    return table_from_data(cols, names)

def table_from_csv_file(fname, format='', delimiter=','):
    with open(fname, newline='') as csvfile:
        return table_from_csv(csvfile, format=format, delimiter=delimiter)
