from bs4 import BeautifulSoup

def parse(fragment):
    """
    Parse a table statement as a python object.
    """
    tbody = fragment.find("tbody")
    if tbody is None:
        tbody = fragment


    py_body = []
    for tr in tbody.find_all("tr"):
        py_row = []
        for titem in tr.find_all(("th", "td")):
            py_row.append(titem.get_text(strip=True))

        py_body.append(py_row)


    return py_body
