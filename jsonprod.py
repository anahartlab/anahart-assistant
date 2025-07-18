import csv
import json

def csv_to_dict_list(path, fieldnames):
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            item = {field: row.get(field, '').strip() for field in fieldnames}
            data.append(item)
    return data

# Путь к CSV (укажи свои локальные пути)
products_path = "products.csv"
tapestries_path = "tapestriesCatalog.csv"

# Поля, которые хотим в итоговом JSON
fields = ["Name", "Title", "Description", "Stock", "Price", "Link"]

products = csv_to_dict_list(products_path, fields)
tapestries = csv_to_dict_list(tapestries_path, fields)

combined = products + tapestries

# Преобразуем поля к нужному виду (пример)
output = []
for item in combined:
    output.append({
        "name": item["Name"],
        "title": item["Title"],
        "description": item["Description"],
        "stock": item["Stock"],
        "price": item["Price"],
        "link": item["Link"]
    })

# Запись в JSON (перезапишет существующий файл)
with open("products.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ Создан файл products.json с {len(output)} товарами")