import requests
import yaml
import time
from bs4 import BeautifulSoup

# Hier das Feld eintragen, das aktualisiert werden soll (z.B. "Description")
update_field = "Description"

def get_description_goodreads_by_id(book_id):
    url = f"https://www.goodreads.com/book/show/{book_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            desc_tag = soup.find("div", {"data-testid": "description"})
            if desc_tag:
                spans = desc_tag.find_all("span")
                if len(spans) > 1 and spans[1].text.strip():
                    return spans[1].text.strip()
                elif spans and spans[0].text.strip():
                    return spans[0].text.strip()
    except Exception:
        pass
    return ''

def get_description_openlibrary(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        key = f"ISBN:{isbn}"
        if key in data:
            details = data[key].get('details', {})
            desc = details.get('description', '')
            if isinstance(desc, dict):
                return desc.get('value', '')
            return desc
    except Exception:
        pass
    return ''

def get_description_googlebooks(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&langRestrict=de"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        items = data.get('items', [])
        if items:
            volume = items[0].get('volumeInfo', {})
            desc = volume.get('description', '')
            # Sprache prüfen
            if volume.get('language', '') == 'de':
                return desc
            if desc:
                return desc
    except Exception:
        pass
    return ''

def get_description(isbn, book_id):
    # 1. Goodreads mit Book Id
    if book_id:
        desc = get_description_goodreads_by_id(book_id)
        if desc:
            return desc
    # 2. OpenLibrary
    desc = get_description_openlibrary(isbn)
    if desc:
        return desc
    # 3. Google Books
    desc = get_description_googlebooks(isbn)
    if desc:
        return desc
    return ''

def get_goodreads_cover_url(book_id):
    """Extrahiert das Cover-Bild von Goodreads anhand der Book Id."""
    url = f"https://www.goodreads.com/book/show/{book_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            img_tag = soup.find("img", {"data-testid": "bookCover"})
            if img_tag and img_tag.get("src"):
                return img_tag["src"]
    except Exception:
        pass
    return ''

# YAML-Datei einlesen (versucht zuerst UTF-8, dann latin1 falls nötig)
try:
    with open("data/Meine_Buchliste.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
except UnicodeDecodeError:
    with open("data/Meine_Buchliste.yaml", "r", encoding="latin1") as f:
        content = f.read()
    # Schreibe die Datei als UTF-8 repariert zurück (optional)
    with open("data/Meine_Buchliste_utf8.yaml", "w", encoding="utf-8") as f:
        f.write(content)
    data = yaml.safe_load(content)
    print("Warnung: Datei war nicht UTF-8 kodiert. Reparierte Version unter Meine_Buchliste_utf8.yaml gespeichert.")

# Bücher aktualisieren
for book in data.get('books', []):
    isbn = book.get('ISBN Combined')
    book_id = book.get('Book Id')
    field_value = book.get(update_field, '').strip("'\" ") if book.get(update_field) else ''
    # Beschreibung ggf. aktualisieren
    if (isbn or book_id) and not field_value:
        new_value = get_description(isbn, book_id)
        if new_value:
            book[update_field] = new_value
            print(f"{book.get('Titel','?')} ({isbn or book_id}): {update_field} aktualisiert.")
            print(new_value)
        time.sleep(1)  # APIs nicht überlasten
    # Cover-URL immer aktualisieren, wenn Book Id vorhanden ist
    if book_id:
        cover_url = get_goodreads_cover_url(book_id)
        if cover_url:
            book['image_Url'] = cover_url
            print(f"{book.get('Titel','?')} ({book_id}): image_Url aktualisiert.")
        time.sleep(1)  # APIs nicht überlasten

# YAML-Datei speichern
with open("data/Meine_Buchliste_test.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print(f"Fertig! Das Feld '{update_field}' wurde aktualisiert.")