#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript zum Nachtragen fehlender image_url Adressen in Meine_Buchliste.yaml

Das Skript sucht für Bücher ohne image_url anhand der ID oder ISBN
nach passenden Buchcover-URLs aus verschiedenen Quellen:
1. Google Books API (anhand ISBN)
2. Goodreads (anhand ID)
3. Open Library (anhand ISBN)
"""

import requests
import yaml
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def get_google_books_image_url(isbn):
    """Holt die Cover-URL von Google Books anhand der ISBN."""
    if not isbn:
        return None
    
    # ISBN von zusätzlichen Zeichen bereinigen
    isbn_clean = re.sub(r'[^0-9X]', '', str(isbn))
    
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_clean}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                volume_info = items[0].get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                # Bevorzuge größere Bilder
                for key in ['extraLarge', 'large', 'medium', 'small', 'thumbnail']:
                    if key in image_links:
                        # Verbessere die Bildqualität durch Zoom-Parameter
                        url = image_links[key]
                        if 'zoom=' not in url:
                            url = url.replace('zoom=1', 'zoom=5') if 'zoom=1' in url else url + '&zoom=5'
                        return url
    except Exception as e:
        print(f"Fehler bei Google Books API für ISBN {isbn}: {e}")
    return None

def get_goodreads_image_url(book_id):
    """Holt die Cover-URL von Goodreads anhand der Book ID."""
    if not book_id:
        return None
    
    url = f"https://www.goodreads.com/book/show/{book_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Versuche verschiedene Selektoren für das Cover-Bild
            selectors = [
                'img[data-testid="bookCover"]',
                'img.ResponsiveImage',
                'img[alt*="cover"]',
                '.BookCover img',
                '.leftContainer img'
            ]
            
            for selector in selectors:
                img_tag = soup.select_one(selector)
                if img_tag and img_tag.get("src"):
                    src = img_tag["src"]
                    # Verbessere die Bildqualität wenn möglich
                    if '_SX' in src or '_SY' in src:
                        src = re.sub(r'_S[XY]\d+_', '_SX600_', src)
                    return src
                    
    except Exception as e:
        print(f"Fehler bei Goodreads für ID {book_id}: {e}")
    return None

def get_openlibrary_image_url(isbn):
    """Holt die Cover-URL von Open Library anhand der ISBN."""
    if not isbn:
        return None
    
    # ISBN von zusätzlichen Zeichen bereinigen
    isbn_clean = re.sub(r'[^0-9X]', '', str(isbn))
    
    # Versuche erst die Cover API
    cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn_clean}-L.jpg"
    try:
        response = requests.head(cover_url, timeout=5)
        if response.status_code == 200:
            return cover_url
    except:
        pass
    
    # Falls Cover API nicht funktioniert, versuche über Books API
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_clean}&jscmd=details&format=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            key = f"ISBN:{isbn_clean}"
            if key in data:
                details = data[key].get('details', {})
                covers = details.get('covers', [])
                if covers:
                    cover_id = covers[0]
                    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    except Exception as e:
        print(f"Fehler bei Open Library für ISBN {isbn}: {e}")
    return None

def get_image_url_for_book(book):
    """Versucht eine Bild-URL für ein Buch zu finden."""
    isbn = book.get('isbn', '')
    book_id = book.get('id', '')
    title = book.get('title', 'Unbekannt')
    
    print(f"Suche Bild für: {title}")
    
    # 1. Versuche Google Books (meist beste Qualität)
    if isbn:
        image_url = get_google_books_image_url(isbn)
        if image_url:
            print(f"  ✓ Google Books: {image_url}")
            return image_url
        time.sleep(0.5)  # Kurze Pause zwischen API-Aufrufen
    
    # 2. Versuche Goodreads
    if book_id:
        image_url = get_goodreads_image_url(book_id)
        if image_url:
            print(f"  ✓ Goodreads: {image_url}")
            return image_url
        time.sleep(1)  # Längere Pause für Goodreads
    
    # 3. Versuche Open Library
    if isbn:
        image_url = get_openlibrary_image_url(isbn)
        if image_url:
            print(f"  ✓ Open Library: {image_url}")
            return image_url
        time.sleep(0.5)
    
    print(f"  ✗ Kein Bild gefunden")
    return None

def load_yaml_file(filepath):
    """Lädt die YAML-Datei mit verschiedenen Encoding-Versuchen."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except UnicodeDecodeError:
        print("UTF-8 Fehler, versuche latin1...")
        with open(filepath, "r", encoding="latin1") as f:
            content = f.read()
        return yaml.safe_load(content)

def save_yaml_file(data, filepath):
    """Speichert die YAML-Datei mit UTF-8 Encoding."""
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

def main():
    input_file = "/Volumes/Documents/_MyBookshelf/Lookshelf/data/Meine_Buchliste.yaml"
    output_file = "/Volumes/Documents/_MyBookshelf/Lookshelf/data/Meine_Buchliste_updated.yaml"
    
    print("Lade YAML-Datei...")
    data = load_yaml_file(input_file)
    
    if not data or 'books' not in data:
        print("Fehler: Keine Bücher in der YAML-Datei gefunden!")
        return
    
    books = data['books']
    total_books = len(books)
    updated_count = 0
    books_without_image = []
    
    print(f"Gefunden: {total_books} Bücher")
    
    # Sammle alle Bücher ohne image_url
    for i, book in enumerate(books):
        image_url = book.get('image_url', '')
        if not image_url or image_url == 'null' or image_url is None:
            books_without_image.append((i, book))
    
    print(f"Bücher ohne image_url: {len(books_without_image)}")
    
    if not books_without_image:
        print("Alle Bücher haben bereits eine image_url!")
        return
    
    # Frage nach Bestätigung
    response = input(f"Möchten Sie image_urls für {len(books_without_image)} Bücher suchen? (j/n): ")
    if response.lower() not in ['j', 'ja', 'y', 'yes']:
        print("Abgebrochen.")
        return
    
    print("\nBeginne mit der Suche nach Bild-URLs...\n")
    
    # Verarbeite jedes Buch ohne Bild
    for i, (book_index, book) in enumerate(books_without_image):
        print(f"[{i+1}/{len(books_without_image)}]", end=" ")
        
        image_url = get_image_url_for_book(book)
        if image_url:
            books[book_index]['image_url'] = image_url
            updated_count += 1
        
        # Pause zwischen Büchern um APIs nicht zu überlasten
        if i < len(books_without_image) - 1:
            time.sleep(1)
    
    print(f"\n✓ Fertig! {updated_count} von {len(books_without_image)} Bild-URLs gefunden.")
    
    if updated_count > 0:
        print(f"Speichere aktualisierte Daten in: {output_file}")
        save_yaml_file(data, output_file)
        print("Datei gespeichert!")
        
        # Frage ob die Originaldatei überschrieben werden soll
        response = input("Möchten Sie die Originaldatei überschreiben? (j/n): ")
        if response.lower() in ['j', 'ja', 'y', 'yes']:
            save_yaml_file(data, input_file)
            print("Originaldatei wurde aktualisiert!")
    else:
        print("Keine Updates vorgenommen.")

if __name__ == "__main__":
    main()
