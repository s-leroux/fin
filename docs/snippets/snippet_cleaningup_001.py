from fin.api.yf import Client
from fin.seq import fc

ticker = "^FCHI"
end_date = "2024-05-14"
duration = dict(years=5)

client = Client()
data = client.historical_data(ticker, duration, end_date, precision=2)

print(data)
