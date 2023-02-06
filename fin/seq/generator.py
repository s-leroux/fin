
# ======================================================================
# Constant generators
# ======================================================================
def constant(*values):
    """ Return a generator producing an infinite stream of samples
        with the same value
    """
    buffer = ((values),)*1000

    def read(n):
        return buffer[:n], read

    return read
