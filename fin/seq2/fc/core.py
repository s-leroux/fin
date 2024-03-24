from fin.seq2.column import Column

def constant(n, **kwargs):
    def _sequence(serie):
        return Column.from_constant(serie.rowcount, n)

    return _sequence

def sequence(seq, **kwargs):
    def _sequence(serie):
        return Column.from_sequence(seq, **kwargs)

    return _sequence

def named(new_name):
    def _named(serie, column):
        return column.rename(new_name)

    return _named
