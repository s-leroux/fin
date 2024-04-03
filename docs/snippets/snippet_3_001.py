from fin.api import yf
from fin.seq import fc
from fin.seq import plot

# Use the Yahoo! Finance provider
provider = yf.Client()

t1 = provider.historical_data("BAC", dict(days=100))
