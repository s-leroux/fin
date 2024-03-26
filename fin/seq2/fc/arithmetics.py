from collections import deque

from fin.seq2.column import Column

# ======================================================================
# Arithmetic operators
# ======================================================================
def add(serie, head, *tail):
    result = head
    for item in tail:
        result += item

    return result

def sub(serie, head, *tail):
    result = head
    for item in tail:
        result -= item

    return result

def mul(serie, head, *tail):
    result = head
    for item in tail:
        result *= item

    return result

def div(serie, head, *tail):
    result = head
    for item in tail:
        result /= item

    return result

# ======================================================================
# Comparisons
# ======================================================================
def min(n):
    """
    Sliding minimum over a n-periods window.
    """
    assert n > 0
    def _min(serie, values):
        rowcount = serie.rowcount
        result = []
        store = result.append
        queue = deque()
        popleft = queue.popleft
        pushright = queue.append
        cooldown = n-1

        for value in values:
            try:
                while len(queue) >= n:
                    popleft()
                while len(queue) and queue[0] > value:
                    popleft()
                pushright(value)
            except TypeError:
                cooldown = n

            if cooldown:
                store(None)
                cooldown -= 1
            else:
                store(queue[0])

        return Column.from_sequence(result)

    return _min

def max(n):
    """
    Sliding maximum over a n-periods window.
    """
    assert n > 0
    def _max(serie, values):
        rowcount = serie.rowcount
        result = []
        store = result.append
        queue = deque()
        popleft = queue.popleft
        pushright = queue.append
        cooldown = n-1

        for value in values:
            try:
                while len(queue) >= n:
                    popleft()
                while len(queue) and queue[0] < value:
                    popleft()
                pushright(value)
            except TypeError:
                cooldown = n

            if cooldown:
                store(None)
                cooldown -= 1
            else:
                store(queue[0])

        return Column.from_sequence(result)

    return _max

