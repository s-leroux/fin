import math

from fin.seq.column import Column

def bss(*, init_funds, init_position=0, short_sales=False, fractional=False, fees=None):
    """ Buy/Sell Simulator.

        This simulator uses two signal lines, _order_ and _price_.
        If _order_ is positive and if there is enought funds, the simulator
        places a buy order. If _order_ is negative, the simulator places a
        sell order for `abs(order)` if _short-sale_ is True, otherwise for
        `min(abs(order), position)`.

        All orders are priced according to the _price_ line.
    """
    def _bss(Serie, orders, prices):
        isnan = math.isnan

        bogus = False
        curr_funds = init_funds
        curr_position = init_position
        funds = []
        positions = []

        for order, price in zip(orders.f_values, prices.f_values):
            if isnan(order) or (order != 0 and isnan(price)):
                bogus = True
                curr_funds = curr_position = None
            
            if not bogus:
                while order > 0:
                    if not fractional:
                        order = int(order)
                        if order < 1:
                            break
                    debit = order*price
                    if fees is not None:
                        debit += fees(True, order, price)
                    if debit > curr_funds:
                        adj_order = curr_funds/price
                        if adj_order >= order:
                            order -= 1
                        else:
                            order = adj_order
                    else:
                        curr_position += order
                        curr_funds -= debit
                        break
                while order < 0:
                    if not fractional:
                        order = int(order)
                        if order > -1:
                            break
                    if not short_sales:
                        if curr_position + order < 0:
                            order = -curr_position
                            if order == 0:
                                break

                        credit = -order*price
                        if fees is not None:
                            credit -= fees(False, -order, price)
                    curr_position += order
                    curr_funds += credit
                    break

            funds.append(curr_funds)
            positions.append(curr_position)

        return (
                Column.from_sequence(funds, name="FUNDS", type="n"),
                Column.from_sequence(positions, name="POSITIONS", type="n"),
            )

    return _bss
