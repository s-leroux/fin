# Cleaning up data:

Yahoo! Finance data are readily available.
Unfortunately, these data are often dirty.

Here is an example:

```
from fin.api.yf import Client
from fin.seq import fc

ticker = "^FCHI"
end_date = "2024-05-14"
duration = dict(years=5)

client = Client()
data = client.historical_data(ticker, duration, end_date)

print(data)
```

At the time of writing, we can identify two types of anomalies in the data. First, some rows are unavailable:
The original data contained _"null"_ values, loaded as `None`.
Then, the volume is missing for some dates.
Here, the missing data are set to _0_.

```
      Date | Open        | High        |  Low        | Close       | Adj Close   |    Volume
---------- | ----------- | ----------- | ----------- | ----------- | ----------- | ---------
2019-12-23 | 6013.560059 | 6035.950195 | 6005.959961 | 6029.370117 | 6029.370117 |  46603900
2019-12-24 | 6027.189941 | 6033.990234 | 6025.620117 | 6029.549805 | 6029.549805 |  12440900
2019-12-25 | None        | None        | None        | None        | None        |      None
2019-12-27 | 6039.950195 | 6065.000000 | 6027.720215 | 6037.390137 | 6037.390137 |  47289800
2019-12-30 | 6028.959961 | 6037.700195 | 5982.220215 | 5982.220215 | 5982.220215 |  40318700
2019-12-31 | 5970.589844 | 5987.220215 | 5958.250000 | 5978.060059 | 5978.060059 |  20670000
...
2020-12-18 | 5533.779785 | 5581.959961 | 5519.169922 | 5527.839844 | 5527.839844 | 173234900
2020-12-21 | 5392.549805 | 5422.100098 | 5306.580078 | 5393.339844 | 5393.339844 | 122849400
2020-12-22 | 5411.149902 | 5477.870117 | 5411.149902 | 5466.859863 | 5466.859863 |         0
2020-12-23 | 5472.140137 | 5539.160156 | 5472.029785 | 5527.589844 | 5527.589844 |  59208500
2020-12-24 | 5542.490234 | 5545.709961 | 5517.009766 | 5522.009766 | 5522.009766 |         0
2020-12-28 | 5562.040039 | 5601.000000 | 5547.899902 | 5588.379883 | 5588.379883 |  44706900
2020-12-29 | 5610.129883 | 5625.520020 | 5603.740234 | 5611.790039 | 5611.790039 |         0
2020-12-30 | 5603.720215 | 5625.600098 | 5594.109863 | 5599.410156 | 5599.410156 |  35280300
2020-12-31 | 5573.200195 | 5598.930176 | 5551.410156 | 5551.410156 | 5551.410156 |         0
2021-01-04 | 5614.040039 | 5656.419922 | 5567.970215 | 5588.959961 | 5588.959961 |  82741000
2021-01-05 | 5561.600098 | 5603.660156 | 5530.479980 | 5564.600098 | 5564.600098 |  79263400
2021-01-06 | 5601.009766 | 5648.419922 | 5553.390137 | 5630.600098 | 5630.600098 | 116286300
```

## Removing _undefined_ data

We can leverage the `fc:all` predicate to remove the rows with missing price data.
The `fc:all` predicate evaluates to `True` when all its parameters are `True`.
Floating point values implicitly convert to `True` if they are defined and not zero.
Other possible outcomes are `False` (for 0.0) or `None` (for _NaN_).
Since prices cannot be equal to 0.0, it is a good filter to remove rows containing undefined data:

```
data = data.where(
        (fc.all, "Open", "High", "Low", "Close", "Adj Close"),
    )
```

```
2019-12-23 | 6013.560059 | 6035.950195 | 6005.959961 | 6029.370117 | 6029.370117 |  46603900
2019-12-24 | 6027.189941 | 6033.990234 | 6025.620117 | 6029.549805 | 6029.549805 |  12440900
2019-12-27 | 6039.950195 | 6065.000000 | 6027.720215 | 6037.390137 | 6037.390137 |  47289800
2019-12-30 | 6028.959961 | 6037.700195 | 5982.220215 | 5982.220215 | 5982.220215 |  40318700
```

## Filtering out rows with zero volume

Here again, we will benefit from the implicit conversion to ternary logical values.
The `0` integer value converts to the `False` value.
Any other integer converts to `True`.
Let's rewrite our `where` condition:

```
data = data.where(
        (fc.all, "Open", "High", "Low", "Close", "Adj Close"),
        "Volume",
    )
print(data)
```

```
2019-12-20 | 5979.529785 | 6024.169922 | 5966.879883 | 6021.529785 | 6021.529785 | 151362500
2019-12-23 | 6013.560059 | 6035.950195 | 6005.959961 | 6029.370117 | 6029.370117 |  46603900
2019-12-24 | 6027.189941 | 6033.990234 | 6025.620117 | 6029.549805 | 6029.549805 |  12440900
2019-12-27 | 6039.950195 | 6065.000000 | 6027.720215 | 6037.390137 | 6037.390137 |  47289800
2019-12-30 | 6028.959961 | 6037.700195 | 5982.220215 | 5982.220215 | 5982.220215 |  40318700
...
2020-12-18 | 5533.779785 | 5581.959961 | 5519.169922 | 5527.839844 | 5527.839844 | 173234900
2020-12-21 | 5392.549805 | 5422.100098 | 5306.580078 | 5393.339844 | 5393.339844 | 122849400
2020-12-23 | 5472.140137 | 5539.160156 | 5472.029785 | 5527.589844 | 5527.589844 |  59208500
2020-12-28 | 5562.040039 | 5601.000000 | 5547.899902 | 5588.379883 | 5588.379883 |  44706900
2020-12-30 | 5603.720215 | 5625.600098 | 5594.109863 | 5599.410156 | 5599.410156 |  35280300
2021-01-04 | 5614.040039 | 5656.419922 | 5567.970215 | 5588.959961 | 5588.959961 |  82741000
2021-01-05 | 5561.600098 | 5603.660156 | 5530.479980 | 5564.600098 | 5564.600098 |  79263400
2021-01-06 | 5601.009766 | 5648.419922 | 5553.390137 | 5630.600098 | 5630.600098 | 116286300
```


