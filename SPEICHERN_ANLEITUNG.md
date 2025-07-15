# Book Editor - Speichern von Änderungen

## Übersicht

Der Book Editor kann Änderungen auf zwei Arten speichern:

### 1. Automatisches Speichern (empfohlen)
- **Voraussetzung**: API-Server muss laufen
- **Funktionalität**: Änderungen werden automatisch in die YAML-Datei gespeichert
- **Backups**: Automatische Backups bei jeder Änderung

### 2. Manuelles Speichern (Fallback)
- **Funktionalität**: YAML-Export zum manuellen Herunterladen
- **Verwendung**: Wenn API-Server nicht verfügbar ist

## API-Server starten

### Einfacher Start:
```bash
./start_api.sh
```

### Manueller Start:
```bash
cd data
python3 book_editor_api.py
```

### Voraussetzungen installieren:
```bash
pip3 install Flask flask-cors PyYAML
```

## Funktionen

### Automatisches Speichern
- **Beim Speichern eines Buchs**: Änderungen werden sofort an Server gesendet
- **Beim Löschen eines Buchs**: Änderungen werden sofort an Server gesendet
- **Manuell**: Button "💾 Zum Server speichern"

### Backup-System
- Automatische Backups in `data/_backups/`
- Timestamp im Dateinamen
- Backups werden vor jeder Änderung erstellt

### Validierung
- Prüfung der Datenstruktur vor dem Speichern
- Fehlermeldungen bei ungültigen Daten

## Status-Anzeigen

### Server erreichbar:
- ✅ "X Bücher vom Server geladen"
- ✅ "Bücher erfolgreich gespeichert (X Bücher)"

### Server nicht erreichbar:
- 📁 "X Bücher von lokaler Datei geladen"
- ❌ "Speichern fehlgeschlagen"
- 💡 "Bitte YAML manuell herunterladen"

## Troubleshooting

### Server startet nicht:
1. Python3 installiert? `python3 --version`
2. Flask installiert? `pip3 install Flask flask-cors PyYAML`
3. Port 5002 belegt? `lsof -i :5002`

### Änderungen werden nicht gespeichert:
1. API-Server läuft? Check Browser Console (F12)
2. CORS-Fehler? Server neu starten
3. Fallback: Manueller Export verwenden

### Backup wiederherstellen:
1. Gehe zu `data/_backups/`
2. Kopiere gewünschte Backup-Datei
3. Benenne um zu `Meine_Buchliste.yaml`
4. Ersetze originale Datei

## API-Endpunkte

- `GET /api/books` - Bücher laden
- `POST /api/books` - Bücher speichern
- `POST /api/books/validate` - Daten validieren
- `GET /api/backups` - Backups auflisten
- `GET /health` - Server-Status

## Sicherheit

- Server läuft nur lokal (localhost)
- Automatische Backups vor Änderungen
- Validierung der Eingabedaten
- Fehlerbehandlung mit Fallback-Optionen
