from prettytable import PrettyTable
from pathlib import Path

import deepdoctection as dd
analyzer = dd.get_dd_analyzer(config_overwrite=["LANGUAGE='Vietnamese'"])
path = Path.cwd() / "images"

df = analyzer.analyze(path=path)
df.reset_state()  # This method must be called just before starting the iteration. It is part of the API.

doc=iter(df)
page = next(doc)

image = page.viz()
print(page.text)
for layout in page.layouts:
    if layout.category_name=="title": 
        print(f"Title: {layout.text}")

table = page.tables[0]
table.get_attribute_names()

datatable = PrettyTable([])
csv_table = []
for i in table.csv:
    i = [item.replace('|', ' ').strip() for item in i]
    csv_table.append(i)
    datatable.add_row(i)

print(datatable)
print(csv_table)