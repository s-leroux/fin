from fin.seq.serie import Serie
from fin.seq import fc

def fees(direction, qty, price):
    return 1

ser = Serie.from_csv_file(
        "tests/_fixtures/MCD-20200103-20230103.csv",
        format="dnnnnni"
    ).select(
        "Date",
        (fc.named("RC"), fc.rownum),
        "Close",
    ).extend(
        (fc.named("SMA FAST"), fc.sma(5), "Close"),
        (fc.named("SMA SLOW"), fc.sma(20), "Close"),
        (fc.named("S1"), fc.gt, "SMA FAST", "SMA SLOW"),
        (fc.named("S2"), fc.lt, "SMA FAST", "SMA SLOW"),
        (fc.named("ORDER"),
            fc.mul,
            (fc.coalesce, (fc.sub, "S1", "S2"), fc.constant(0)),
            fc.constant(1000)
        ),
        (fc.bss(init_funds=1000, fees=fees), "ORDER", "Close"),
        (fc.named("BALANCE"), fc.add, "FUNDS", fc.mul, "POSITIONS", "Close"),
    )
print(ser)
