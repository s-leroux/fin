import fin.model

import math
import fin.math


def call(k, t, s_0, sigma_0, r_0, c_0, *, sqrt=math.sqrt, log=math.log, exp=math.exp, cdf=fin.math.cdf):
    """
    Model function using the Black-Scholes formula to price call options.

    This function evaluates to 0 if the model is at equilibrium given:
    - k: Strike price
    - t: Time until expiration
    - s_0: Underlying asset price on the valuation date
    - sigma_0: Underlying asset volatility on the valuation date
    - r_0: Continuously compounded risk-free interest rate on the valuation date
    - c_0: Long call value
    """
    v = sigma_0*sqrt(t)
    d1 = (log(s_0/k)+(r_0+sigma_0*sigma_0/2)*t)
    try:
        d1 /= v
    except ZeroDivisionError:
        d1 *= float("inf")
    d2 = d1 - v

    return c_0-(s_0*cdf(d1)-k*exp(-r_0*t)*cdf(d2))

def put(k, t, s_0, sigma_0, r_0, p_0, *, sqrt=math.sqrt, log=math.log, exp=math.exp, cdf=fin.math.cdf):
    """
    Model function using the Black-Scholes formula to price put options.

    This function evaluates to 0 if the model is at equilibrium given:
    - k: Strike price
    - t: Time until expiration
    - s_0: Underlying asset price on the valuation date
    - sigma_0: Underlying asset volatility on the valuation date
    - r_0: Continuously compounded risk-free interest rate on the valuation date
    - p_0: Long put value
    """
    v = sigma_0*sqrt(t)
    d1 = (log(s_0/k)+(r_0+sigma_0*sigma_0/2)*t)
    try:
        d1 /= v
    except ZeroDivisionError:
        d1 *= float("inf")
    d2 = d1 - v

    return p_0+(s_0*cdf(-d1)-k*exp(-r_0*t)*cdf(-d2))

def simple_binomial_tree_call(k, t, s_0, s_u, s_d, r_0, f_n, *, exp=math.exp):
    """
    Model for option pricing using a simple (one step) binomial tree.

    This function evaluates to 0 if the model is at equilibrium given:
    - k: Strike price
    - t: Time until expiration
    - s_0: Underlying asset price on the valuation date
    - s_u: Underlying asset price at expiration if the price rises
    - s_d: Underlying asset price at expiration if the price falls
    - r_0: Continuously compounded risk-free interest rate on the valuation date
    - f_0: Option price at expiration
    """
    c_0 = s_u - k # Must be > 0 !
    delta = c_0 / (s_u - s_d)
    fv = s_d*delta # future value of a portfolio of -1 call and delta shares
    pv = fv*exp(-r_0*t) # present value of the same portfolio
    f = delta*s_0-pv

    return f-f_n

class SimpleBinomialTree:
    call = fin.model.Model(simple_binomial_tree_call, ())



Call = fin.model.Model(call, ())
Put = fin.model.Model(put, ())
