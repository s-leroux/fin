"""
Evaluate the price of a warrant if the underlying asset changes over a short
time period (in this example, we assume interrest rates and volatility to be constant)

Usage:
    PYTHONPATH="$PWD" python3 examples/fin/model/warrant_price_change.py
"""
from fin.model import option
from fin.seq import table
from fin.seq import algo, expr

NLBNPFR1Y883 = dict(
    s_0=674.186,
    k=700,
    t=25/252,
    r_0=0.04,
    parity=10,
    f_0=5.37,
)
PUT_QTY=75

DE000SU71PW8 = dict(
    s_0=674.186,
    k=740,
    t=25/252,
    r_0=0.04,
    parity=50,
    f_0=0.390,
)
CALL_QTY=240

model_put = option.Warrant.put(NLBNPFR1Y883)
model_call = option.Warrant.call(DE000SU71PW8)
print(f"Implied volatility is {model_put['sigma_0']}")
print(f"Implied volatility is {model_call['sigma_0']}")


tbl = table.table_from_column("PC", [-120, -100, -70, -30, 0, +30, +70, +100, +120])
tbl.add_column("PRICE", (algo.add(), model_put['s_0'], "PC"))
tbl.add_column("PUT", (expr.map(model_put.find('f_0', 's_0')), "PRICE"))
tbl.add_column("CALL", (expr.map(model_call.find('f_0', 's_0')), "PRICE"))
tbl.add_column("PUT VALUE", (algo.mul(), "PUT", PUT_QTY))
tbl.add_column("CALL VALUE", (algo.mul(), "CALL", CALL_QTY))
tbl.add_column("TOTAL", (algo.add(), "PUT VALUE", "CALL VALUE"))
print(tbl)
