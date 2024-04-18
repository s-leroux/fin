from fin.utils.ternary cimport *

# ======================================================================
# Python wrappers arround C-level functions
# ======================================================================
def parse_pattern(pat):
    return ternary_parse_pattern(pat)
