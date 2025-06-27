import csv
import yaml

input_csv = r"data/Meine_Buchliste.csv"
output_yaml = r"data/Meine_Buchliste.yaml"

with open(input_csv, encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    rows = list(reader)

with open(output_yaml, "w", encoding="utf-8") as yamlfile:
    yaml.dump(rows, yamlfile, allow_unicode=True, sort_keys=False, width=120)

print(f"Converted {input_csv} to {output_yaml}")