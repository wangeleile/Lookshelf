#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript zum Nachtragen von image_url für die ersten 5 Bücher ohne Bild
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
                for key in ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']:
                    if key in image_links:
                        url = image_links[key]
                        # Verbessere die Bildqualität durch Zoom-Parameter und https
                        url = url.replace('http://', 'https://')
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
    test_count = 0
    max_tests = 5  # Teste nur die ersten 5 Bücher ohne Bild
    
    print(f"Teste die ersten {max_tests} Bücher ohne image_url...")
    
    for i, book in enumerate(books):
        if test_count >= max_tests:
            break
            
        title = book.get('title', 'Unbekannt')
        isbn = book.get('isbn', '')
        image_url = book.get('image_url', '')
        
        # Nur Bücher ohne image_url oder mit null-Werten bearbeiten
        if not image_url or image_url == 'null' or image_url is None:
            test_count += 1
            if isbn:
                print(f"[Test {test_count}/{max_tests}] Suche Bild für: {title}")
                print(f"  ISBN: {isbn}")
                new_image_url = get_google_books_image_url(isbn)
                if new_image_url:
                    print(f"  ✓ Gefunden: {new_image_url}")
                    # Für den Test zeigen wir nur das Ergebnis, aber ändern nichts
                    # book['image_url'] = new_image_url
                    # updated_count += 1
                else:
                    print(f"  ✗ Kein Bild gefunden")
                
                time.sleep(1)  # Pause um API nicht zu überlasten
            else:
                print(f"[Test {test_count}/{max_tests}] Überspringe '{title}' - keine ISBN")
    
    print(f"\n✓ Test beendet! Von {test_count} getesteten Büchern wurden Bilder gefunden.")

if __name__ == "__main__":
    main()
