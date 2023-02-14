
class InvalidError(Exception):
    pass

class DuplicateName(ValueError):
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
        self._meta = [ dict(name="#") ]
        self._data = [ list(range(rows)) ]

    def columns(self):
        return len(self._data)

    def rows(self):
        return len(self._data) and self._rows

    def names(self):
        """ Return the column names
        """
        return [meta['name'] for meta in self._meta]

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
            raise InvalidError()

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
        cols = [self[n]._column for n in cols]
        result = fct(self._rows, *cols)

        return result

    def filter(self, fct, *cols):
        cols = [self._data[self._get_column_index(n)] for n in cols]
        rows = [ row for row, flt in zip(zip(*self._data[1:]),zip(*cols)) if fct(*flt) ]

        t = Table(len(rows))
        for meta, column in zip(self._meta[1:], zip(*rows)):
            t.add_column(meta['name'], column)
            t.set_column_meta(meta['name'], **meta)

        return t

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

import csv
def table_from_csv(iterator, format=''):
    rows = []
    reader = csv.reader(iterator)
    heading = next(reader)
    rows = list(reader)
    for index, fchar in enumerate(format):
        if fchar=='n': # NUMERIC
            for row in rows:
                row[index] = float(row[index])
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

def table_from_csv_file(fname, format=''):
    with open(fname, newline='') as csvfile:
        return table_from_csv(csvfile, format=format)
