from fin.model import Model
from fin.utils import tabular

import math
import fin.math

# ======================================================================
# Interest rates
# ======================================================================
def continuous_compounding(rm, m=1, *, log1p=math.log1p):
    """
    Convert from discrete compounding rates to continuous compounding
    interest rates.
    
    ``rm`` is the per annum compounding rate. ``m`` is the compounding
    frequency expressed as 1/year.
    """
    try:
        return m*log1p(rm/m)
    except ZeroDivisionError:
        return 0.00

def discrete_compounding(rc, m=1, exp=math.exp, *, infinity=float("inf")):
    """
    Convert from continuous compounding rates to discrete compounding
    interest rates.
    
    ``rc`` is the continuous compounding rate. ``m`` is the compounding
    frequency expressed as 1/year.
    """
    try:
        return m*(exp(rc/m)-1)
    except (ZeroDivisionError, OverflowError):
        return infinity

Rates = fin.model.Model(
    lambda rc, rm, m : continuous_compounding(rm, m) - rc,
    rc = dict(
        value=continuous_compounding,
        description="Continuous compounding rate per period",
        formatter=tabular.PercentFormatter(),
    ),
    rm = dict(
        value=discrete_compounding,
        description="Discrete compounding rate per period",
        formatter=tabular.PercentFormatter(),
    ),
    m = dict(
        value=(.001, 1000),
        description="Coupons per period",
    ),
)

ExpectedReturn = fin.model.Model(
    lambda amount, expected, rate, duration, m : (amount*(1+rate/m)**(m*duration)) - expected,
    m = dict(
        value=(.001, 1000),
    ),
    rate = dict(
        value=(0.00, 1000),
    )
)
