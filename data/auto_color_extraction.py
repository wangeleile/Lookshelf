#!/usr/bin/env python3
"""
Automatische Farbextraktion für Buchcover
==========================================

Dieses Skript verarbeitet alle Bücher in der YAML-Datei und extrahiert automatisch
die dominierenden Farben aus den Buchcovern für Bücher, die noch kein book_color Feld haben.

Autor: Automatisiert aus colorpicker.py
"""

import yaml
import requests
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import colorsys

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('color_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BookColorExtractor:
    """Klasse für die automatische Extraktion von Buchcover-Farben"""
    
    def __init__(self, yaml_file: str = "Meine_Buchliste_updated.yaml"):
        self.yaml_file = yaml_file
        self.backup_file = f"{yaml_file}.backup"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Statistiken
        self.processed = 0
        self.errors = 0
        self.skipped = 0
        self.updated = 0
        
    def load_books_data(self) -> Dict:
        """YAML-Datei laden"""
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Fehler beim Laden der YAML-Datei: {e}")
            raise
    
    def save_books_data(self, data: Dict) -> None:
        """YAML-Datei speichern mit Backup"""
        try:
            # Backup erstellen
            if Path(self.yaml_file).exists():
                import shutil
                shutil.copy2(self.yaml_file, self.backup_file)
                logger.info(f"Backup erstellt: {self.backup_file}")
            
            # Neue Daten speichern
            with open(self.yaml_file, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
            logger.info(f"Daten gespeichert: {self.yaml_file}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der YAML-Datei: {e}")
            raise
    
    def download_image(self, url: str, timeout: int = 10) -> Optional[Image.Image]:
        """Bild von URL herunterladen"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # Zu RGBA konvertieren falls nötig
            if image.mode in ('RGBA', 'LA'):
                # Weißen Hintergrund für transparente Bilder
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            logger.warning(f"Fehler beim Herunterladen des Bildes {url}: {e}")
            return None
    
    def extract_dominant_color(self, image: Image.Image, n_clusters: int = 5) -> str:
        """
        Dominante Farbe aus Bild extrahieren
        
        Args:
            image: PIL Image object
            n_clusters: Anzahl der Cluster für K-Means
            
        Returns:
            Hex-Farbcode der dominantesten Farbe
        """
        try:
            # Bild verkleinern für schnellere Verarbeitung
            image = image.resize((100, 100))
            
            # Zu numpy array konvertieren
            data = np.array(image)
            data = data.reshape((-1, 3))
            
            # K-Means Clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans.fit(data)
            
            # Cluster-Zentren und ihre Häufigkeiten
            colors = kmeans.cluster_centers_
            labels = kmeans.labels_
            
            # Häufigkeiten berechnen
            label_counts = np.bincount(labels)
            
            # Dominanteste Farbe (häufigster Cluster)
            dominant_color_idx = np.argmax(label_counts)
            dominant_color = colors[dominant_color_idx].astype(int)
            
            # Zu Hex konvertieren
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(dominant_color[0]), 
                int(dominant_color[1]), 
                int(dominant_color[2])
            )
            
            return hex_color
            
        except Exception as e:
            logger.error(f"Fehler bei der Farbextraktion: {e}")
            return "#808080"  # Fallback zu Grau
    
    def needs_color_update(self, book: Dict) -> bool:
        """Prüft ob Buch eine Farbaktualisierung benötigt"""
        return (
            'image_url' in book and 
            book['image_url'] and 
            book['image_url'].strip() and
            ('book_color' not in book or not book['book_color'])
        )
    
    def process_single_book(self, book: Dict, book_index: int) -> bool:
        """
        Verarbeitet ein einzelnes Buch
        
        Returns:
            True wenn erfolgreich aktualisiert, False sonst
        """
        title = book.get('title', 'Unbekannt')
        author = book.get('author', 'Unbekannt')
        image_url = book.get('image_url', '')
        
        logger.info(f"[{book_index}] Verarbeite: '{title}' von {author}")
        
        try:
            # Bild herunterladen
            image = self.download_image(image_url)
            if image is None:
                logger.warning(f"[{book_index}] Bild konnte nicht geladen werden: {image_url}")
                return False
            
            # Dominante Farbe extrahieren
            color = self.extract_dominant_color(image)
            
            # Farbe im Buch-Dictionary setzen
            book['book_color'] = color
            
            logger.info(f"[{book_index}] Farbe extrahiert: {color}")
            return True
            
        except Exception as e:
            logger.error(f"[{book_index}] Fehler bei der Verarbeitung: {e}")
            return False
    
    def process_all_books(self, max_books: Optional[int] = None, delay: float = 0.5) -> None:
        """
        Verarbeitet alle Bücher ohne book_color
        
        Args:
            max_books: Maximale Anzahl zu verarbeitender Bücher (None = alle)
            delay: Verzögerung zwischen Anfragen in Sekunden
        """
        logger.info("Starte automatische Farbextraktion...")
        
        # Daten laden
        data = self.load_books_data()
        books = data.get('books', [])
        
        # Bücher filtern, die eine Aktualisierung benötigen
        books_to_process = [
            (i, book) for i, book in enumerate(books) 
            if self.needs_color_update(book)
        ]
        
        total_books = len(books_to_process)
        if max_books:
            books_to_process = books_to_process[:max_books]
            total_books = min(total_books, max_books)
        
        logger.info(f"Gefunden: {total_books} Bücher ohne book_color")
        
        if total_books == 0:
            logger.info("Alle Bücher haben bereits eine Farbe. Nichts zu tun.")
            return
        
        # Bücher verarbeiten
        for processed_count, (book_index, book) in enumerate(books_to_process, 1):
            logger.info(f"\n--- Fortschritt: {processed_count}/{total_books} ---")
            
            if self.process_single_book(book, book_index + 1):
                self.updated += 1
            else:
                self.errors += 1
            
            self.processed += 1
            
            # Verzögerung zwischen Anfragen
            if delay > 0 and processed_count < total_books:
                time.sleep(delay)
            
            # Zwischenspeicherung alle 10 Bücher
            if processed_count % 10 == 0:
                logger.info(f"Zwischenspeicherung nach {processed_count} Büchern...")
                self.save_books_data(data)
        
        # Finale Speicherung
        logger.info("\nFinale Speicherung...")
        self.save_books_data(data)
        
        # Statistiken ausgeben
        self.print_statistics()
    
    def print_statistics(self) -> None:
        """Statistiken ausgeben"""
        logger.info("\n" + "="*50)
        logger.info("VERARBEITUNGSSTATISTIKEN")
        logger.info("="*50)
        logger.info(f"Verarbeitete Bücher: {self.processed}")
        logger.info(f"Erfolgreich aktualisiert: {self.updated}")
        logger.info(f"Fehler: {self.errors}")
        logger.info(f"Erfolgsrate: {(self.updated/max(self.processed, 1)*100):.1f}%")
        logger.info("="*50)

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatische Farbextraktion für Buchcover')
    parser.add_argument('--file', '-f', default='Meine_Buchliste_updated.yaml',
                       help='YAML-Datei mit Buchدaten')
    parser.add_argument('--max-books', '-m', type=int, default=None,
                       help='Maximale Anzahl zu verarbeitender Bücher')
    parser.add_argument('--delay', '-d', type=float, default=0.5,
                       help='Verzögerung zwischen Anfragen in Sekunden')
    parser.add_argument('--test', '-t', action='store_true',
                       help='Testmodus: Nur die ersten 5 Bücher verarbeiten')
    
    args = parser.parse_args()
    
    if args.test:
        args.max_books = 5
        logger.info("TESTMODUS: Verarbeite nur die ersten 5 Bücher")
    
    extractor = BookColorExtractor(args.file)
    extractor.process_all_books(max_books=args.max_books, delay=args.delay)

if __name__ == "__main__":
    main()
