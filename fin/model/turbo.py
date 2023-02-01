import fin.math

class Call:
    def __init__(self, params):
        pnames = (
            "tp",
            "ap",
            "ep",
            "parity",
            "premium",
        )

        self._params = {}
        missing = []
        for pname in pnames:
            pvalue = self._params[pname] = params.get(pname)
            if pvalue is None:
                missing.append(pname)

        if len(missing) > 1:
            raise fin.model.Underdefined(missing)

        if len(missing) == 1:
            pname = missing[0]
            self._params[pname] = fin.math.solve(
                    call,
                    pname,
                    fin.math.EPSILON,
                    fin.math.HUGE,
                    self._params
            )

    def __getattr__(self, name):
        return self._params[name]

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

