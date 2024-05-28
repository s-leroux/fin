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
        return cls.from_sequence(text.splitlines(), **kwargs)

    @classmethod
    def from_sequence(cls, sequence, **kwargs):
        iterator = iter(sequence)
        reader = csv.reader(iterator, **kwargs)
        self = cls.__new__(cls)
        headings = self.headings = next(reader)
        rows = self.rows = [row for row in reader]
        self.columns = ColumnSelector(headings, rows)

        return self

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        return self.rows[idx]

class ColumnSelector:
    def __init__(self, headings, rows):
        self.headings = headings
        self.rows = rows

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
        self.columns = ColumnSelector(tpl, rows)

        return result

