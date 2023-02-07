""" A sink is a consumer for a sequence
"""

def take(source, n):
    """ Consume up to n rows from source and return them in a list.
    """
    result = ()
    while n > 0:
        chunk, source = source(n)
        if not chunk:
            break
        else:
            if result:
                i = len(result)
                while i:
                    i -= 1
                    result[i].extend(chunk[i])
            else:
                result = [list(col) for col in chunk]
            n -= len(chunk[0])

    return tuple(tuple(col) for col in result), source

def all(source):
    """ Consume a source until eof and return all data
        in one (potentially huge) list.

        Obviously, you should not call this function on an
        infinite sequence.

    """
    BLOCK_SIZE = 1024

    result, source = source(BLOCK_SIZE)
    result = [list(col) for col in result]
    while True:
        chunk, source = source(BLOCK_SIZE)
        if not chunk:
            break
        else:
            i = len(result)
            while i:
                i -= 1
                result[i].extend(chunk[i])

    return tuple(tuple(col) for col in result)

def consumeall(source):
    """ Consume a source until eof and discard data.
        Use this function when you need the side-effects
        of reading a sequence, but not the associated data.

        Obviously, you should not call this function on an
        infinite sequence.

    """
    BLOCK_SIZE = 1024

    while True:
        data, source = source(BLOCK_SIZE)
        if not data:
            return source

def count(source):
    """ Consume a source until eof, counting the number of
        rows.

        Obviously, you should not call this function on an
        infinite sequence.

    """
    BLOCK_SIZE = 1024
    total = 0

    while True:
        data, source = source(BLOCK_SIZE)
        if not data:
            return total
        else:
            total += len(data[0])

