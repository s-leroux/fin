import fin.model

import math
import fin.math

def ProportionalFees(rate, minimum=0):
    return lambda amount : max(amount*rate, minimum)

def FixedFees(f):
    return lambda amount: f

def BDFees(amount):
    if amount <= 500:
        return 0.99
    if amount <= 1000:
        return 1.90
    if amount <= 2000:
        return 2.90
    if amount <= 4400:
        return 3.80
    return 0.0009*amount

def MSFees(amount):
    if amount < 500:
        return 2.50

    return 0.00

def _breakeven_eq(qty, s0, s1, _fees):
    """
    Model a simple buy/sell process involving some fees.

    This function evaluates to 0 if the model is at equilibrium given:
    - s0: Underlying asset price when buying
    - s1: Underlying asset price when selling
    - qty: purchase quantity
    """
    debit = s0*qty
    debit += _fees(debit)
    credit = s1*qty
    credit -= _fees(credit)

    return credit-debit

class Breakeven(fin.model.Model(_breakeven_eq, ())):
    def __init__(self, fees_fct, values):
        values = values.copy()
        self._fees_fct = values['_fees'] = fees_fct

        super().__init__(values)

    def clone(self, new_values):
        return type(self)(self._fees_fct, new_values)

def _profit_loss_eq(qty, s0, s1, pl, _fees):
    """
    Model a simple buy/sell process involving some fees.

    This function evaluates to 0 if the model is at equilibrium given:
    - s0: Underlying asset price when buying
    - s1: Underlying asset price when selling
    - qty: purchase quantity
    - pl: profit/loss
    """
    debit = s0*qty
    debit += _fees(debit)
    credit = s1*qty
    credit -= _fees(credit)

    return credit-debit-pl

class ProfitLoss(fin.model.Model(_profit_loss_eq, ())):
    def __init__(self, fees_fct, params):
        values = values.copy()
        self._fees_fct = values['_fees'] = fees_fct

        super().__init__(values)

    def clone(self, new_values):
        return type(self)(self._fees_fct, new_values)
