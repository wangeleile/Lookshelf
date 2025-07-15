#!/usr/bin/env python3
"""
Einfache API für den Book Editor
Ermöglicht das Speichern von Änderungen an der YAML-Datei
"""

import os
import yaml
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import shutil

app = Flask(__name__)
CORS(app)  # Erlaube CORS für alle Domains

# Pfad zur YAML-Datei
YAML_FILE = os.path.join(os.path.dirname(__file__), 'Meine_Buchliste.yaml')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), '_backups')

def create_backup():
    """Erstelle ein Backup der aktuellen YAML-Datei"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'Meine_Buchliste_backup_{timestamp}.yaml')
    
    if os.path.exists(YAML_FILE):
        shutil.copy2(YAML_FILE, backup_file)
        return backup_file
    return None

@app.route('/api/books', methods=['GET'])
def get_books():
    """Lade alle Bücher"""
    try:
        with open(YAML_FILE, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Fehler beim Laden: {str(e)}'}), 500

@app.route('/api/books', methods=['POST'])
def save_books():
    """Speichere alle Bücher"""
    try:
        # Backup erstellen
        backup_file = create_backup()
        
        # Neue Daten empfangen
        new_data = request.json
        
        # Validierung
        if not new_data or 'books' not in new_data:
            return jsonify({'error': 'Ungültige Datenstruktur'}), 400
        
        # Generation date hinzufügen
        new_data['generation_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # YAML-Datei speichern
        with open(YAML_FILE, 'w', encoding='utf-8') as file:
            yaml.dump(new_data, file, default_flow_style=False, allow_unicode=True, 
                     indent=2, sort_keys=False)
        
        response_data = {
            'success': True, 
            'message': 'Bücher erfolgreich gespeichert',
            'backup_file': os.path.basename(backup_file) if backup_file else None,
            'book_count': len(new_data.get('books', []))
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Speichern: {str(e)}'}), 500

@app.route('/api/books/validate', methods=['POST'])
def validate_books():
    """Validiere Buchdaten"""
    try:
        data = request.json
        books = data.get('books', [])
        
        errors = []
        warnings = []
        
        for i, book in enumerate(books):
            # Pflichtfelder prüfen
            if not book.get('title'):
                errors.append(f'Buch {i+1}: Titel fehlt')
            if not book.get('author'):
                errors.append(f'Buch {i+1}: Autor fehlt')
            
            # Datentypen prüfen
            if book.get('year') and not isinstance(book.get('year'), (int, float)):
                warnings.append(f'Buch {i+1}: Jahr sollte eine Zahl sein')
            if book.get('rating') and not isinstance(book.get('rating'), (int, float)):
                warnings.append(f'Buch {i+1}: Rating sollte eine Zahl sein')
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
        
    except Exception as e:
        return jsonify({'error': f'Validierungsfehler: {str(e)}'}), 500

@app.route('/api/backups', methods=['GET'])
def list_backups():
    """Liste alle verfügbaren Backups"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return jsonify({'backups': []})
        
        backups = []
        for file in os.listdir(BACKUP_DIR):
            if file.endswith('.yaml') and file.startswith('Meine_Buchliste_backup_'):
                file_path = os.path.join(BACKUP_DIR, file)
                backups.append({
                    'filename': file,
                    'created': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    'size': os.path.getsize(file_path)
                })
        
        # Nach Erstellungsdatum sortieren (neueste zuerst)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'backups': backups})
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Laden der Backups: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health Check Endpunkt"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'yaml_file_exists': os.path.exists(YAML_FILE)
    })

if __name__ == '__main__':
    print("🚀 Book Editor API Server startet...")
    print(f"📁 YAML-Datei: {YAML_FILE}")
    print(f"💾 Backup-Verzeichnis: {BACKUP_DIR}")
    print("🌐 Server läuft auf http://localhost:5002")
    print("📝 Endpunkte:")
    print("   GET  /api/books - Bücher laden")
    print("   POST /api/books - Bücher speichern")
    print("   POST /api/books/validate - Daten validieren")
    print("   GET  /api/backups - Backups auflisten")
    print("   GET  /health - Health Check")
    
    app.run(debug=True, port=5002, host='localhost')
