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
