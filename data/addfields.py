import yaml

input_file = "data/Meine_Buchliste.yaml"
output_file = "data/Meine_Buchliste_out.yaml"

def parse_float(val):
    try:
        return float(str(val).replace(",", "."))
    except Exception:
        return None

def fill_empty_fields(entry):
    for key, value in entry.items():
        if value is None or (isinstance(value, str) and value.strip() == ""):
            entry[key] = ""
    return entry

with open(input_file, encoding="utf-8") as f:
    data = yaml.safe_load(f)

for entry in data:
    # Leere Felder auffüllen
    fill_empty_fields(entry)
    # year_asc und year_desc
    year = entry.get("year") or entry.get("Year Published")
    try:
        year_int = int(str(year).strip())
    except Exception:
        year_int = None
    if year_int is not None:
        entry["year_asc"] = year_int
        entry["year_desc"] = -year_int
    # rating_asc und rating_desc
    rating = entry.get("Average Rating")
    rating_val = parse_float(rating)
    if rating_val is not None:
        entry["rating_asc"] = rating_val
        entry["rating_desc"] = -rating_val

with open(output_file, "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)