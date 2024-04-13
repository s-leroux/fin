from pprint import pprint

from .column cimport Column
from .serie cimport (
        Join,
        serie_get_column_by_name,
        c_left_outer_join,
    )

cdef class SavedState:
    cdef unsigned   dp

    def __repr__(self):
        return f"SavedState(dp={self.dp})"

cdef class State:
    cdef list       frame
    cdef list       data
    cdef list       ops
    cdef unsigned   dp

    def __cinit__(self):
        self.frame = []
        self.data = []
        self.ops = []
        self.dp = 0

def py_evaluate(serie, expr):
    """ For testing purposes.
    """
    return evaluate(serie, expr)

cdef inline int flush(State state) except -1:
    while len(state.data) > state.dp:
        data = state.data.pop()
        state.frame.append(data)

cdef dump(State state):
    print("-----"*16)
    print("ops")
    for i, op in enumerate(state.ops):
        print(f"{i:3d} {op!r}")

    print("data")
    for i, data in enumerate(state.data):
        flag = ">" if i == state.dp else " "
        print(f"{i:3d}{flag}{data!r}")

cdef tuple evaluate(Serie serie, object expr):
    """ Evaluate an expresion.

        This function is the top-most entry point for the s-expression interpreter.
    """
    cdef bint           trace = False # For debugging purposes
    cdef State          state = State()
    cdef SavedState     saved
    cdef Join           join

    state.ops.append(expr)
    while state.ops:
        obj = state.ops.pop()
        if trace:
            print(f"pop {obj!r}")
        t = type(obj)
        if t is SavedState:
            state.dp = (<SavedState?>obj).dp
        elif t is Column:
            state.data.append(obj)
        elif t is str:
            state.data.append(serie_get_column_by_name(serie, obj))
        elif t is tuple:
            saved = SavedState()
            saved.dp = state.dp
            state.ops.append(saved)
            state.dp = len(state.data)
            state.ops.extend(obj)
        elif t is Serie:
            join = c_left_outer_join(serie, obj, False)
            if join.index != serie._index: # XXX Impossible by def of the `left outer join`‽
                raise ValueError(f"Cannot insert serie: indices differ.")
            state.ops.append(join.right)
        elif callable(obj):
            flush(state)
            state.ops.append(obj(serie, *state.frame))
            state.frame.clear()
        elif t is int or t is float:
            raise TypeError(f"Unexpected {t}. Did you mean fc.constant({t!r})?")
        else:
            raise ValueError(f"Unexpected object {obj!r} of type {t}")

        if trace:
            dump(state)

    flush(state)
    return tuple(state.frame)
