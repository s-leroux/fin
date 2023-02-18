import fin.model

class Call(fin.model.Model):
    def __init__(self, params):
        super().__init__(call, (), params)

class Put(fin.model.Model):
    def __init__(self, params):
        super().__init__(put, (), params)

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
    return (0.0 if ap <= ep else (ap-ep)/parity+premium)-tp

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
    return (0.0 if ep <= ap else (ep-ap)/parity+premium)-tp

