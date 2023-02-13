
class InvalidError(Exception):
    pass

class ColumnRef:
    def __init__(self, table, index):
        self._table = table
        self._index = index
        self._column = table._data[index]

    def __add__(self, o):
        result = [v+o for v in self._column]
        return result

    def __getitem__(self, index):
        return self._column[index]

class Table:
    """ A Table is a list of columns, all of the same length
        (i.e.: tables are rectangular)
    """
    def __init__(self, rows):
        self._rows = rows
        self._headers = []
        self._data = []

    def columns(self):
        return len(self._data)

    def rows(self):
        return len(self._data) and self._rows

    def names(self):
        """ Return the column names
        """
        return list(self._headers)

    def rename(self, name_or_index, newname):
        """ Change the name of a column.

            The Original column may be specified using its index or name.
            If the name is ambiguous, the behavior is unspecified.
        """
        column = self.get_column(name_or_index)
        index = column._index
        self._headers[index] = newname

    def add_column(self, name, init, *cols):
        column = self.eval(init, *cols)
        if type(column) != list: # In case the eval function returned a generator
            column = list(column)

        if column is None:
            raise TypeError("Can't create column from 'init': " + repr(init))
        if len(column) != self._rows:
            raise InvalidError()

        self._data.append(column)
        self._headers.append(name)

    def add_columns(self, *col_specs):
        for col_spec in col_specs:
            self.add_column(*col_spec)

    def eval(self, init, *cols):
        if callable(init):
            return self.eval_from_callable(init, *cols)
        else:
            try:
                it = iter(init)
            except TypeError:
                return self.eval_from_value(init, *cols)
            else:
                return self.eval_from_iterator(it, *cols)

    def eval_from_value(self, value):
        return [value]*self._rows

    def eval_from_iterator(self, it):
        return list(it)

    def eval_from_callable(self, fct, *cols):
        cols = [self.get_column(n)._column for n in cols]
        return fct(self._rows, *cols)

    def get_column(self,c):
        if type(c) is str:
            c = self._headers.index(c)

        return ColumnRef(self, c)

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
            fmt += f" {{:{w}}}"
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

def table_from_data(data, headers):
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
    t._data = data
    t._headers = headers

    return t

import csv
def table_from_csv(iterator, format=''):
    rows = []
    reader = csv.reader(iterator)
    header = next(reader)
    rows = list(reader)
    for index, fchar in enumerate(format):
        if fchar=='n': # NUMERIC
            for row in rows:
                row[index] = float(row[index])

    cols = list(zip(*rows))
    n = 0
    for index, fchar in enumerate(format):
        if fchar=='-':
            del cols[n]
        else:
            n += 1

    return table_from_data(cols, header)

def table_from_csv_file(fname, format=''):
    with open(fname, newline='') as csvfile:
        return table_from_csv(csvfile, format=format)
