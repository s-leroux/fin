# ======================================================================
# Constants and utilities
# ======================================================================
def samples(values=()):
    return tuple(values)
    # return array('f', values)

# ======================================================================
# Core generators
# ======================================================================
def nothing():
    """ Empty generator. Produce an infinite stream of nothingness.
    """
    def _nothing(count, cache=()*1000):
        return cache[:count], _nothing

    return _nothing

def constant(*values):
    """ Return a generator producing an infinite stream of samples
        with the same value
    """
    buffer = ((values),)*1000

    def read(n):
        return buffer[:n], read

    return read

def rawdata(data, cont=nothing()):
    """ Return a generator from rawdata.
    """
    data = samples(data)
    def at(offset):
        def read(count):
            stop = offset+count
            result = data[offset:stop]
            if result:
                return result, at(stop)
            else:
                return cont(count)

        return read

    return at(0)
