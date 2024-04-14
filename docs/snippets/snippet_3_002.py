t2 = t1.select(
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        (fc.sma(5), "Close"),
    )

print(t2)
