""" A filter takes 1 or several
    input sequence to produce one or several output sequences
"""
from fin.seq import sink
from fin.seq import source

def chunked(source, size):
    """ Read the source in fixed-size chunks.

        Mostly used for testing purposes.
    """
    def _chunked(n):
        n = min(n, size)
        data, rest = sink.take(source, n)
        return data, chunked(rest, n)

    return _chunked

def fuse(a,b):
    """ Catenate two sequences.

        The resulting sequence will have at most min(N,M) rows
        where M (resp. N) is the number of rows in a (resp. b)
    """
    def read(n):
        ca, resta = a(n)
        if not ca:
            return (), source.nothing()

        la = len(ca[0])
        n = min(la, n)
        cb, restb = sink.take(b, n)
        if not cb:
            return (), source.nothing()

        lb = len(cb[0])

        # necessarily,  lb <= la
        # if lb < la we have exhausted b
        if lb < la:
            la = tuple([col[:lb] for col in la])

        return ca+cb, fuse(resta, restb)

    return read
