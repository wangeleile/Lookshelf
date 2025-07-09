import requests
import yaml

def get_book_data_by_isbn(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    resp = requests.get(url)
    data = resp.json()
    return data.get(f"ISBN:{isbn}")

def is_english_book(book_data):
    if not book_data:
        return False
    languages = book_data.get('languages', [])
    for lang in languages:
        if lang.get('key') == '/languages/eng':
            return True
    return False

def find_german_translation(book_data):
    works = book_data.get('works', [])
    if not works:
        return None
    work_key = works[0].get('key')
    url = f"https://openlibrary.org{work_key}/editions.json"
    resp = requests.get(url)
    editions = resp.json().get('entries', [])
    for edition in editions:
        languages = edition.get('languages', [])
        for lang in languages:
            if lang.get('key') == '/languages/ger':
                return edition
    return None

def get_goodreads_id(isbn):
    # Platzhalter, da Goodreads-API nicht frei verfügbar
    return "GOODREADS_ID_PLACEHOLDER"

def process_buchliste(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for book in data.get("books", []):
        print(f"Processing book: {book.get('title')}")
        isbn = book.get("isbn")
        if not isbn:
            continue
        isbn_str = str(isbn)
        if not isbn_str.isdigit():
            continue
        book_data = get_book_data_by_isbn(isbn_str)
        if not is_english_book(book_data):
            continue
        german_edition = find_german_translation(book_data)
        if not german_edition:
            continue
        new_isbn = german_edition.get('isbn_13', [None])[0] or german_edition.get('isbn_10', [None])[0]
        if new_isbn:
            book['isbn'] = new_isbn
        book['id'] = get_goodreads_id(new_isbn)
        image_link = german_edition.get('cover', {}).get('large') or \
                     german_edition.get('cover', {}).get('medium') or \
                     german_edition.get('cover', {}).get('small')
        if image_link:
            book['image_url'] = image_link

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    process_buchliste("data/Meine_Buchliste.yaml", "data/Meine_Buchliste_text.yaml")