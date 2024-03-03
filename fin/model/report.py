from fin.utils import tabular
from fin.utils import formatters

"""
Textual tabular reports.
"""

class Report:
    """
    A report based on some underlying data model.
    """
    def __init__(self, context):
        self._keys = []
        self._descriptions = []
        self._formatters = []
        self._context = context

    def add_field(self, key, description, formatter):
        self._keys.append(key)
        self._descriptions.append(description)
        self._formatters.append(formatter)

    def add_fields(self, *args):
        for arg in args:
            self.add_field(*arg)

    def for_dict(self, d):
        """
        Produce a report for a dict-like data structure.
        """
        t = tabular.Tabular(2, self._context)
        description_formatter = formatters.StringLeftFormatter()
        for key, description, formatter in zip(self._keys, self._descriptions, self._formatters):
            t.add_row(description, d[key], formatters=(description_formatter, formatter))

        return t
