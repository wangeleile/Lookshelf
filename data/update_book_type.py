#!/usr/bin/env python3
"""
Skript zum Aktualisieren des bookType Feldes basierend auf dem Binding Feld.
Wenn Binding "Hardcover", "Paperback" oder "Kindle" enthält, wird bookType auf "book" gesetzt.
"""

import yaml
import os
from typing import Dict, Any, List

def load_yaml_file(filepath: str) -> Dict[str, Any]:
    """Lädt die YAML-Datei."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_yaml_file(filepath: str, data: Dict[str, Any]) -> None:
    """Speichert die YAML-Datei."""
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

def update_book_types(data: Dict[str, Any]) -> int:
    """
    Aktualisiert bookType basierend auf Binding.
    Gibt die Anzahl der geänderten Einträge zurück.
    """
    books = data.get('books', [])
    changes_count = 0
    
    target_bindings = ['Hardcover', 'Paperback', 'Kindle']
    
    for book in books:
        binding = book.get('Binding', '') or ''
        current_book_type = book.get('bookType', '')
        
        # Prüfe ob Binding einen der Zielwerte enthält
        if binding and any(target in binding for target in target_bindings):
            if current_book_type != 'book':
                print(f"Ändere '{book.get('title', 'Unbekannt')}': Binding='{binding}', bookType: '{current_book_type}' -> 'book'")
                book['bookType'] = 'book'
                changes_count += 1
    
    return changes_count

def main():
    filepath = '/workspaces/Lookshelf/data/Meine_Buchliste.yaml'
    backup_filepath = '/workspaces/Lookshelf/data/_backups/Meine_Buchliste_before_booktype_update.yaml'
    
    # Stelle sicher, dass das Backup-Verzeichnis existiert
    os.makedirs(os.path.dirname(backup_filepath), exist_ok=True)
    
    print("Lade YAML-Datei...")
    data = load_yaml_file(filepath)
    
    print("Erstelle Backup...")
    save_yaml_file(backup_filepath, data)
    print(f"Backup erstellt: {backup_filepath}")
    
    print("\nAktualisiere bookType Felder...")
    changes_count = update_book_types(data)
    
    if changes_count > 0:
        print(f"\nSpeichere {changes_count} Änderungen...")
        save_yaml_file(filepath, data)
        print(f"Datei erfolgreich aktualisiert: {filepath}")
    else:
        print("\nKeine Änderungen erforderlich.")
    
    print(f"\nZusammenfassung: {changes_count} Einträge wurden aktualisiert.")

if __name__ == "__main__":
    main()
