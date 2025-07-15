#!/bin/bash

echo "🚀 Starte Book Editor API Server..."

# Prüfe ob Python verfügbar ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 ist nicht installiert!"
    exit 1
fi

# Prüfe ob Flask installiert ist
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Installiere Flask..."
    pip3 install Flask flask-cors PyYAML
fi

# Wechsle in das data Verzeichnis
cd "$(dirname "$0")/data"

# Starte den Server
echo "🌐 Server startet auf http://localhost:5002"
echo "📄 Verwende YAML-Datei: $(pwd)/Meine_Buchliste.yaml"
echo ""
echo "💡 Zum Beenden: Strg+C drücken"
echo ""

python3 book_editor_api.py
