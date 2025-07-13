#!/usr/bin/env python3
"""
Schneller Test der Farbextraktion
==================================

Testet die Farbextraktion mit den ersten paar Büchern ohne book_color.
"""

import yaml
import sys
from auto_color_extraction import BookColorExtractor
import logging

# Logging für Test konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_test():
    """Schneller Test mit 3 Büchern"""
    logger.info("Starte Schnelltest der Farbextraktion...")
    
    try:
        # YAML-Datei finden
        yaml_file = "Meine_Buchliste_updated.yaml"
        
        # Testen ob Datei existiert
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                books = data.get('books', [])
                logger.info(f"Gefunden: {len(books)} Bücher in {yaml_file}")
        except FileNotFoundError:
            logger.error(f"Datei nicht gefunden: {yaml_file}")
            return False
        
        # Bücher ohne book_color finden
        books_without_color = []
        for i, book in enumerate(books):
            if ('image_url' in book and book['image_url'] and 
                ('book_color' not in book or not book['book_color'])):
                books_without_color.append((i, book))
        
        logger.info(f"Gefunden: {len(books_without_color)} Bücher ohne book_color")
        
        if len(books_without_color) == 0:
            logger.info("Alle Bücher haben bereits eine Farbe!")
            return True
        
        # Die ersten 3 anzeigen
        logger.info("\nErste Bücher ohne book_color:")
        for i, (idx, book) in enumerate(books_without_color[:5]):
            title = book.get('title', 'Unbekannt')
            author = book.get('author', 'Unbekannt')
            image_url = book.get('image_url', '')[:100] + '...' if len(book.get('image_url', '')) > 100 else book.get('image_url', '')
            logger.info(f"{i+1}. '{title}' von {author}")
            logger.info(f"   Image URL: {image_url}")
        
        # Extractor erstellen und testen
        extractor = BookColorExtractor(yaml_file)
        
        # Test mit nur einem Buch
        logger.info(f"\nTeste Farbextraktion mit 1 Buch...")
        extractor.process_all_books(max_books=1, delay=1.0)
        
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Test: {e}")
        return False

if __name__ == "__main__":
    quick_test()
