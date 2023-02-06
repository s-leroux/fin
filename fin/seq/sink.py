""" A sink is a consumer for a sequence
"""

def take(source, n):
    """ Consume up to n rows from source and return them in a list.
    """
    result = []
    while n > 0:
        chunk, source = source(n)
        if not chunk:
            break
        else:
            result += chunk
            n -= len(chunk)

    return result

def all(source):
    """ Consume a source until eof and return all data
        in one (potentially huge) list.

        Obviously, you should not call this function on an
        infinite sequence.

    """
    BLOCK_SIZE = 1024*1024

    result = []
    while True:
        data, source = source(BLOCK_SIZE)
        if not data:
            return result
        else:
            result += data


def consumeall(source):
    """ Consume a source until eof and discard data.
        Use this function when you need the side-effects
        of reading a sequence, but not the associated data.

        Obviously, you should not call this function on an
        infinite sequence.

    """
    BLOCK_SIZE = 1024*1024

    while True:
        data, source = source(BLOCK_SIZE)
        if not data:
            return source

def count(source):
    """ Consume a source until eof, counting the number of
        bytes read,

        Obviously, you should not call this function on an
        infinite sequence.

    """
    BLOCK_SIZE = 1024*1024
    total = 0

    while True:
        data, source = source(BLOCK_SIZE)
        if not data:
            return total
        else:
            total += len(data)

