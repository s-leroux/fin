from collections import defaultdict

def ptree(fct, n, asset_price, asset_price_changes):
    """
    Evaluate the possible outcomes for a product if the underlying asset's price
    changes in a similar manner over n periods.
    """
    def eval(x):
        return (fct(x), x)

    # Map price changes to prop changes:
    price_changes = [ (prob, price/asset_price) for prob, price in asset_price_changes ]
    identity = [ [ 1.0, 1.0 ] ]

    result = { eval(asset_price): 1.0 }
    cache = {}

    while n > 0:
        current = defaultdict(float)
        for (current_product_price, current_asset_price), current_prob in result.items():
            if current_product_price == 0.0:
                changeset = identity
            else:
                changeset = price_changes

            for prob_change, price_change in changeset:
                new_asset_price = current_asset_price * price_change
                new_prob = current_prob * prob_change

                key = cache.get(new_asset_price)
                if key is None:
                    key = cache[new_asset_price] = eval(new_asset_price)
                
                current[key] += new_prob

        n -= 1
        result = current

    # Map the dictionary to a sorted list
    result = [(a,b,c) for (a,b),c in result.items()]
    result.sort()
    return result
