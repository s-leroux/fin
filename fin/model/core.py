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

class Breakeven(fin.model.Model):
    def __init__(self, fees_fct, params):
        self._fees_fct = fees_fct
        pnames = (
            "qty",
            "s0",
            "s1",
        )

        def breakeven_model(qty, s0, s1):
            """
            Model a simple buy/sell process involving some fees.

            This function evaluates to 0 if the model is at equilibrium given:
            - s0: Underlying asset price when buying
            - s1: Underlying asset price when selling
            - qty: purchase quantity
            """
            debit = s0*qty
            debit += fees_fct(debit)
            credit = s1*qty
            credit -= fees_fct(credit)

            return credit-debit

        super().__init__(breakeven_model, pnames, params)

    def clone(self, new_params):
        return type(self)(self._fees_fct, new_params)

class ProfitLoss(fin.model.Model):
    def __init__(self, fees_fct, params):
        self._fees_fct = fees_fct
        pnames = (
            "qty",
            "s0",
            "s1",
            "pl",
        )

        def profit_loss_model(qty, s0, s1, pl):
            """
            Model a simple buy/sell process involving some fees.

            This function evaluates to 0 if the model is at equilibrium given:
            - s0: Underlying asset price when buying
            - s1: Underlying asset price when selling
            - qty: purchase quantity
            - pl: profit/loss
            """
            debit = s0*qty
            debit += fees_fct(debit)
            credit = s1*qty
            credit -= fees_fct(credit)

            return credit-debit-pl

        super().__init__(profit_loss_model, pnames, params)

    def clone(self, new_params):
        return type(self)(self._fees_fct, new_params)

