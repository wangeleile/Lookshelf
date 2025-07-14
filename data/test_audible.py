#!/usr/bin/env python3
"""
Test-Skript für die Audible-Suchfunktionalität
"""

import sys
import os
import json
import requests
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audible_scraper import AudibleScraper


def test_direct_scraping():
    """Test der direkten Scraping-Funktionalität"""
    print("🧪 Teste Audible Scraper direkt...")
    
    scraper = AudibleScraper()
    
    # Test-Suche
    test_queries = [
        "Harry Potter",
        "Herr der Ringe",
        "Krimi"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Suche nach: '{query}'")
        try:
            results = scraper.search_books(query, max_results=3)
            if results:
                print(f"✅ {len(results)} Ergebnisse gefunden")
                for i, book in enumerate(results, 1):
                    print(f"  {i}. {book.get('title', 'Unbekannt')} - {', '.join(book.get('authors', []))}")
                    if book.get('narrators'):
                        print(f"     Sprecher: {', '.join(book['narrators'])}")
                    if book.get('runtime'):
                        print(f"     Laufzeit: {book['runtime']}")
            else:
                print("❌ Keine Ergebnisse")
        except Exception as e:
            print(f"❌ Fehler: {e}")
        
        time.sleep(1)  # Rate limiting


def test_api_server():
    """Test der API-Server-Funktionalität"""
    print("\n🌐 Teste Audible API Server...")
    
    base_url = "http://localhost:5001"
    
    # Health Check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server ist erreichbar")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
        else:
            print(f"❌ Server antwortet mit Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server nicht erreichbar. Starten Sie den Server mit:")
        print("   python audible_api_server.py")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Health Check: {e}")
        return False
    
    # Test API Search
    test_query = "Fantasy Hörbuch"
    print(f"\n🔍 API-Suche nach: '{test_query}'")
    try:
        response = requests.get(f"{base_url}/api/audible/search", 
                               params={'q': test_query, 'limit': 3}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('results', [])
                print(f"✅ {len(results)} Ergebnisse über API erhalten")
                for i, book in enumerate(results, 1):
                    print(f"  {i}. {book.get('title', 'Unbekannt')}")
            else:
                print(f"❌ API Fehler: {data.get('error')}")
        else:
            print(f"❌ API antwortet mit Status {response.status_code}")
    except Exception as e:
        print(f"❌ API-Fehler: {e}")
    
    return True


def test_browser_integration():
    """Test der Browser-Integration"""
    print("\n🌐 Browser-Integration Test...")
    print("Für den vollständigen Test:")
    print("1. Starten Sie den API Server: python audible_api_server.py")
    print("2. Öffnen Sie book-editor.html")
    print("3. Verwenden Sie die externe Suche mit 'Audible' als Quelle")
    print("4. Testen Sie Begriffe wie: 'Harry Potter', 'Krimi Hörbuch', 'Fantasy'")


def main():
    print("🚀 Audible-Funktionalität Testbericht")
    print("=" * 50)
    
    # Test 1: Direktes Scraping
    try:
        test_direct_scraping()
    except KeyboardInterrupt:
        print("\n⚠️ Test unterbrochen")
        return
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler beim direkten Scraping: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: API Server
    try:
        server_working = test_api_server()
    except KeyboardInterrupt:
        print("\n⚠️ Test unterbrochen")
        return
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler beim API Test: {e}")
        server_working = False
    
    print("\n" + "=" * 50)
    
    # Test 3: Browser Integration Info
    test_browser_integration()
    
    print("\n" + "=" * 50)
    print("📋 Zusammenfassung:")
    print("- Direktes Scraping: Implementiert")
    print(f"- API Server: {'✅ Funktioniert' if server_working else '❌ Nicht erreichbar'}")
    print("- Browser Integration: Implementiert (manuelle Tests erforderlich)")
    
    if not server_working:
        print("\n💡 Nächste Schritte:")
        print("1. Starten Sie den API Server: python audible_api_server.py")
        print("2. Führen Sie diesen Test erneut aus")
        print("3. Testen Sie die Integration in book-editor.html")


if __name__ == '__main__':
    main()
