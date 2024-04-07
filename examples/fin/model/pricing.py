"""
Evaluate a position size, stop price, and take profit from a maximum loss
and entry price.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/model/pricing.py
"""
from fin.model.complexmodel import ComplexModel

UNKNOWN = (0, 1000)
QTY = UNKNOWN
ENTRY_PRICE = 100.0
STOP_PRICE = 90
TAKE_PROFIT = UNKNOWN
MAX_LOSS = 50

def fees(price):
    return price*0.1/100

def balance(debit, credit):
    return (credit-fees(credit))-(debit+fees(debit))

model = ComplexModel()
eq1 = model.register(
        lambda entry, stop, qty, maxloss : balance(entry*qty, stop*qty) - -maxloss,
        dict(name="entry", description="Entry price", domain=ENTRY_PRICE),
        dict(name="stop", description="Stop price", domain=STOP_PRICE),
        dict(name="qty", description="Quantity", domain=QTY),
        dict(name="maxloss", description="Maximum loss", domain=MAX_LOSS),
    )
eq2 = model.register(
        lambda entry, stop, qty, tp : balance(entry*qty, stop*qty)*2 + balance(entry*qty, tp*qty),
        dict(name="entry", description="Entry price", domain=ENTRY_PRICE),
        dict(name="stop", description="Stop price", domain=STOP_PRICE),
        dict(name="qty", description="Quantity", domain=QTY),
        dict(name="tp", description="Take profit", domain=TAKE_PROFIT),
    )

model.bind(eq1, "entry", eq2, "entry")
model.bind(eq1, "stop", eq2, "stop")
model.bind(eq1, "qty", eq2, "qty")

from fin.model.solvers import ParticleSwarmSolver
solver = ParticleSwarmSolver(5,300)
score, params = model.solve(solver)

print(f"Score {score}")
for name, param in params.items():
    print(f"{param['description']:20s}: {param['value']}")

qty = params["qty"]["value"]
stop = params["stop"]["value"]
entry = params["entry"]["value"]
print(f"{'Real loss':20s}: {-balance(qty*entry, qty*stop):5.2f}")

