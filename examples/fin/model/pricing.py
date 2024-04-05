"""
Evaluates a position size, stop price and take profit from a maximum loss
and entry price.

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/model/pricing.py
"""
from fin.model.complexmodel import ComplexModel

UNKNOWN = (0, 1000)
ENTRY_PRICE = 100.0
STOP_PRICE = 90
TAKE_PROFIT = UNKNOWN
MAX_LOSS = 50

model = ComplexModel()
eq1 = model.register(
        lambda entry, stop, qty, maxloss : (entry-stop)*qty - maxloss,
        dict(name="entry", description="Entry price", domain=ENTRY_PRICE),
        dict(name="stop", description="Stop price", domain=STOP_PRICE),
        dict(name="qty", description="Quantity", domain=(0,1000)),
        dict(name="maxloss", description="Maximum loss", domain=MAX_LOSS),
    )
eq2 = model.register(
        lambda entry, stop, tp : (entry-stop)*2.0025 - (tp-entry),
        dict(name="entry", description="Entry price", domain=ENTRY_PRICE),
        dict(name="stop", description="Stop price", domain=STOP_PRICE),
        dict(name="tp", description="Take profit", domain=TAKE_PROFIT),
    )

model.bind(eq1, "entry", eq2, "entry")
model.bind(eq1, "stop", eq2, "stop")

params, domains, eqs = model.export()

from fin.model.solvers import ParticleSwarmSolver
solver = ParticleSwarmSolver()
score, result = solver.solve(domains, eqs)

print(f"Score {score}")
for param, value in zip(params, result):
    print(f"{param['description']:20s}: {value}")
