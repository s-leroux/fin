# cython: boundscheck=False
# cython: cdivision=True

from cpython cimport array
from libc.math cimport erf, sqrt, exp, log
from libc.stdlib cimport rand, RAND_MAX

from fin.mathx cimport NaN

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN = float("NaN")

# ======================================================================
# Financial functions
# ======================================================================
cpdef double bsm_call(
    double s_0,
    double k,
    double t,
    double r_0,
    double sigma_0):
    """
    The Black-Scholes formula to price call options.

    This function evaluates the price at time 0 of a European call option on
    non-dividend pying stck assuming constant volatility and interest rates.
    - k: Strike price
    - s_0: Underlying asset price at the valuation date
    - r_0: Continuously compounded risk-free interest rate at the valuation date
    - t: Time until expiration
    - sigma_0: Underlying asset volatility on the valuation date
    """
    v = sigma_0*sqrt(t)
    d1 = (log(s_0/k)+(r_0+sigma_0*sigma_0/2)*t)
    d1 /= v
    d2 = d1 - v

    return s_0*cdf(d1)-k*exp(-r_0*t)*cdf(d2)

cpdef double bsm_put(
    double s_0,
    double k,
    double t,
    double r_0,
    double sigma_0):
    """
    The Black-Scholes formula to price put options.

    This function evaluates the price at time 0 of a European put option on
    non-dividend pying stck assuming constant volatility and interest rates.
    - k: Strike price
    - s_0: Underlying asset price at the valuation date
    - r_0: Continuously compounded risk-free interest rate at the valuation date
    - t: Time until expiration
    - sigma_0: Underlying asset volatility on the valuation date
    """
    v = sigma_0*sqrt(t)
    d1 = (log(s_0/k)+(r_0+sigma_0*sigma_0/2)*t)
    d1 /= v
    d2 = d1 - v

    return -s_0*cdf(-d1)+k*exp(-r_0*t)*cdf(-d2)

cpdef double bsm_call_parity(
    double s_0,
    double k,
    double t,
    double r_0,
    double sigma_0,
    double parity):
    """
    The Black-Scholes formula to price call options with non-1:1 parity..
    """
    return bsm_call(s_0/parity, k/parity, t, r_0, sigma_0)

cpdef double bsm_put_parity(
    double s_0,
    double k,
    double t,
    double r_0,
    double sigma_0,
    double parity):
    """
    The Black-Scholes formula to price put options with non-1:1 parity..
    """
    return bsm_put(s_0/parity, k/parity, t, r_0, sigma_0)

# ======================================================================
# Statistical functions
# ======================================================================
cpdef double cdf(double x, double mu=0.0, double sigma=1.0):
    """ Cumulative distribution function for x normal distributions.
    """
    x = (x-mu)/sigma
    return (1.0 + erf(x / sqrt(2.0))) / 2.0


# ======================================================================
# Array management
# ======================================================================
cdef array.array double_array_template = array.array('d', [])
cdef array.array int_array_template = array.array('i', [])
cdef array.array byte_array_template = array.array('b', [])

cdef inline double[::1] alloc(unsigned n, double init_value = NaN):
    """
    Allocate a contiguous array of n double initialized to NaN.
    Return a view on the array.
    """
    cdef double[::1] arr = array.clone(double_array_template, n, zero=False)[::1]
    cdef unsigned i
    for i in range(n):
        arr[i] = init_value

    return arr


cdef inline array.array aalloc(unsigned n, double init_value = NaN):
    """
    Allocate a contiguous array of n double initialized to NaN.
    Return the array.
    """
    cdef array.array arr = array.clone(double_array_template, n, zero=False)
    cdef unsigned i
    for i in range(n):
        arr.data.as_doubles[i] = init_value

    return arr

cdef inline array.array ialloc(unsigned n, int init_value = 0):
    """
    Allocate a contiguous array of n integers.
    Return the array.
    """
    cdef array.array arr = array.clone(int_array_template, n, zero=(init_value==0))
    cdef unsigned i
    if init_value != 0:
        for i in range(n):
            arr.data.as_ints[i] = init_value # XXX Use memset ?

    return arr

cdef inline array.array balloc(unsigned n, char init_value = 0):
    """
    Allocate a contiguous array of n bytes.
    Return the array.
    """
    cdef array.array arr = array.clone(byte_array_template, n, zero=(init_value==0))
    cdef unsigned i
    if init_value != 0:
        for i in range(n):
            arr.data.as_ints[i] = init_value # XXX Use memset ?

    return arr

# ======================================================================
# Vectorized operations
# ======================================================================
cdef void vrand(unsigned n, double* buffer):
    """ Fill a buffer with random values in the range (0, 1) exclusive.
    """
    cdef unsigned i
    cdef int rnd
    for i in range(n):
        while True:
            rnd = rand() # XXX Replace with https://en.wikipedia.org/wiki/Mersenne_Twister ?
            if rnd != 0 and rnd != RAND_MAX:
                break
        buffer[i] = float(rnd)/float(RAND_MAX)
