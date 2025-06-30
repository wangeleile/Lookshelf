import yaml
import re
from datetime import datetime

# Mapping von Feldern aus der alten YAML zu den neuen Keys
FIELD_MAP = {
    'Titel': 'title',
    'Author': 'author',
    'My Rating': 'my_rating',
    'Average Rating': 'rating',
    'Bookshelves': 'bookshelf',
    'Serie': 'Series',
    'Serien Nr.': 'Serie no',
    'ISBN Combined': 'isbn',
    'Book Id': 'id',
    'Publisher': 'publisher',
    'Number of Pages': 'pages',
    'Year Published': 'year',
    'Original Publication Year': 'original_year',
    'Date Read': 'date_read',
    'Date Added': 'date_added',
    'PublishedDate': 'publication_date',
    'PageCount': 'pages',
    'Categories': 'Categories',
    'Description': 'Description',
    'ImageURL': 'image_url',
    'Private Notes': 'Private_Notes',
    'My Review': 'My_Review',
    'Binding': 'binding',
    'Read Count': 'read_count',
    'Average Rating': 'rating',
}

# Hilfsfunktion für numerische Felder
FLOAT_FIELDS = ['rating', 'my_rating']
INT_FIELDS = ['pages', 'year', 'rating_count']

# Hilfsfunktion für boolesche Felder
BOOL_FIELDS = ['bestseller']

# Felder, die im Ziel immer enthalten sein sollen
TARGET_FIELDS = [
    'id', 'gender', 'title', 'author', 'genre', 'year', 'type', 'pages', 'duration', 'rating', 'rating_count',
    'publisher', 'publication_date', 'image_url', 'bestseller', 'language', 'year_asc', 'year_desc',
    'rating_asc', 'rating_desc', 'Description', 'Private_Notes', 'My_Review', 'date_added', 'date_read',
    'bookshelf', 'Series', 'Serie no', 'Categories'
]

def parse_entry(entry):
    out = {}
    for k, v in entry.items():
        key = k.strip().replace(':', '')
        key = FIELD_MAP.get(key, key)
        if isinstance(v, str):
            v = v.strip()
        # Typkonvertierung
        if key in FLOAT_FIELDS:
            try:
                out[key] = float(v.replace(',', '.')) if v else None
            except Exception:
                out[key] = None
        elif key in INT_FIELDS:
            try:
                out[key] = int(v) if v else None
            except Exception:
                out[key] = None
        else:
            out[key] = v
    # id als String
    if 'id' in out:
        out['id'] = str(out['id'])
    # year_asc, year_desc, rating_asc, rating_desc
    if 'year' in out and out['year']:
        try:
            out['year_asc'] = int(out['year'])
            out['year_desc'] = -int(out['year'])
        except Exception:
            out['year_asc'] = out['year_desc'] = None
    if 'rating' in out and out['rating']:
        try:
            out['rating_asc'] = float(out['rating'])
            out['rating_desc'] = -float(out['rating'])
        except Exception:
            out['rating_asc'] = out['rating_desc'] = None
    # Standardwerte
    out.setdefault('bestseller', False)
    out.setdefault('language', 'German')
    # Typ (Buch/Audiobook)
    if 'binding' in out and out['binding']:
        if 'audio' in out['binding'].lower():
            out['type'] = 'audiobook'
        else:
            out['type'] = 'book'
    else:
        out['type'] = 'book'
    # genre heuristisch
    if 'Categories' in out and out['Categories']:
        if 'fiction' in out['Categories'].lower():
            out['genre'] = 'Fiction'
        else:
            out['genre'] = 'Nonfiction'
    else:
        out['genre'] = 'Fiction'
    # gender heuristisch (optional, kann manuell ergänzt werden)
    out.setdefault('gender', '')
    # rating_count (nicht vorhanden, auf 0 setzen)
    out.setdefault('rating_count', 0)
    # duration (falls vorhanden)
    if 'duration' not in out:
        out['duration'] = ''
    # Felder sortieren und leere Felder auffüllen
    for f in TARGET_FIELDS:
        out.setdefault(f, '')
    return out

def main():
    with open('data/Meine_Buchliste.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    books = [parse_entry(entry) for entry in data]
    # Schreibe als Liste von Objekten (ohne books: -Key)
    with open('data/Meine_Buchliste_converted.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(books, f, allow_unicode=True, sort_keys=False)

if __name__ == '__main__':
    main()
