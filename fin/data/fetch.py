"""
Fetch data and populates the _data files.
"""
import os
import json
from pprint import pprint
from fin.api import investing

def main():
    indices = (
            # https://www.investing.com terminology
            # "nasdaq-composite",
            "france-40",
            )

    dir_name = os.path.dirname(__file__)
    for index in indices:
        it = investing.Index(index)
        it.fetch()
        record = it._data.copy()
        record["components"] = []
        for component in it.components:
            component.fetch()
            record["components"].append(component._data)

        file_name = os.path.join(dir_name, f"_{index}.json")
        with open(file_name, "wt") as f:
            json.dump(record, f, indent=4)

if __name__ == "__main__":
    main()
