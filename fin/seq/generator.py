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
    chunk = None
    def _chunk_generator(count):
        nonlocal chunk

        if chunk is None:
            chunk = fct()
        if not chunk:
            return nothing()(count)
        else:
            return rawdata(chunk, chunk_generator(fct))(count)

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

def range(start_or_end, end=None, step=1):
    MAX_BUFFER_SIZE=500

    start = 0
    if end is None:
        end = start_or_end
    else:
        start = start_or_end

    def fct():
        nonlocal start

        n = min(math.ceil((end - start)/step), MAX_BUFFER_SIZE)
        if n <= 0:
            return ()

        chunk = [None]*n
        for i in builtins.range(n):
            chunk[i] = (i*step+start,)

        start += n*step

        return chunk

    return chunk_generator(fct)
