@echo off
echo 🚀 Starte Audible API Server...
echo 📚 Für die Audible-Suchfunktion im Buch-Editor
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert oder nicht im PATH
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "data\audible_api_server.py" (
    echo ❌ Audible API Server nicht gefunden.
    echo    Bitte führen Sie dieses Skript aus dem Hauptverzeichnis aus.
    pause
    exit /b 1
)

REM Check if virtual environment exists, if not create one
if not exist "venv" (
    echo 📦 Erstelle Python Virtual Environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Aktiviere Virtual Environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📚 Installiere Python-Abhängigkeiten...
pip install -r data\requirements_audible.txt

echo.
echo 🌟 Audible API Server wird gestartet...
echo 📍 URL: http://localhost:5001
echo 🔍 Test: http://localhost:5001/api/health
echo.
echo 💡 Tipp: Öffnen Sie jetzt book-editor.html und verwenden Sie die Audible-Suche!
echo 🛑 Zum Beenden: Strg+C
echo.

REM Start the server
cd data
python audible_api_server.py

pause
