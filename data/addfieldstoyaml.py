import yaml

with open('data/Meine_Buchliste.yaml', encoding='utf-8') as f:
    data = yaml.safe_load(f)

for book in data['books']:
    book['book_color'] = "#4E4B4B"

with open('data/Meine_Buchliste.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)