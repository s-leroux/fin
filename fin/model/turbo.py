def call(tp,ap,ep,parity,premium):
    """
    Model function for a call Turbo.

    This function evaluates to 0 if the model is at equilibrium given:
    - tp: the current Turbot's price
    - ap: the current asset's price
    - ep: the expected asset's price
    - parity:
    - premium: the issuer's fees (gap prime, precount dividends, ...)
    """
    return (ap-ep)/parity+premium-tp

def put(tp,ap,ep,parity,premium):
    """
    Model function for a put Turbo.

    This function evaluates to 0 if the model is at equilibrium given:
    - tp: the current Turbot's price
    - ap: the current asset's price
    - ep: the expected asset's price
    - parity:
    - premium: the issuer's fees (gap prime, precount dividends, ...)
    """
    return (ep-ap)/parity+premium-tp

