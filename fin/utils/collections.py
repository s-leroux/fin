"""
A set of utilities to manipulate standard collections.
"""

def dictionaries_to_list(fields, iterable):
    """
    Convert dictionaries to list of values.
    """
    for mapping in iterable:
        yield [mapping[field] for field in fields]

def km_to_ll(fields, iterable):
    """
    Convert an interable of (key, values) pairs, where values is
    a mapping, to a nested list.

    This is useful when a collections is (somewhat improperly)
    stored in a mappping instead of a sequence.
    """
    for key, mapping in iterable:
        yield [key, *[mapping[field] for field in fields]]

def mm_to_ll(fields, mapping):
    """
    Convert a mapping of mappings to a list of lists.
    """
    return km_to_ll(fields, mapping.items())

