
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
    def __init__(self):
        self._rows = 0
        self._headers = []
        self._data = []

    def columns(self):
        return len(self._data)

    def rows(self):
        return len(self._data) and self._rows

    def append(self, column, title=None):
        if callable(column):
            column = column()
        self._data.append(column)
        self._headers.append(title)
        self._rows = max(self._rows, len(column))

    def get_column(self,c):
        if type(c) is str:
            c = self._headers.index(c)

        return ColumnRef(self, c)

def table_from_data(data, headers):
    t = Table()
    t._data = data
    t._headers = headers
    t._rows = max(len(c) for c in data)

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
