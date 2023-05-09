# cython: boundscheck=False
# cython: cdivision=True
# cython: binding=True

"""
Cython implementation of the Kelly Criterion.
"""
cpdef double kelly_criterion(double p, double a, double b, double f_star):
    """
    Model for the general form of the Kelly formula.
    
    From https://en.wikipedia.org/wiki/Kelly_criterion:
    ``f^{*}`` is the fraction of the assets to apply to the security.
    ``p`` is the probability that the investment increases in value.
    ``q`` is the probability that the investment decreases in value (implied since ``q = 1−p``).
    ``a`` a is the fraction that is lost in a negative outcome. If the security price falls 10%, then a = 0.1
    ``b`` is the fraction that is gained in a positive outcome. If the security price rises 10%, then b = 0.1.
    """
    cdef double q = 1.0-p
    return p/a - (1-p)/b - f_star
