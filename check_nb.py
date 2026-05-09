import json
nb = json.load(open("Codes/C00_all_collection.ipynb"))
cells = nb["cells"]
print("Total cells:", len(cells))
for i, c in enumerate(cells[:20]):
    src = "".join(c["source"])[:100].replace("\n", " ")
    ct = c["cell_type"]
    print(f"Cell {i+1} [{ct}]: {src}")
