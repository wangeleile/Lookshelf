#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dry-Run Version: Zeigt, welche image_urls gefunden werden würden,
ohne die YAML-Datei zu ändern.

Testet die ersten 10 Bücher ohne Bild.
"""

import requests
import yaml
import time
import re

def get_google_books_image_url(isbn):
    """Holt die Cover-URL von Google Books anhand der ISBN."""
    if not isbn:
        return None
    
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
                
                for key in ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']:
                    if key in image_links:
                        url = image_links[key]
                        url = url.replace('http://', 'https://')
                        if 'zoom=1' in url:
                            url = url.replace('zoom=1', 'zoom=5')
                        elif 'zoom=' not in url:
                            url = url + '&zoom=5'
                        return url
    except Exception as e:
        print(f"   Fehler: {e}")
    return None

def main():
    input_file = "/Volumes/Documents/_MyBookshelf/Lookshelf/data/Meine_Buchliste.yaml"
    
    print("🔍 Dry-Run: Teste die ersten 10 Bücher ohne image_url")
    print("=" * 60)
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except UnicodeDecodeError:
        with open(input_file, "r", encoding="latin1") as f:
            content = f.read()
        data = yaml.safe_load(content)
    
    books = data.get('books', [])
    books_without_image = []
    
    # Sammle Bücher ohne image_url
    for i, book in enumerate(books):
        image_url = book.get('image_url', '')
        if not image_url or image_url == 'null' or image_url is None:
            isbn = book.get('isbn', '')
            if isbn:
                books_without_image.append((i, book))
    
    # Teste nur die ersten 10
    test_books = books_without_image[:10]
    found_count = 0
    
    for i, (_, book) in enumerate(test_books):
        title = book.get('title', 'Unbekannt')
        isbn = book.get('isbn', '')
        
        print(f"[{i+1:2d}/10] {title}")
        print(f"       ISBN: {isbn}")
        
        image_url = get_google_books_image_url(isbn)
        if image_url:
            found_count += 1
            print(f"       ✅ Gefunden: {image_url}")
        else:
            print(f"       ❌ Kein Bild gefunden")
        
        if i < len(test_books) - 1:
            time.sleep(1)
        print()
    
    print("=" * 60)
    print(f"📊 Test-Ergebnis: {found_count}/10 Bilder gefunden")
    print(f"   Geschätzte Erfolgsquote: {found_count*10}%")
    print(f"   Von {len(books_without_image)} Büchern würden ca. {int(len(books_without_image) * found_count/10)} Bilder gefunden werden.")

if __name__ == "__main__":
    main()
