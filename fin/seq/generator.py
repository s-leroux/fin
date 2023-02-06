import builtins
import math

# ======================================================================
# Constants and utilities
# ======================================================================
def samples(values=()):
    return tuple(values)
    # return array('f', values)

def chunk_generator(fct):
    """ Build a sequence chunk by chunk
    """
    
    def _chunk_generator(count):
        chunk = fct()
        if not chunk:
            return nothing()(count)
        else:
            return rawdata(chunk, _chunk_generator)(count)

    return _chunk_generator

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

def range(from_or_to, to=None, step=1):
    BUFFER_SIZE=500

    from_ = 0
    if to is None:
        to = from_or_to
    else:
        from_ = from_or_to

    def fct():
        nonlocal from_

        n = min(math.ceil((to - from_)/step), BUFFER_SIZE)
        if n <= 0:
            return ()

        chunk = [None]*n
        for i in builtins.range(n):
            chunk[i] = (i*step+from_,)

        from_ += n*step

        return chunk

    return chunk_generator(fct)
