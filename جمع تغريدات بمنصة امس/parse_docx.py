import docx
import json

doc = docx.Document("استمارة-معدلة.docx")
structure = []

for t_idx, table in enumerate(doc.tables):
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            text = cell.text.strip().replace('\n', ' ')
            if text:
                structure.append({"table": t_idx, "row": r_idx, "col": c_idx, "text": text})

with open("scratch/docx_structure.json", "w", encoding="utf-8") as f:
    json.dump(structure, f, ensure_ascii=False, indent=2)

print("Done. Saved to scratch/docx_structure.json")
