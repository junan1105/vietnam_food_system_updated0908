from docx import Document

path = r"C:\Users\tuana\Documents\Codex\2026-07-21\new-chat\outputs\vietnam_food_system_updated\安嘉之越南美食品在淡水_系統文件書_品質強化版.docx"
doc = Document(path)
for index, table in enumerate(doc.tables, 1):
    print(f"TABLE {index}: {len(table.rows)} rows x {len(table.columns)} cols")
    for row in table.rows:
        print(" | ".join(cell.text.replace("\n", " / ") for cell in row.cells))
