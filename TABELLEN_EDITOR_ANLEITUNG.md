# Buch Tabellen-Editor

Der Tabellen-Editor bietet eine **tabellarische Ansicht** für die effiziente Bearbeitung Ihrer Buchliste.

## ✨ Hauptfunktionen

### 📋 Tabellenansicht
- **Inline-Editing**: Klicken Sie auf eine Zelle zum direkten Bearbeiten
- **Sortierung**: Klicken Sie auf Spaltenüberschriften zum Sortieren
- **Spalten ein-/ausblenden**: Passen Sie die Ansicht an Ihre Bedürfnisse an
- **Sticky Columns**: ID-Spalte bleibt beim Scrollen sichtbar

### 🔍 Filter & Suche
- **Textsuche**: Durchsuchen Sie Titel, Autor, ISBN und Verlag
- **Genre-Filter**: Fiction / Nonfiction
- **Buchtyp-Filter**: Book / Audiobook / eBook
- **Echtzeit-Filterung**: Ergebnisse werden sofort angezeigt

### 📊 Statistiken
- Gesamtanzahl der Bücher
- Gefilterte Anzahl
- Durchschnittsbewertung
- Genre-Verteilung

### 📄 Pagination
- Einstellbare Seitengröße (25, 50, 100 oder alle)
- Navigation zwischen Seiten
- Aktuelle Position wird angezeigt

## 🛠️ Bearbeitungsfunktionen

### Zell-Typen
- **Text**: Titel, Autor, Verlag, etc.
- **Zahlen**: Jahr, Seiten, Bewertungen
- **Dropdown**: Genre, Buchtyp
- **Checkbox**: Bestseller-Status
- **Bilder**: Cover-Vorschau
- **Textarea**: Beschreibungen (mit Vorschau)

### Aktionen pro Buch
- **Details bearbeiten**: Öffnet den vollständigen Editor
- **Löschen**: Mit Bestätigungsdialog
- **Duplizieren**: Erstellt eine Kopie

### Bulk-Operationen
- **Neues Buch hinzufügen**: Mit Standard-Feldern
- **Alle speichern**: Speichert Änderungen an Server
- **Export**: YAML-Datei generieren

## ⌨️ Tastaturkürzel

- **Strg+N**: Neues Buch hinzufügen
- **Strg+S**: Alle Änderungen speichern
- **Strg+F**: Fokus auf Suchfeld
- **Enter**: Bearbeitung abschließen
- **Escape**: Bearbeitung abbrechen

## 💾 Speichern

### Automatisches Speichern
- Änderungen werden sofort im Speicher gespeichert
- Warnung vor ungespeicherten Änderungen beim Verlassen
- Server-Integration für permanente Speicherung

### Status-Anzeigen
- 📝 "Feld aktualisiert (nicht gespeichert)" - Lokale Änderung
- ✅ "Bücher erfolgreich gespeichert" - Server-Speicherung erfolgreich
- ❌ "Speichern fehlgeschlagen" - Fallback auf manuellen Export

## 🎯 Anwendungsfälle

### Schnelle Bearbeitung
- Bewertungen aktualisieren
- Serien-Nummern korrigieren
- Genre-Kategorisierung

### Datenbereinigung
- Duplikate finden und entfernen
- Fehlende Informationen ergänzen
- Einheitliche Formatierung

### Übersicht und Analyse
- Gesamtkollektion überblicken
- Statistiken einsehen
- Filter für spezielle Auswertungen

## 🔗 Integration

### Mit Book Editor
- **Details-Button**: Öffnet vollständigen Editor
- **Gleiche Datenquelle**: Synchrone Daten
- **URL-Parameter**: Direkter Zugriff auf spezielle Bücher

### Mit API-Server
- **Laden**: Bücher vom Server abrufen
- **Speichern**: Änderungen permanent speichern
- **Backups**: Automatische Sicherung

## 📱 Responsive Design

- **Desktop**: Vollständige Tabelle mit allen Funktionen
- **Tablet**: Angepasste Spaltenbreiten
- **Mobile**: Optimierte Navigation und Steuerung

## 🚀 Performance

- **Lazy Loading**: Nur sichtbare Zeilen werden gerendert
- **Pagination**: Große Datenmengen effizient verwalten
- **Optimierte Suche**: Schnelle Filter-Algorithmen

---

**Tipp**: Der Tabellen-Editor eignet sich perfekt für die **Batch-Bearbeitung** vieler Bücher, während der normale Book Editor ideal für **detaillierte Einzelbearbeitung** ist.
