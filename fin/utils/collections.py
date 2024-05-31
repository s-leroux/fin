"""
A set of utilities to manipulate standard collections.
"""

def dictionaries_to_list(fields, iterable):
    """
    Convert dictionaries to list of values.
    """
    for obj in iterable:
        yield [obj[field] for field in fields]
