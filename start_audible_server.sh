#!/bin/bash

# Start Audible API Server
# Dieses Skript startet den lokalen Audible API Server für die Buchsuche

echo "🚀 Starte Audible API Server..."
echo "📚 Für die Audible-Suchfunktion im Buch-Editor"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 ist nicht installiert oder nicht im PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "data/audible_api_server.py" ]; then
    echo "❌ Audible API Server nicht gefunden."
    echo "   Bitte führen Sie dieses Skript aus dem Hauptverzeichnis aus."
    exit 1
fi

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "📦 Erstelle Python Virtual Environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Aktiviere Virtual Environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installiere Python-Abhängigkeiten..."
pip install -r data/requirements_audible.txt

echo ""
echo "🌟 Audible API Server wird gestartet..."
echo "📍 URL: http://localhost:5001"
echo "🔍 Test: http://localhost:5001/api/health"
echo ""
echo "💡 Tipp: Öffnen Sie jetzt book-editor.html und verwenden Sie die Audible-Suche!"
echo "🛑 Zum Beenden: Strg+C"
echo ""

# Start the server
cd data
python audible_api_server.py
