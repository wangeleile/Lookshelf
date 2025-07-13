#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finales Skript zum Nachtragen fehlender image_url Adressen in Meine_Buchliste.yaml

Das Skript:
1. Lädt die YAML-Datei
2. Findet alle Bücher ohne image_url
3. Sucht für jedes Buch über Google Books API nach Cover-URLs
4. Aktualisiert die image_url Felder
5. Speichert eine Backup-Datei und überschreibt dann das Original

Verwendung:
    python3 final_image_updater.py

Das Skript fragt vor Änderungen nach Bestätigung.
"""

import requests
import yaml
import time
import re
import shutil
from datetime import datetime

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
                
                # Bevorzuge größere Bilder und verbessere Qualität
                for key in ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']:
                    if key in image_links:
                        url = image_links[key]
                        # Konvertiere zu https für bessere Sicherheit
                        url = url.replace('http://', 'https://')
                        # Verbessere Bildqualität durch Zoom-Parameter
                        if 'zoom=1' in url:
                            url = url.replace('zoom=1', 'zoom=5')
                        elif 'zoom=' not in url:
                            url = url + '&zoom=5'
                        return url
    except Exception as e:
        print(f"   Fehler bei Google Books API für ISBN {isbn}: {e}")
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

def create_backup(filepath):
    """Erstellt eine Backup-Datei mit Zeitstempel."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.replace('.yaml', f'_backup_{timestamp}.yaml')
    shutil.copy2(filepath, backup_path)
    return backup_path

def main():
    input_file = "/Volumes/Documents/_MyBookshelf/Lookshelf/data/Meine_Buchliste.yaml"
    
    print("🔍 Lade YAML-Datei...")
    data = load_yaml_file(input_file)
    
    if not data or 'books' not in data:
        print("❌ Fehler: Keine Bücher in der YAML-Datei gefunden!")
        return
    
    books = data['books']
    total_books = len(books)
    books_without_image = []
    
    print(f"📚 Gefunden: {total_books} Bücher")
    
    # Sammle alle Bücher ohne image_url
    for i, book in enumerate(books):
        image_url = book.get('image_url', '')
        if not image_url or image_url == 'null' or image_url is None:
            isbn = book.get('isbn', '')
            if isbn:  # Nur Bücher mit ISBN können über Google Books gefunden werden
                books_without_image.append((i, book))
    
    print(f"🖼️  Bücher ohne image_url (mit ISBN): {len(books_without_image)}")
    
    if not books_without_image:
        print("✅ Alle Bücher haben bereits eine image_url oder keine ISBN!")
        return
    
    # Zeige einige Beispiele
    print("\\n📖 Beispiele von Büchern ohne Bild:")
    for i, (_, book) in enumerate(books_without_image[:5]):
        title = book.get('title', 'Unbekannt')
        isbn = book.get('isbn', '')
        print(f"   {i+1}. {title} (ISBN: {isbn})")
    if len(books_without_image) > 5:
        print(f"   ... und {len(books_without_image) - 5} weitere")
    
    # Frage nach Bestätigung
    print(f"\\n❓ Möchten Sie image_urls für {len(books_without_image)} Bücher suchen?")
    print("   Dies kann einige Minuten dauern...")
    response = input("   Fortfahren? (j/n): ")
    if response.lower() not in ['j', 'ja', 'y', 'yes']:
        print("❌ Abgebrochen.")
        return
    
    # Erstelle Backup
    print("\\n💾 Erstelle Backup...")
    backup_path = create_backup(input_file)
    print(f"   Backup gespeichert: {backup_path}")
    
    print("\\n🔎 Beginne mit der Suche nach Bild-URLs...")
    print("=" * 60)
    
    updated_count = 0
    
    # Verarbeite jedes Buch ohne Bild
    for i, (book_index, book) in enumerate(books_without_image):
        title = book.get('title', 'Unbekannt')
        isbn = book.get('isbn', '')
        
        print(f"[{i+1:3d}/{len(books_without_image)}] {title}")
        print(f"      ISBN: {isbn}")
        
        image_url = get_google_books_image_url(isbn)
        if image_url:
            books[book_index]['image_url'] = image_url
            updated_count += 1
            print(f"      ✅ Gefunden: {image_url}")
        else:
            print(f"      ❌ Kein Bild gefunden")
        
        # Pause zwischen API-Aufrufen um Rate-Limits zu vermeiden
        if i < len(books_without_image) - 1:
            time.sleep(0.8)
        print()
    
    print("=" * 60)
    print(f"✅ Fertig! {updated_count} von {len(books_without_image)} Bild-URLs gefunden.")
    
    if updated_count > 0:
        print("\\n💾 Speichere aktualisierte Daten...")
        save_yaml_file(data, input_file)
        print(f"   ✅ {input_file} wurde aktualisiert!")
        print(f"   📁 Backup verfügbar: {backup_path}")
        
        print(f"\\n📊 Zusammenfassung:")
        print(f"   • Bücher insgesamt: {total_books}")
        print(f"   • Bücher ohne Bild (mit ISBN): {len(books_without_image)}")
        print(f"   • Neue Bilder gefunden: {updated_count}")
        print(f"   • Erfolgsquote: {updated_count/len(books_without_image)*100:.1f}%")
    else:
        print("\\n❌ Keine Updates vorgenommen.")
        print("   Keine neuen Bild-URLs gefunden.")

if __name__ == "__main__":
    print("🎨 Image URL Updater für Meine_Buchliste.yaml")
    print("=" * 50)
    main()
