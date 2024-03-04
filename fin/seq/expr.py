from fin.seq.column import Column

# ======================================================================
# Expr
# ======================================================================
def c(data, *, name=None):
    return ( lambda rowcount : Column.from_sequence(name, data) ,)

def constant(value, *, name=None):
    return ( lambda rowcount : Column.from_sequence(name, [value]*rowcount) ,)

def call(f, *args, name=None):
    return ( lambda rowcount : Column.from_sequence(name, f(rowcount, *args)) ,)

def apply(f, *, name=None):
    return lambda rowcount, *args : Column.from_sequence(name, f(rowcount, *args))

def map(f, *, name=None):
    return lambda rowcount, *args : Column.from_sequence(name, [f(*row) for row in zip(*args)])

def spread(f):
    return lambda rowcount, *args : [(f, arg) for arg in args]

def iterator(it, *, name=None):
    return ( lambda rowcount : Column.from_sequence(name, [next(it, None) for _ in range(rowcount)]) ,)

def iterable(it, *, name=None):
    return iterator(iter(it), name=name)

def ramp(start=0, end=None, *, name=None):
    return ( lambda rowcount : Column.from_sequence(name, range(start, end if end is not None else start+rowcount)) ,)

def serie(v0, fct, *, name=None):
    def g(rowcount, v0):
        while rowcount:
            yield v0
            v0 = fct(v0)

            rowcount -= 1

    return lambda rowcount : Column.from_sequence(name, g(rowcount, v0))
