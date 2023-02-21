
class InvalidError(Exception):
    pass

class RowCountMismatch(InvalidError):
    def __init__(self, detail, expected, actual):
        msg = """in {detail}: {expected} rows expected, {actual} given"""
        super().__init__(msg.format(detail=detail, expected=expected, actual=actual))

class DuplicateName(ValueError):
    pass

class ColumnRef:
    def __init__(self, table, index):
        self._table = table
        self._index = index
        self._column = table._data[index]
        self._meta = table._meta[index]

    def __eq__(self, other):
        if not isinstance(other, ColumnRef):
            return False

        if self._meta != other._meta:
            return False

        if self._column != other._column:
            return False

        return True

    def __len__(self):
        return len(self._column)

    def __add__(self, o):
        result = [v+o for v in self._column]
        return result

    def __getitem__(self, index):
        return self._column[index]

    def __setitem__(self, index, value):
        self._column[index] = value

# ======================================================================
# Table class
# ======================================================================
class Table:
    """ A Table is a list of columns, all of the same length
        (i.e.: tables are rectangular)
    """
    def __init__(self, rows):
        self._rows = rows
        self._meta = [ dict(name="#") ]
        self._data = [ list(range(rows)) ]

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def columns(self):
        return len(self._data)

    def rows(self):
        return len(self._data) and self._rows

    def row_iterator(self, columns=None):
        """
        Return an iterator on the table rows.

        The ''column'' parameter lists the columns to select. If
        you specify ''None'' all the columns are selected.
        """
        columns = [self[name_or_index] for name_or_index in columns] if columns != None else self._data
        return zip(*columns)

    def names(self):
        """ Return the column names
        """
        return [meta['name'] for meta in self._meta]

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
        cols = [self._data[self._get_column_index(n)] for n in cols]
        rows = [ row for row, flt in zip(zip(*self._data[1:]),zip(*cols)) if fct(*flt) ]

        t = Table(len(rows))
        for meta, column in zip(self._meta[1:], zip(*rows)):
            t.add_column(meta['name'], column)
            t.set_column_meta(meta['name'], **meta)

        return t

    def select(self, *cols):
        """
        Return a new table containing a sub-set of the reveiver's columns.
        """
        t = Table(self._rows)
        indices = [self._get_column_index(col) for col in cols]
        for index in indices:
            t._meta.append(self._meta[index])
            t._data.append(self._data[index])

        return t

    # ------------------------------------------------------------------
    # Mutative methods
    # ------------------------------------------------------------------
    def rename(self, name_or_index, newname):
        """ Change the name of a column.

            The Original column may be specified using its index or name.
            If the name is ambiguous, the behavior is unspecified.
        """
        column = self[name_or_index]
        index = column._index
        if index == 0:
            raise ValueError("Cannot rename column 0")

        self._meta[index]['name'] = newname

    def add_column(self, name, init, *cols):
        if name in self.names():
            raise DuplicateName(name)

        column = self.eval(init, *cols)

        if column is None:
            raise TypeError("Can't create column from 'init': " + repr(init))
        if type(column) != list: # In case, for example, the function returns a generator
            column = list(column)
        if len(column) != self._rows:
            raise RowCountMismatch("column " + name, self._rows, len(column))

        self._data.append(column)
        self._meta.append(dict(name=name))

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
        del self._data[index]

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
            meta['name']=name

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def eval(self, init, *cols):
        """
        Evaluate an column expression.

        A column expression can be:
        1) A callable with the corresponding column arguments
        2) A ColumnRef
        3) An iterable
        4) A constant value

        When the column expression is a callable, it may return any value.
        In all other cases, ''eval'' returns a list.
        """
        if callable(init):
            return self.eval_from_callable(init, *cols)
        elif type(init) == ColumnRef:
            return self.eval_from_column_ref(init, *cols)
        else:
            try:
                it = iter(init)
            except TypeError:
                return self.eval_from_value(init, *cols)
            else:
                return self.eval_from_iterator(it, *cols)

    def eval_from_value(self, value):
        return [value]*self._rows

    def eval_from_column_ref(self, colref):
        return colref._column

    def eval_from_iterator(self, it):
        return list(it)

    def eval_from_callable(self, fct, *cols):
        cols = [self[n]._column for n in cols]
        result = fct(self._rows, *cols)

        return result

    def __getitem__(self,c):
        c = self._get_column_index(c)

        return ColumnRef(self, c)

    def _get_column_index(self, index_or_name):
        if type(index_or_name) is str:
            index_or_name = self.names().index(index_or_name)

        return int(index_or_name)

    def __str__(self):
        def value_to_string(value):
            if type(value) == float:
                return f"{value:10.4f}"
            else:
                return str(value)

        rows = [ self.names() ]
        width = [ len(c) for c in rows[0] ]

        for row in zip(*self._data):
            row = [value_to_string(value) for value in row]
            for i, value in enumerate(row):
                width[i] = max(width[i], len(value))

            rows.append(row)

        fmt = ""
        for w in width:
            fmt += f" {{:>{w}}}"
        fmt += "\n"

        result = ""
        it = iter(rows)

        # title row
        result += fmt.format(*next(it))
        result += "-"*len(result) + "\n"

        # data rows
        for row in it:
            result += fmt.format(*row)

        return result

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
        t.add_column(heading, column)

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
        itB = tableA.row_iterator([keyA] + colsB)

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
def table_from_csv(iterator, format='', delimiter=','):
    rows = []
    reader = csv.reader(iterator, delimiter=delimiter)
    heading = next(reader)
    rows = list(reader)
    for index, fchar in enumerate(format):
        if fchar=='n': # NUMERIC
            for row in rows:
                try:
                    row[index] = float(row[index])
                except:
                    row[index] = None
        elif fchar=='i': # INTEGER
            for row in rows:
                row[index] = int(row[index])

    cols = list(zip(*rows))
    n = 0
    for index, fchar in enumerate(format):
        if fchar=='-':
            del cols[n]
            del heading[n]
        else:
            n += 1

    return table_from_data(cols, heading)

def table_from_csv_file(fname, format='', delimiter=','):
    with open(fname, newline='') as csvfile:
        return table_from_csv(csvfile, format=format, delimiter=delimiter)
