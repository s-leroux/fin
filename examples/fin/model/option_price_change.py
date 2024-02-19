"""
Evaluate the price of an option if the underlying asset changes over a short
time period (in this example, we assume interrest rates and volatility to be constant)

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/model/option_price_change.py
"""
from fin.model import option


CALL_PRICE=1.875
STRIKE=20
MATURITY=0.25
RISK_FREE_RATE=0.10
ASSET_PRICE=21

present_state = option.Call(dict(
    c_0=CALL_PRICE,
    k=STRIKE,
    t=MATURITY,
    s_0=ASSET_PRICE,
    r_0=RISK_FREE_RATE,
))

print(present_state)

sigma = present_state['sigma_0']

PRICE_CHANGE = 70

future_state = option.Call(dict(
    k=STRIKE,
    t=MATURITY,
    s_0=ASSET_PRICE+PRICE_CHANGE,
    r_0=RISK_FREE_RATE,
    sigma_0 = sigma,
))

print(f"Implied volatility is {sigma}")
print(f"If price change by {PRICE_CHANGE} over a short period of time")
print(f"The option price will go from {present_state['c_0']} to {future_state['c_0']}")
print("----")

TIME_TO_MATURITY=1/12
RISK_FREE_RATE=0.08
ASSET_PRICE=40
ASSET_PRICE_UP=42
ASSET_PRICE_DOWN=38
STRIKE=39

call_option_model = option.SimpleBinomialTree.call(dict(
    k=STRIKE,
    t=TIME_TO_MATURITY,
    s_0=ASSET_PRICE,
    s_u=ASSET_PRICE_UP,
    s_d=ASSET_PRICE_DOWN,
    r_0=RISK_FREE_RATE,
))

print(f"Price of option at expiration will be {call_option_model['f_n']}")
print("----")

TIME_TO_MATURITY=25/252
RISK_FREE_RATE=0.04
ASSET_PRICE=726.30
ASSET_PRICE_UP=796.30
ASSET_PRICE_DOWN=656.30
STRIKE=740

call_option_model = option.SimpleBinomialTree.call(dict(
    k=STRIKE,
    t=TIME_TO_MATURITY,
    s_0=ASSET_PRICE,
    s_u=ASSET_PRICE_UP,
    s_d=ASSET_PRICE_DOWN,
    r_0=RISK_FREE_RATE,
))

print(f"Price of option at expiration will be {call_option_model['f_n']}")
print("----")

