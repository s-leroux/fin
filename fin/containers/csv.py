import io
import csv

class CSV:
    """
    A table-like structure specifically designed to store CSV data.
    """
    def __init__(self):
        raise NotImplementedError(
            f"You must use a factory method to create instances of {type(self).__qualname__}"
        )

    @classmethod
    def from_text(cls, text, **kwargs):
        return cls.from_lines(text.splitlines(), **kwargs)

    @classmethod
    def from_lines(cls, iterable, **kwargs):
        iterator = iter(iterable)
        reader = csv.reader(iterator, **kwargs)
        self = cls.__new__(cls)
        self.headings = headings = next(reader)
        self.rows = rows = [row for row in reader]
        self.kwargs = kwargs
        kwargs.setdefault("lineterminator", "\n")

        self.columns = ColumnSelector(headings, rows, kwargs)

        return self

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __str__(self):
        with io.StringIO() as output:
            writer = csv.writer(output, self.headings, **self.kwargs)
            writer.writerow(self.headings)
            writer.writerows(self.rows)

            return output.getvalue()

    def __getitem__(self, idx):
        return self.rows[idx]

class ColumnSelector:
    def __init__(self, headings, rows, kwargs):
        self.headings = headings
        self.rows = rows
        self.kwargs = kwargs

    def __len__(self):
        return len(self.headings)

    def __getitem__(self, tpl):
        if type(tpl) is not tuple:
            tpl = (tpl,)

        headings = self.headings
        rows = self.rows
        store = [[] for _ in range(len(rows))]

        for column in tpl:
            idx = headings.index(column)
            for dst, src in zip(store, rows):
                dst.append(src[idx])
        
        result = CSV.__new__(CSV)
        result.headings = tpl
        result.rows = store
        result.kwargs = kwargs = self.kwargs
        self.columns = ColumnSelector(tpl, rows, kwargs)

        return result

