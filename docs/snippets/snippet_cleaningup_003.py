data = data.where(
        (fc.all, "Open", "High", "Low", "Close", "Adj Close"),
        "Volume",
    )
print(data)

