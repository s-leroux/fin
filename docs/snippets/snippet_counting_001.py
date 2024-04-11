from fin.api import yf
from fin.datetime import CalendarDateDelta, CalendarDate
from fin.seq import fc
from fin.seq import ag

client = yf.Client()

quote = client.historical_data("BTC-USD", CalendarDateDelta(years=1), CalendarDate(2024, 4, 8))
print("Average number of consecutive days BTC closes below its SMA50D")
print("See https://github.com/s-leroux/fin/issues/27")
print(
    quote["Close"].extend(
        (fc.named("Sma"), fc.sma(50), "Close"),
        (fc.named("Comp"), fc.lt, "Close", "Sma"),
    ).group_by(
        "Comp",
        (ag.first, "Date"),
        (ag.first, "Comp"), # XXX <--- Should this be implied?
        (ag.count, fc.named("Count"), "Comp"),
    ).where(
        "Comp",
    ).group_by(
        "Comp",
        (ag.first, "Date"),
        (ag.avg, fc.named("Avg"), "Count"),
    )
)
