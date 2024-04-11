def first(*cols):
    return [col[0] for col in cols]

def count(*cols):
    return [len(col) for col in cols]
