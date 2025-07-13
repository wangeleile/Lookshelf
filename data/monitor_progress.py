#!/usr/bin/env python3
"""
Monitor für die Farbextraktion
==============================

Zeigt den aktuellen Fortschritt der Farbextraktion an.
"""

import yaml
import time
from pathlib import Path

def monitor_progress():
    yaml_file = "Meine_Buchliste_updated.yaml"
    
    print("Farbextraktion Monitor")
    print("=====================")
    
    while True:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                books = data.get('books', [])
            
            # Bücher zählen
            total_books = len(books)
            books_with_color = sum(1 for book in books if book.get('book_color'))
            books_without_color = total_books - books_with_color
            
            percentage = (books_with_color / total_books * 100) if total_books > 0 else 0
            
            print(f"\r[{time.strftime('%H:%M:%S')}] "
                  f"Bücher mit Farbe: {books_with_color}/{total_books} "
                  f"({percentage:.1f}%) | "
                  f"Fehlend: {books_without_color}", end="", flush=True)
            
            # Wenn alle Bücher Farben haben, beenden
            if books_without_color == 0:
                print("\n✅ Alle Bücher haben jetzt eine Farbe!")
                break
                
            time.sleep(5)  # Alle 5 Sekunden aktualisieren
            
        except KeyboardInterrupt:
            print("\nMonitoring gestoppt.")
            break
        except Exception as e:
            print(f"\nFehler: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_progress()
