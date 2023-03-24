# ======================================================================
# Column class
# ======================================================================
class Column:
    __slots__ = (
            "values",
            "name",
            )

    def __init__(self, name, sequence):
        self.name = name
        self.values = list(sequence)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]

    def __eq__(self, other):
        if not isinstance(other, Column):
            return False

        if self.values != other.values:
            return False
        if self.name != other.name:
            return False

        return True

    def __repr__(self):
        return "Column(\"{}\", {})".format(self.name, self.values)

    def min_max(self):
        """
        Return the minimum and maximum values in the column.
        None values are ignored.
        """
        values = [v for v in self.values if v is not None]
        return min(values), max(values)

    def slice(self, start, end=None):
        """
        Return a new column containing a copy of the data in the range [start;end)

        Negative values for `start` or `end` are not allowed.
        """
        if end is None:
            end = len(self.values)

        assert end >= start >= 0

        return Column(self.name, self.values[start:end])

    def alter(self, **kwargs):
        """
        Create a new column with the same values but altered metadata.
        """
        name = kwargs.get("name", None) or self.name

        return Column(name, self.values)

    def type(self):
        """
        Return the type of data stored in the column.

        Currently, the type is extrapolated from the actual data.
        If the content of a column is homogeneous (all values of the same type or None),
        that type is returned. Otherwise, None is returned.
        """
        t = None
        it = iter(self.values)
        for v in it:
            if v is not None:
                t = type(v)
                break
        else:
            return None

        for v in it:
            if v is not None:
                if type(v) is not t:
                    return None

        return t
