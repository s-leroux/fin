"""
Output driver for fin.seq.table.Table
"""


class Tabular:
    def format(self, table):
        def value_to_string(value):
            if type(value) == float:
                return f"{value:10.4f}"
            else:
                return str(value)

        rows = [ table.names() ]
        width = [ len(c) for c in rows[0] ]

        for row in zip(*table.data()):
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

class CSV:
    def __init__(self, delimiter=','):
        self._delimiter = delimiter

    def format(self, table):
        result = ""
        # Heading
        result += self._delimiter.join(table.names()) + "\n"

        # Data
        for row in table.row_iterator():
            result += self._delimiter.join(map(str, row)) + "\n"

        return result
