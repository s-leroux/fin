import sys

from bs4 import BeautifulSoup

def _union(selection, start, end):
    """
    Add all values in the (start, end) range to the selection.

    This functions follows Python semantic of considering _start_ included,
    but _end_ excluded in the ranges.
    """
    result = []
    for a,b in selection:
        if start > b:
            result.append((a,b))
        elif end < a:
            result.append((start,end))
            start = a
            end = b
        elif start <= a:
            end = max(end, b)
        elif end >= b:
            start = min(start, a)
        else:
            start = a
            end = b

    result.append((start,end))

    return result

def _filter_cell_text(text, element):
    """
    Apply various heuristics to cleanup cell data.
    """

    # MarketWatch has duplicated headings
    if not text.isdecimal():
        l = len(text)
        head = text[:l//2]
        tail = text[l//2:]
        if head == tail:
            text = head

    return text

def cols(start, end):
    def _cols(cols, rows):
        return _union(cols, start, end), rows

    return _cols

def rows(start, end):
    def _rows(cols, rows):
        return cols, _union(rows, start, end)

    return _rows

class Table:
    def __init__(self, indices, data, *, data_row_start=0, data_col_start=0):
        self.data = data
        self.indices = indices
        self.data_row_start = data_row_start
        self.data_col_start = data_col_start

    def __repr__(self):
        return f"Table({self.indices!r}, {self.data!r}"

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def select(self, *headings):
        selection = ((),())
        for heading in headings:
            selection = self.indices[heading](*selection)

        return selection

    def find(self, *headings):
        cols, rows = self.select(*headings)
        if not cols:
            cols = ((self.data_col_start, sys.maxsize),)
        if not rows:
            rows = ((self.data_row_start, sys.maxsize),)

        result = []
        for rstart, rend in rows:
            for rindex in range(rstart, rend):
                try:
                    in_row = self.data[rindex]
                except IndexError:
                    break

                out_row = []
                for cstart, cend in cols:
                    for cindex in range(cstart, cend):
                        try:
                            cell = in_row[cindex]
                        except IndexError:
                            break

                        out_row.append(cell)
                result.append(out_row)

        return result

def parse(fragment):
    """
    Parse a table statement as a python object.
    """
    indices = {}
    data = []

    data_row_start = 0
    data_col_start = 0

    for rnum, tr in enumerate(fragment.find_all("tr")):
        py_row = []
        for cnum, titem in enumerate(tr.find_all(("th", "td"))):
            # Clean-up markup
            for it in titem.find_all("sup"):
                it.extract()

            name = titem.name
            text = titem.get_text(strip=True)
            text = _filter_cell_text(text, name)

            py_row.append(text)
            if name == "th":
                if cnum > 0:
                    indices[text] = cols(cnum, cnum+1)
                    data_row_start = 1
                else:
                    rows(rnum, rnum+1)
            elif cnum == 0:
                # Heuristic: the first td element of each row is assumed to
                # be a row header
                indices[text] = rows(rnum, rnum+1)
                data_col_start = 1

        data.append(py_row)


    return Table(indices, data, data_row_start=data_row_start, data_col_start=data_col_start)
