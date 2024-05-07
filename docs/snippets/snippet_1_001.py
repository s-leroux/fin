from fin.api import yf
from fin.datetime import CalendarDateDelta, CalendarDate

client = yf.Client()

t = client.historical_data("TSLA", CalendarDateDelta(days=5), CalendarDate(2023, 7, 20), precision=2)
print(t)
