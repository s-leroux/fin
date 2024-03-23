from fin.seq2.column import Column

def constant(n, **kwargs):
    def _sequence(rowcount):
        return Column.from_constant(rowcount, n)

    return _sequence

def sequence(seq, **kwargs):
    def _sequence(*args):
        # The rowcount parameter is optional in this function since it is useless
        # This allows the funtion to be used to define the index of a new serie
        return Column.from_sequence(seq, **kwargs)

    return _sequence

def named(new_name):
    def _named(rowcount, column):
        return column.rename(new_name)

    return _named
