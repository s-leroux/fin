from fin.seq.column import Column

# ======================================================================
# Expr
# ======================================================================
def c(data, *, name=None):
    return ( lambda rowcount : Column(name, data) ,) # is the lambda required here?

def constant(value, *, name=None):
    return ( lambda rowcount : Column(name, [value]*rowcount) ,) # is the lambda required here?

def call(f, *args, name=None):
    return ( lambda rowcount : Column(name, f(rowcount, *args)) ,)

def apply(f, *, name=None):
    return lambda rowcount, *args : Column(name, f(rowcount, *args))

def spread(f):
    return lambda rowcount, *args : [(f, arg) for arg in args]

def iterator(it, *, name=None):
    return ( lambda rowcount : Column(name, [next(it, None) for _ in range(rowcount)]) ,)

def iterable(it, *, name=None):
    return iterator(iter(it), name=name)

def ramp(start=0, end=None, *, name=None):
    return ( lambda rowcount : Column(name, range(start, end if end is not None else start+rowcount)) ,)

