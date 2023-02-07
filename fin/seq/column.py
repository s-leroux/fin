import builtins

def range(start_or_end, end=None, step=1):
    def build():
        return tuple(builtins.range(start_or_end, end, step) if end else builtins.range(start_or_end, step))

    return build
