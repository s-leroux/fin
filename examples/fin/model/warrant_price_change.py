"""
Evaluate the price of a warrant if the underlying asset changes over a short
time period (in this example, we assume interrest rates and volatility to be constant)

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/model/warrant_price_change.py
"""
from fin.model import option

NLBNPFR1Y883 = dict(
    s_0=674.186,
    k=700,
    t=25/252,
    r_0=0.04,
    parity=10,
    f_0=5.37,
)

DE000SU71PW8 = dict(
    s_0=674.186,
    k=740,
    t=25/252,
    r_0=0.04,
    parity=50,
    f_0=0.390,
)

present_state_put = option.Warrant.put(NLBNPFR1Y883)
present_state_call = option.Warrant.call(DE000SU71PW8)
print(f"Implied volatility is {present_state_put['sigma_0']}")
print(f"Implied volatility is {present_state_call['sigma_0']}")

for PRICE_CHANGE in (-70, -30, 0, +30, +70):

    future_state_put = present_state_put.adjust('f_0', dict(s_0=NLBNPFR1Y883['s_0']+PRICE_CHANGE))
    future_state_call = present_state_call.adjust('f_0', dict(s_0=NLBNPFR1Y883['s_0']+PRICE_CHANGE))

    print(f"If price change by {PRICE_CHANGE} over a short period of time")
    print(f"The put option price will go from {present_state_put['f_0']} to {future_state_put['f_0']}")
    print(f"The call option price will go from {present_state_call['f_0']} to {future_state_call['f_0']}")
    print("----")
