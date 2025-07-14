# Audible-Suchfunktionalität

## Übersicht
Die Audible-Suchfunktionalität ermöglicht es, Audiobooks direkt von Audible.de zu suchen und in den Buch-Editor zu importieren. Da Audible keine öffentliche API bereitstellt, wird Web-Scraping verwendet.

## Features
- 🔍 Suche nach Audiobooks auf Audible.de
- 📖 Automatischer Import von Metadaten (Titel, Autor, Sprecher, Laufzeit, etc.)
- 🖼️ Buchcover-Integration
- ⭐ Bewertungen und Release-Daten
- 🎧 Spezielle Audiobook-Felder (Sprecher, Laufzeit)

## Installation und Setup

### 1. Abhängigkeiten installieren
```bash
# Automatisch über Start-Skript (empfohlen)
./start_audible_server.sh

# Oder manuell:
pip install -r data/requirements_audible.txt
```

### 2. Server starten

#### macOS/Linux:
```bash
./start_audible_server.sh
```

#### Windows:
```cmd
start_audible_server.bat
```

#### Manuell:
```bash
cd data
python audible_api_server.py
```

### 3. Server-Status prüfen
- Öffnen Sie: http://localhost:5001/api/health
- Sie sollten eine JSON-Antwort mit `"status": "healthy"` sehen

## Verwendung

### Im Buch-Editor (book-editor.html):

1. **Externe Suche verwenden:**
   - Geben Sie einen Suchbegriff ein
   - Wählen Sie "Audible (Audiobooks)" als Quelle
   - Oder verwenden Sie "Auto" - Audiobook-Begriffe werden automatisch erkannt

2. **Unterstützte Suchbegriffe:**
   - Buchtitel: `"Der Herr der Ringe"`
   - Autor + Titel: `"Tolkien Herr der Ringe"`
   - Audiobook-spezifisch: `"Hörbuch Fantasy"`
   - Audible-URLs: Direkte Links zu Audible-Büchern

3. **Auto-Detection:**
   - Audiobook-Keywords: `audiobook`, `hörbuch`, `narrator`, `sprecher`, `audible`
   - Audible-URLs werden automatisch erkannt

### Importierte Daten:
- ✅ Titel
- ✅ Autor(en)
- ✅ Sprecher/Narrator
- ✅ Laufzeit
- ✅ Beschreibung
- ✅ Buchcover
- ✅ Bewertung
- ✅ Veröffentlichungsdatum
- ✅ Audible-URL

## API-Endpunkte

### Buchsuche
```
GET http://localhost:5001/api/audible/search?q=SUCHBEGRIFF&limit=10
```

**Parameter:**
- `q`: Suchbegriff (erforderlich)
- `limit`: Max. Anzahl Ergebnisse (optional, Standard: 10)

### Buchdetails
```
GET http://localhost:5001/api/audible/details?url=AUDIBLE_URL
```

**Parameter:**
- `url`: Vollständige Audible-URL (erforderlich)

### Health Check
```
GET http://localhost:5001/api/health
```

## Beispiel-Antworten

### Suchresultate:
```json
{
  "success": true,
  "query": "Harry Potter",
  "results": [
    {
      "title": "Harry Potter und der Stein der Weisen",
      "authors": ["J.K. Rowling"],
      "narrators": ["Rufus Beck"],
      "runtime": "9 Std. und 39 Min.",
      "cover_url": "https://...",
      "audible_url": "https://www.audible.de/...",
      "rating": "4.8",
      "release_date": "2017",
      "source": "audible"
    }
  ],
  "count": 1
}
```

## Problembehandlung

### Server startet nicht:
1. Python 3 installiert? `python3 --version`
2. Dependencies installiert? `pip install -r data/requirements_audible.txt`
3. Port 5001 bereits belegt? Ändern Sie den Port in `audible_api_server.py`

### Keine Suchergebnisse:
1. Server läuft? Prüfen Sie http://localhost:5001/api/health
2. Internetverbindung aktiv?
3. Audible.de erreichbar? (im Browser testen)

### CORS-Fehler:
- Der Server sollte automatisch CORS aktivieren
- Falls nicht, prüfen Sie die Flask-CORS Konfiguration

## Technische Details

### Web-Scraping:
- Verwendet BeautifulSoup für HTML-Parsing
- Requests für HTTP-Anfragen
- Robuste Fehlerbehandlung
- User-Agent Rotation zur Vermeidung von Blockierungen

### Sicherheit:
- Läuft nur lokal (127.0.0.1)
- Keine Speicherung persönlicher Daten
- Rate-Limiting implementiert

### Performance:
- Caching von Suchergebnissen
- Parallele Anfragen möglich
- Timeout-Konfiguration

## Erweiterte Konfiguration

### Anpassung der Suchergebnisse:
Bearbeiten Sie `audible_scraper.py`:
- `max_results`: Standard-Anzahl Ergebnisse
- CSS-Selektoren für andere Audible-Versionen
- Timeout-Werte

### Server-Konfiguration:
Bearbeiten Sie `audible_api_server.py`:
- Port ändern (Standard: 5001)
- Debug-Modus aktivieren/deaktivieren
- Logging-Level anpassen

## Rechtliche Hinweise
- Diese Software dient nur zu persönlichen, nicht-kommerziellen Zwecken
- Respektieren Sie die Nutzungsbedingungen von Audible
- Verwenden Sie das Scraping verantwortungsvoll
- Keine Weiterverbreitung der extrahierten Daten

## Support
Bei Problemen prüfen Sie:
1. Server-Logs in der Konsole
2. Browser-Konsole für JavaScript-Fehler
3. Network-Tab in den Browser-Entwicklertools
