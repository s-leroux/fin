import fin.model

import math
import fin.math

class Call(fin.model.Model):
    def __init__(self, params):
        pnames = (
            "k",
            "t",
            "s_0",
            "sigma_0",
            "r_0",
            "c_0",
        )
        super().__init__(call, pnames, params)

class Put(fin.model.Model):
    def __init__(self, params):
        pnames = (
            "k",
            "t",
            "s_0",
            "sigma_0",
            "r_0",
            "p_0",
        )
        super().__init__(put, pnames, params)

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
