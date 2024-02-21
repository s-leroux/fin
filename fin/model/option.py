import fin.model

import math
import fin.math


def call(k, t, s_0, sigma_0, r_0, f_0, *, sqrt=math.sqrt, log=math.log, exp=math.exp, cdf=fin.math.cdf):
    """
    Model function using the Black-Scholes formula to price call options.

    This function evaluates to 0 if the model is at equilibrium given:
    - k: Strike price
    - t: Time until expiration
    - s_0: Underlying asset price on the valuation date
    - sigma_0: Underlying asset volatility on the valuation date
    - r_0: Continuously compounded risk-free interest rate on the valuation date
    - f_0: Long call value
    """
    return f_0-fin.math.bsm_call(s_0, k, t, r_0, sigma_0)

def put(k, t, s_0, sigma_0, r_0, f_0, *, sqrt=math.sqrt, log=math.log, exp=math.exp, cdf=fin.math.cdf):
    """
    Model function using the Black-Scholes formula to price put options.

    This function evaluates to 0 if the model is at equilibrium given:
    - k: Strike price
    - t: Time until expiration
    - s_0: Underlying asset price on the valuation date
    - sigma_0: Underlying asset volatility on the valuation date
    - r_0: Continuously compounded risk-free interest rate on the valuation date
    - f_0: Long put value
    """
    return f_0-fin.math.bsm_put(s_0, k, t, r_0, sigma_0)

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

def call_parity(s_0, k, t, r_0, sigma_0, parity, f_0):
    return f_0 - fin.math.bsm_call_parity(s_0, k, t, r_0, sigma_0, parity)

def put_parity(s_0, k, t, r_0, sigma_0, parity, f_0):
    return f_0 - fin.math.bsm_put_parity(s_0, k, t, r_0, sigma_0, parity)

class SimpleBinomialTree:
    call = fin.model.Model(simple_binomial_tree_call, ())

class Warrant:
    call = fin.model.Model(call_parity, ())
    put = fin.model.Model(put_parity, ())


Call = fin.model.Model(call, ())
Put = fin.model.Model(put, ())
