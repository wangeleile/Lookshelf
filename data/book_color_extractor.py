#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Color Extractor - Extrahiert dominante Farben aus Buchcover-Bildern

Das Skript:
1. Lädt die YAML-Datei mit den Büchern
2. Lädt jedes Buchcover-Bild von der image_url
3. Extrahiert die dominante Farbe mittels K-Means Clustering
4. Konvertiert die Farbe zu Hex-Format
5. Trägt die Farbe ins book_color Feld ein
6. Speichert die aktualisierte YAML-Datei

Benötigte Pakete:
pip install pillow numpy scikit-learn pyyaml requests
"""

import requests
import yaml
import time
import shutil
from datetime import datetime
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from io import BytesIO
import re

def rgb_to_hex(rgb):
    """Konvertiert RGB-Werte zu Hex-Format."""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

def get_dominant_color(image_url, max_colors=5):
    """
    Extrahiert die dominante Farbe aus einem Bild.
    
    Args:
        image_url: URL zum Bild
        max_colors: Anzahl der Farb-Cluster für K-Means
    
    Returns:
        Hex-Farbcode der dominanten Farbe oder None bei Fehlern
    """
    try:
        # Bild herunterladen
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        # Bild öffnen und verarbeiten
        image = Image.open(BytesIO(response.content))
        
        # Konvertiere zu RGB falls nötig
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Bild verkleinern für schnellere Verarbeitung
        image = image.resize((150, 150))
        
        # Bild zu Numpy Array konvertieren
        data = np.array(image)
        data = data.reshape((-1, 3))
        
        # Entferne sehr helle Farben (Weiß/Hell) und sehr dunkle (Schwarz)
        # um bessere "echte" Buchfarben zu bekommen
        mask = np.all(data > [20, 20, 20], axis=1) & np.all(data < [235, 235, 235], axis=1)
        if np.sum(mask) < len(data) * 0.1:  # Falls zu wenig Farben übrig, verwende alle
            filtered_data = data
        else:
            filtered_data = data[mask]
        
        # K-Means Clustering für dominante Farben
        n_clusters = min(max_colors, len(np.unique(filtered_data.view(np.void), axis=0)))
        if n_clusters < 1:
            n_clusters = 1
            
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(filtered_data)
        
        # Finde den größten Cluster (dominanteste Farbe)
        labels = kmeans.labels_
        cluster_counts = np.bincount(labels)
        dominant_cluster = np.argmax(cluster_counts)
        dominant_color = kmeans.cluster_centers_[dominant_cluster].astype(int)
        
        # Zu Hex konvertieren
        hex_color = rgb_to_hex(dominant_color)
        return hex_color
        
    except Exception as e:
        print(f"    Fehler beim Verarbeiten des Bildes: {e}")
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
    backup_path = filepath.replace('.yaml', f'_backup_colors_{timestamp}.yaml')
    shutil.copy2(filepath, backup_path)
    return backup_path

def test_color_extraction():
    """Testet die Farbextraktion mit ein paar Beispiel-URLs."""
    test_urls = [
        "https://books.google.com/books/content?id=ncBODwAAQBAJ&printsec=frontcover&img=1&zoom=5&source=gbs_api",
        "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1363885869i/17666457.jpg",
        "https://books.google.com/books/content?id=_gvLPQAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api"
    ]
    
    print("🧪 Teste Farbextraktion mit Beispielbildern...")
    for i, url in enumerate(test_urls, 1):
        print(f"  Test {i}: {url[:60]}...")
        color = get_dominant_color(url)
        if color:
            print(f"    ✅ Dominante Farbe: {color}")
        else:
            print(f"    ❌ Fehler beim Extrahieren der Farbe")
        time.sleep(1)

def main():
    input_file = "/Volumes/Documents/_MyBookshelf/Lookshelf/data/Meine_Buchliste_updated.yaml"
    
    print("🎨 Book Color Extractor")
    print("=" * 50)
    
    # Test der Farbextraktion
    test_color_extraction()
    
    print("\n📖 Lade Buchdaten...")
    data = load_yaml_file(input_file)
    
    if not data or 'books' not in data:
        print("❌ Fehler: Keine Bücher in der YAML-Datei gefunden!")
        return
    
    books = data['books']
    total_books = len(books)
    books_without_color = []
    books_with_image_url = []
    
    # Sammle Bücher die eine image_url haben aber keine book_color
    for i, book in enumerate(books):
        image_url = book.get('image_url', '')
        book_color = book.get('book_color', '')
        
        if image_url and image_url != 'null' and image_url is not None:
            books_with_image_url.append((i, book))
            if not book_color or book_color == 'null' or book_color is None:
                books_without_color.append((i, book))
    
    print(f"📚 Bücher gesamt: {total_books}")
    print(f"🖼️  Bücher mit image_url: {len(books_with_image_url)}")
    print(f"🎨 Bücher ohne book_color: {len(books_without_color)}")
    
    if not books_without_color:
        print("✅ Alle Bücher haben bereits eine book_color!")
        return
    
    # Zeige einige Beispiele
    print(f"\n📖 Beispiele von Büchern ohne Farbe:")
    for i, (_, book) in enumerate(books_without_color[:5]):
        title = book.get('title', 'Unbekannt')
        image_url = book.get('image_url', '')[:60] + "..." if len(book.get('image_url', '')) > 60 else book.get('image_url', '')
        print(f"   {i+1}. {title}")
        print(f"      URL: {image_url}")
    if len(books_without_color) > 5:
        print(f"   ... und {len(books_without_color) - 5} weitere")
    
    # Frage nach Bestätigung
    print(f"\n❓ Möchten Sie Farben für {len(books_without_color)} Bücher extrahieren?")
    print("   Dies kann einige Minuten dauern (je nach Internetverbindung)...")
    response = input("   Fortfahren? (j/n): ")
    if response.lower() not in ['j', 'ja', 'y', 'yes']:
        print("❌ Abgebrochen.")
        return
    
    # Erstelle Backup
    print("\n💾 Erstelle Backup...")
    backup_path = create_backup(input_file)
    print(f"   Backup gespeichert: {backup_path}")
    
    print("\n🎨 Beginne mit der Farbextraktion...")
    print("=" * 70)
    
    updated_count = 0
    failed_count = 0
    
    # Verarbeite jedes Buch ohne Farbe
    for i, (book_index, book) in enumerate(books_without_color):
        title = book.get('title', 'Unbekannt')
        image_url = book.get('image_url', '')
        
        print(f"[{i+1:3d}/{len(books_without_color)}] {title}")
        print(f"      URL: {image_url[:60]}{'...' if len(image_url) > 60 else ''}")
        
        # Extrahiere dominante Farbe
        dominant_color = get_dominant_color(image_url)
        
        if dominant_color:
            books[book_index]['book_color'] = dominant_color
            updated_count += 1
            print(f"      ✅ Farbe: {dominant_color}")
        else:
            failed_count += 1
            print(f"      ❌ Extraktion fehlgeschlagen")
        
        # Pause zwischen Downloads um Server nicht zu überlasten
        if i < len(books_without_color) - 1:
            time.sleep(0.8)
        print()
    
    print("=" * 70)
    print(f"✅ Fertig! {updated_count} Farben extrahiert, {failed_count} fehlgeschlagen.")
    
    if updated_count > 0:
        print("\n💾 Speichere aktualisierte Daten...")
        save_yaml_file(data, input_file)
        print(f"   ✅ {input_file} wurde aktualisiert!")
        print(f"   📁 Backup verfügbar: {backup_path}")
        
        print(f"\n📊 Zusammenfassung:")
        print(f"   • Bücher gesamt: {total_books}")
        print(f"   • Bücher mit Bildern: {len(books_with_image_url)}")
        print(f"   • Neue Farben extrahiert: {updated_count}")
        print(f"   • Fehlgeschlagen: {failed_count}")
        print(f"   • Erfolgsquote: {updated_count/(updated_count+failed_count)*100:.1f}%")
    else:
        print("\n❌ Keine Farben extrahiert.")

if __name__ == "__main__":
    main()
