# Simulation and strategy backtesting:

The `fin.seq` package contains a basic buy/sell simulator to backtest your strategies.

Here is a basic example, taken from `examples/fin/seq/backtesting.py`
```
from fin.seq.serie import Serie
from fin.seq import fc

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
        (fc.bss(init_funds=1000), "ORDER", "Close"),
        (fc.named("BALANCE"), fc.add, "FUNDS", fc.mul, "POSITIONS", "Close"),
    )
print(ser)
```
I assume you are familiar with the basic usage of series expressions. The most important job here occurs in the `extend(...)` clause.
There, we create two signal columns, `S1` and `S2`, each containing a three-state logical value `True`, `False`, or `None`, depending on whether the fast SMA is above or below the slow SMA.

From those two signals, we build an `ORDER` column representing the orders we'd like to pass depending on the indicators.
To simplify things in that example, I systematically pass orders in 1000 shares batches. `+1000` means I'm buying, and `-1000` means selling. The simulator `fc.bss` will adjust the orders' size to the available funds/shares and will produce two new columns: `FUNDS` and `POSITION`:

```
sh$ python3 < examples/fin/seq/backtesting.py | sed -n -e '1,2p
' -e '737,$p'
      Date |  RC | Close  | SMA F… | SMA S… |    S1 |    S2 | ORDER    | FUNDS   | POS… | BALANCE
---------- | --- | ------ | ------ | ------ | ----- | ----- | -------- | ------- | ---- | -------
2022-12-01 | 734 | 273.40 | 273.10 | 273.74 | False |  True | -1000.00 | 1187.38 | 0.00 | 1187.38
2022-12-02 | 735 | 273.40 | 272.78 | 273.76 | False |  True | -1000.00 | 1187.38 | 0.00 | 1187.38
2022-12-05 | 736 | 271.59 | 272.52 | 273.61 | False |  True | -1000.00 | 1187.38 | 0.00 | 1187.38
2022-12-06 | 737 | 271.77 | 272.59 | 273.38 | False |  True | -1000.00 | 1187.38 | 0.00 | 1187.38
2022-12-07 | 738 | 270.34 | 272.10 | 272.98 | False |  True | -1000.00 | 1187.38 | 0.00 | 1187.38
2022-12-08 | 739 | 273.39 | 272.10 | 272.76 | False |  True | -1000.00 | 1187.38 | 0.00 | 1187.38
2022-12-09 | 740 | 272.04 | 271.83 | 272.56 | False |  True | -1000.00 | 1187.38 | 0.00 | 1187.38
2022-12-12 | 741 | 276.62 | 272.83 | 272.83 |  True | False |  1000.00 |   80.90 | 4.00 | 1187.38
2022-12-13 | 742 | 274.28 | 273.33 | 272.93 |  True | False |  1000.00 |   80.90 | 4.00 | 1178.02
2022-12-14 | 743 | 274.53 | 274.17 | 273.26 |  True | False |  1000.00 |   80.90 | 4.00 | 1179.02
2022-12-15 | 744 | 271.73 | 273.84 | 273.22 |  True | False |  1000.00 |   80.90 | 4.00 | 1167.82
2022-12-16 | 745 | 266.12 | 272.66 | 272.86 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-19 | 746 | 265.83 | 270.50 | 272.48 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-20 | 747 | 267.25 | 269.09 | 272.12 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-21 | 748 | 268.16 | 267.82 | 271.79 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-22 | 749 | 265.77 | 266.63 | 271.41 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-23 | 750 | 267.57 | 266.92 | 271.04 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-27 | 751 | 266.84 | 267.12 | 270.74 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-28 | 752 | 265.11 | 266.69 | 270.43 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-29 | 753 | 265.93 | 266.24 | 270.08 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2022-12-30 | 754 | 263.53 | 265.80 | 269.59 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
2023-01-03 | 755 | 264.33 | 265.15 | 269.14 | False |  True | -1000.00 | 1145.38 | 0.00 | 1145.38
```
As you can see, this strategy increased our funds from 1000 to 1145.38, _ignoring the transaction fees_.

Let's add some fixed fees. It requires adding a function to calculate the fees and passing that function to `fc:bss`:

```
def fees(direction, qty, price):
    # we pay 1¤ fees for each transaction
    return 1
```
```
        (fc.bss(init_funds=1000, fees=fees), "ORDER", "Close"),
```

Now, the result is a bit different:

```
python3 < docs/snippets/snippet_simul_fees_001.py | tail -1
2023-01-03 | 755 | 264.33 | 265.15 | 269.14 | False |  True | -1000.00 | 1103.05 | 0.00 | 1103.05
```
