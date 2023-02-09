
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

    def add_column(self, name, init, *cols):
        column = self.eval(init, *cols)

        if column is None:
            raise TypeError("Can't create column from 'init': " + repr(init))
        if len(column) != self._rows:
            raise InvalidError()

        self._data.append(column)
        self._headers.append(name)

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
def table_from_csv(fname, format=''):
    rows = []
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
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
