#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfaches Skript zum Nachtragen fehlender image_url Adressen 
in Meine_Buchliste.yaml mittels Google Books API
"""

import requests
import yaml
import time
import re

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
                        url = image_links[key]
                        # Verbessere die Bildqualität durch Zoom-Parameter
                        if 'zoom=' not in url:
                            url = url.replace('zoom=1', 'zoom=5') if 'zoom=1' in url else url + '&zoom=5'
                        return url
    except Exception as e:
        print(f"Fehler bei Google Books API für ISBN {isbn}: {e}")
    return None

def main():
    input_file = "/Volumes/Documents/_MyBookshelf/Lookshelf/data/Meine_Buchliste.yaml"
    
    print("Lade YAML-Datei...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except UnicodeDecodeError:
        with open(input_file, "r", encoding="latin1") as f:
            content = f.read()
        data = yaml.safe_load(content)
    
    if not data or 'books' not in data:
        print("Fehler: Keine Bücher in der YAML-Datei gefunden!")
        return
    
    books = data['books']
    updated_count = 0
    
    print(f"Verarbeite {len(books)} Bücher...")
    
    for i, book in enumerate(books):
        title = book.get('title', 'Unbekannt')
        isbn = book.get('isbn', '')
        image_url = book.get('image_url', '')
        
        # Nur Bücher ohne image_url oder mit null-Werten bearbeiten
        if not image_url or image_url == 'null' or image_url is None:
            if isbn:
                print(f"[{i+1}/{len(books)}] Suche Bild für: {title}")
                new_image_url = get_google_books_image_url(isbn)
                if new_image_url:
                    book['image_url'] = new_image_url
                    updated_count += 1
                    print(f"  ✓ Gefunden: {new_image_url}")
                else:
                    print(f"  ✗ Kein Bild gefunden")
                
                time.sleep(0.5)  # Pause um API nicht zu überlasten
            else:
                print(f"[{i+1}/{len(books)}] Überspringe '{title}' - keine ISBN")
    
    print(f"\n✓ Fertig! {updated_count} Bild-URLs hinzugefügt.")
    
    if updated_count > 0:
        output_file = input_file.replace('.yaml', '_updated.yaml')
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        print(f"Aktualisierte Datei gespeichert: {output_file}")

if __name__ == "__main__":
    main()
