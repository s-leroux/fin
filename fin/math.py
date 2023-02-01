EPSILON=0.0001

class MathError(Exception):
    pass

class DomainError(MathError):
    pass

def solve(fct, x, min, max, vars={}):
    """
    Find a root for a (supposedly) continuous and monotonic function in the
    range [min, max].
    """
    # Sanityze
    if max < min:
        min, max = max, min

    da = vars.copy()
    db = vars.copy()
    dc = vars.copy()

    da[x] = min
    db[x] = (min+max)/2
    dc[x] = max

    a = fct(**da)
    c = fct(**dc)
    if a*c > 0:
        raise DomainError()

    while not -EPSILON < min-max < EPSILON:
        db[x] = (min+max)/2
        b = fct(**db)
        if b*c < 0:
            a = b;
            min = da[x] = db[x]
        elif a*b < 0:
            c = b
            max = dc[x] = db[x]
        # Special cases
        elif a == 0:
            return da[x]
        elif b == 0:
            return db[x]
        elif c == 0:
            return dc[x]
        else:
            raise DomainError()

    return db[x]

