#!/usr/bin/env python3
"""
Debug-Script für Audible-Seiten-Struktur
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def debug_audible_page(url):
    """Debugge eine spezifische Audible-Seite"""
    print(f"🔍 Debugge Audible-Seite: {url}")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Titel finden
        print("📖 TITEL-SUCHE:")
        title_selectors = [
            'h1',
            '.bc-size-headline1',
            '.bc-size-headline2', 
            '[data-testid="title"]',
            '.product-title',
            '.bc-heading'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if len(title) > 5 and 'audible' not in title.lower():
                    print(f"  ✅ {selector}: {title}")
                    break
        
        # Beschreibung finden - alle möglichen Textelemente analysieren
        print("\\n📝 BESCHREIBUNGS-ANALYSE:")
        
        # Methode 1: Spezifische Selektoren
        desc_selectors = [
            '.bc-section[data-module="ProductSummary"]',
            '.product-summary',
            '.bc-expander-content',
            '[class*="summary"]',
            '[class*="description"]',
            '.bc-size-base.bc-text',
            'div.bc-text:not(.bc-size-caption)',
            '.editorial-summary'
        ]
        
        print("  🎯 Spezifische Selektoren:")
        for selector in desc_selectors:
            elements = soup.select(selector)
            for i, element in enumerate(elements[:3]):  # Nur die ersten 3 zeigen
                text = element.get_text(strip=True)
                if len(text) > 50:
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"    {selector}[{i}]: {preview}")
        
        # Methode 2: Alle Textblöcke analysieren
        print("\\n  📊 Textblock-Analyse (>100 Zeichen):")
        all_divs = soup.find_all(['div', 'p', 'span'], string=True)
        text_blocks = []
        
        for div in all_divs:
            text = div.get_text(strip=True) if div else ""
            if (len(text) > 100 and 
                'navigation' not in text.lower() and
                'menü' not in text.lower() and
                'cookie' not in text.lower() and
                'anmelden' not in text.lower() and
                'hotline' not in text.lower() and
                'std' not in text.lower() and
                'min' not in text.lower()):
                text_blocks.append((text, div.name, div.get('class', [])))
        
        # Sortiere nach Länge
        text_blocks.sort(key=lambda x: len(x[0]), reverse=True)
        
        for i, (text, tag, classes) in enumerate(text_blocks[:5]):
            preview = text[:150] + "..." if len(text) > 150 else text
            class_str = " ".join(classes) if classes else "no-class"
            print(f"    Block {i+1} ({tag}.{class_str}): {preview}")
        
        # Methode 3: Spezielle Muster suchen
        print("\\n  🔍 Beschreibungsmuster-Suche:")
        page_text = soup.get_text()
        
        patterns = [
            (r'Beschreibung[:\s]+(.*?)(?=\n\n|\n[A-Z]|Autor|Sprecher|\\d+ Std)', 'Beschreibung-Pattern'),
            (r'Inhalt[:\s]+(.*?)(?=\n\n|\n[A-Z]|Autor|Sprecher|\\d+ Std)', 'Inhalt-Pattern'),
            (r'Klappentext[:\s]+(.*?)(?=\n\n|\n[A-Z]|Autor|Sprecher|\\d+ Std)', 'Klappentext-Pattern'),
            (r'(\\b\\w+.*?ist.*?\\w+.*?[.!?])(?=\\s*\\n|\\s*\\d+ Std)', 'Ist-Satz-Pattern'),
            (r'(\\b\\w+.*?war.*?\\w+.*?[.!?])(?=\\s*\\n|\\s*\\d+ Std)', 'War-Satz-Pattern')
        ]
        
        for pattern, name in patterns:
            matches = re.findall(pattern, page_text, re.DOTALL | re.I)
            for i, match in enumerate(matches[:2]):  # Nur erste 2 Treffer
                clean_match = re.sub(r'\\s+', ' ', match).strip()
                if len(clean_match) > 50:
                    preview = clean_match[:100] + "..." if len(clean_match) > 100 else clean_match
                    print(f"    {name}[{i}]: {preview}")
        
        print("\\n" + "=" * 60)
        print("✅ Debug-Analyse abgeschlossen")
        
    except Exception as e:
        print(f"❌ Fehler beim Debuggen: {e}")

if __name__ == "__main__":
    # Teste mit einem bekannten Harry Potter Buch
    test_url = "https://www.audible.de/pd/Harry-Potter-und-der-Stein-der-Weisen-Gesprochen-von-Rufus-Beck-Hoerbuch/B01M02FJ7A"
    debug_audible_page(test_url)
