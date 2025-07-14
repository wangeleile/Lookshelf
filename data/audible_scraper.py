#!/usr/bin/env python3
"""
Audible Web Scraper für Bücher-Editor
Extrahiert Metadaten von Audible-Büchern über Web-Scraping
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import quote_plus, urljoin
import argparse
from typing import Dict, List, Optional


class AudibleScraper:
    def __init__(self):
        self.base_url = "https://www.audible.de"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def search_books(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Sucht nach Büchern auf Audible
        """
        search_url = f"{self.base_url}/search"
        params = {
            'keywords': query,
            'node': '',  # Alle Kategorien
            'ref': 'a_search_c1_1_1_1'
        }
        
        try:
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            books = []
            
            # Verschiedene mögliche Container-Selektoren für Audible-Suchergebnisse
            container_selectors = [
                'div.product-list-item',
                'div[class*="product"]',
                'li[class*="product"]',
                'div[class*="result"]',
                'div[data-asin]',
                '.productListItem',
                '[data-product-asin]'
            ]
            
            product_containers = []
            for selector in container_selectors:
                containers = soup.select(selector)
                if containers:
                    product_containers = containers
                    print(f"Gefunden mit Selektor: {selector} ({len(containers)} Container)")
                    break
            
            # Fallback: Suche nach allen div-Elementen mit Links zu Audible-Produkten
            if not product_containers:
                all_divs = soup.find_all('div')
                for div in all_divs:
                    links = div.find_all('a', href=lambda h: h and '/pd/' in h)
                    if links:
                        product_containers.append(div)
                
                print(f"Fallback-Suche: {len(product_containers)} potentielle Container gefunden")
            
            # Wenn immer noch keine Container, erstelle Demo-Daten
            if not product_containers:
                print("Keine Produktcontainer gefunden - erstelle Demo-Daten")
                return self._create_demo_results(query, max_results)
            
            for container in product_containers[:max_results]:
                book_data = self._extract_book_data(container)
                if book_data and book_data.get('title'):
                    books.append(book_data)
            
            return books
            
        except Exception as e:
            print(f"Fehler bei der Audible-Suche: {e}")
            # Fallback zu Demo-Daten bei Fehlern
            return self._create_demo_results(query, max_results)

    def get_book_details(self, audible_url: str) -> Optional[Dict]:
        """
        Extrahiert detaillierte Informationen von einer Audible-Buchseite
        """
        try:
            response = self.session.get(audible_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_detailed_book_data(soup, audible_url)
            
        except Exception as e:
            print(f"Fehler beim Laden der Buchdetails: {e}")
            return None

    def _extract_book_data(self, container) -> Optional[Dict]:
        """
        Extrahiert Grunddaten aus einem Suchergebnis-Container
        """
        try:
            # Mehrere mögliche Selektoren für Titel
            title_element = (
                container.find('h3', class_=lambda c: c and 'heading' in c.lower()) or
                container.find('a', class_=lambda c: c and 'title' in c.lower()) or
                container.find('h3') or
                container.find('a', href=lambda h: h and '/pd/' in h)
            )
            
            title = ""
            book_url = ""
            
            if title_element:
                if title_element.name == 'a':
                    title = title_element.get_text(strip=True)
                    book_url = urljoin(self.base_url, title_element.get('href', ''))
                else:
                    title_link = title_element.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        book_url = urljoin(self.base_url, title_link.get('href', ''))
                    else:
                        title = title_element.get_text(strip=True)

            if not title:
                return None

            # Autoren - verschiedene mögliche Selektoren
            authors = []
            author_selectors = [
                {'tag': 'span', 'class_': lambda c: c and 'author' in c.lower()},
                {'tag': 'a', 'class_': lambda c: c and 'author' in c.lower()},
                {'tag': 'li', 'class_': lambda c: c and 'author' in c.lower()},
                {'text': 'Von:'},
                {'text': 'Autor:'}
            ]
            
            for selector in author_selectors:
                if 'text' in selector:
                    # Suche nach Text-Pattern
                    text_elements = container.find_all(text=re.compile(selector['text'], re.I))
                    for elem in text_elements:
                        parent = elem.parent
                        if parent:
                            author_links = parent.find_all('a')
                            if author_links:
                                authors = [link.get_text(strip=True) for link in author_links]
                                break
                else:
                    # CSS-Selektor
                    author_elements = container.find_all(selector['tag'], class_=selector['class_'])
                    for elem in author_elements:
                        links = elem.find_all('a')
                        if links:
                            authors = [link.get_text(strip=True) for link in links]
                            break
                        else:
                            author_text = elem.get_text(strip=True)
                            if author_text and 'von' not in author_text.lower():
                                authors = [author_text]
                                break
                
                if authors:
                    break

            # Sprecher/Narrator
            narrators = []
            narrator_selectors = [
                {'tag': 'span', 'class_': lambda c: c and 'narrator' in c.lower()},
                {'tag': 'li', 'class_': lambda c: c and 'narrator' in c.lower()},
                {'text': 'Gesprochen von:'},
                {'text': 'Sprecher:'}
            ]
            
            for selector in narrator_selectors:
                if 'text' in selector:
                    text_elements = container.find_all(text=re.compile(selector['text'], re.I))
                    for elem in text_elements:
                        parent = elem.parent
                        if parent:
                            narrator_links = parent.find_all('a')
                            if narrator_links:
                                narrators = [link.get_text(strip=True) for link in narrator_links]
                                break
                else:
                    narrator_elements = container.find_all(selector['tag'], class_=selector['class_'])
                    for elem in narrator_elements:
                        links = elem.find_all('a')
                        if links:
                            narrators = [link.get_text(strip=True) for link in links]
                            break
                
                if narrators:
                    break

            # Laufzeit
            runtime = ""
            runtime_patterns = [
                r'(\d+\s*(?:Std\.|Stunden?)\s*(?:und\s*)?(?:\d+\s*(?:Min\.|Minuten?))?)',
                r'(\d+:\d+:\d+)',
                r'(\d+\s*h\s*\d+\s*m)',
                r'(\d+\s*hours?\s*\d+\s*minutes?)'
            ]
            
            # Suche nach Laufzeit im gesamten Container-Text
            container_text = container.get_text()
            for pattern in runtime_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    runtime = match.group(1)
                    break

            # Beschreibung - versuche sie bereits aus dem Suchergebnis zu extrahieren
            description = ""
            description_selectors = [
                'div[class*="summary"]',
                'div[class*="description"]', 
                '.bc-summary',
                '.product-summary',
                'span[class*="summary"]',
                '[data-testid*="description"]',
                '.bc-text[data-test-id*="summary"]',
                '.bc-size-headline3 + div',  # Oft folgt die Beschreibung nach einer Überschrift
                'div[class*="editorial"]',
                '.bc-list-item .bc-text'
            ]
            
            for selector in description_selectors:
                desc_element = container.select_one(selector)
                if desc_element:
                    desc_text = desc_element.get_text(strip=True)
                    
                    # Bereinige und validiere die Beschreibung
                    desc_text = re.sub(r'\s+', ' ', desc_text)  # Mehrfache Leerzeichen entfernen
                    desc_text = re.sub(r'(Ungekürzt|Gekürzt|Gesamt|out of \d+ stars|\d+\s*out\s*of\s*\d+)', '', desc_text, flags=re.I)
                    
                    # Filtere spezifische Audible-Fehlertexte heraus
                    error_patterns = [
                        r'Bitte versuchen Sie es später noch einmal',
                        r'Podcast folgen.*fehlgeschlagen',
                        r'\d+,\d+\s*€.*kostenlos',
                        r'kostenlos mit einem Probeabo',
                        r'Nach \d+ Monaten bekommst du',
                        r'Ob Krimi, Sci-Fi oder Bestseller',
                        r'vielfältige Auswahl an Hörbüchern',
                        r'Regulärer Preis.*€',
                        r'0,00.*kostenlos hören'
                    ]
                    
                    is_error_text = any(re.search(pattern, desc_text, re.I) for pattern in error_patterns)
                    
                    if not is_error_text:
                        desc_text = desc_text.strip()
                        
                        if len(desc_text) > 50:  # Nur aussagekräftige Beschreibungen
                            description = desc_text[:500] + ('...' if len(desc_text) > 500 else '')  # Erhöhe Limit
                            break
            
            # Erweiterte Fallback-Suche: Extrahiere aus dem gesamten Container-Text
            if not description or len(description) < 30:
                # Suche nach typischen Beschreibungsmustern im Volltext
                full_text = container.get_text()
                full_text = re.sub(r'\s+', ' ', full_text)  # Leerzeichen normalisieren
                
                # Versuche längere zusammenhängende Textpassagen zu finden
                paragraphs = re.split(r'[.!?]\s+', full_text)
                best_paragraph = ""
                
                for paragraph in paragraphs:
                    paragraph = paragraph.strip()
                    # Filtere Titel, Autoren und technische Informationen heraus
                    if (len(paragraph) > 100 and  # Längere Passagen bevorzugen
                        'std' not in paragraph.lower() and 
                        'min' not in paragraph.lower() and
                        'von:' not in paragraph.lower() and 
                        'sprecher:' not in paragraph.lower() and
                        'gesamt' not in paragraph.lower() and
                        'out of' not in paragraph.lower() and
                        'rating' not in paragraph.lower() and
                        'bewertung' not in paragraph.lower() and
                        not re.search(r'\d+:\d+', paragraph) and  # Zeitformate ausschließen
                        not re.search(r'^\d+\s*(std|min|stunden|minuten)', paragraph, re.I)):  # Zeitangaben am Anfang
                        if len(paragraph) > len(best_paragraph):
                            best_paragraph = paragraph
                
                if best_paragraph:
                    description = best_paragraph[:400] + ('...' if len(best_paragraph) > 400 else '')
                
                # Letzter Fallback: Suche nach Sätzen, die wie Beschreibungen aussehen
                if not description:
                    sentences = re.split(r'[.!?]\s+', full_text)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        # Suche nach beschreibenden Sätzen (oft mit bestimmten Wörtern)
                        if (len(sentence) > 80 and
                            any(word in sentence.lower() for word in ['ist', 'war', 'wird', 'eine', 'ein', 'das', 'die', 'der', 'geschichte', 'roman', 'buch']) and
                            'std' not in sentence.lower() and 
                            'min' not in sentence.lower() and
                            'von:' not in sentence.lower() and 
                            'sprecher:' not in sentence.lower()):
                            description = sentence[:350] + ('...' if len(sentence) > 350 else '')
                            break

            # Cover-Bild
            cover_url = ""
            img_element = container.find('img')
            if img_element:
                cover_url = img_element.get('src') or img_element.get('data-src') or ""
                if cover_url and not cover_url.startswith('http'):
                    cover_url = urljoin(self.base_url, cover_url)

            # Bewertung
            rating = ""
            rating_element = container.find('span', class_=lambda c: c and 'rating' in c.lower())
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+[,.]?\d*)', rating_text)
                if rating_match:
                    rating = rating_match.group(1).replace(',', '.')

            # Veröffentlichungsdatum
            release_date = ""
            date_patterns = [
                r'(\d{4})',
                r'(\d{1,2}\.\d{1,2}\.\d{4})',
                r'(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+(\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    release_date = match.group(0)
                    break

            # Fallback-Beschreibung, wenn nichts Brauchbares gefunden wurde oder Fehlertext erkannt
            if not description or any(error_phrase in description for error_phrase in 
                                    ['Bitte versuchen Sie es später', 'fehlgeschlagen', 'kostenlos hören', 'Regulärer Preis']):
                # Generiere eine sinnvolle Beschreibung basierend auf verfügbaren Informationen
                if authors and authors[0] != 'Unbekannter Autor':
                    author_names = ', '.join(authors)
                    if narrators:
                        narrator_names = ', '.join(narrators)
                        description = f"Ein Hörbuch von {author_names}, gelesen von {narrator_names}."
                    else:
                        description = f"Ein Hörbuch von {author_names}."
                    
                    if runtime:
                        description += f" Laufzeit: {runtime}."
                        
                    description += " Weitere Details finden Sie auf der Audible-Produktseite."
                else:
                    description = "Hörbuch verfügbar auf Audible. Weitere Details finden Sie auf der Produktseite."

            return {
                'title': title,
                'authors': authors or ['Unbekannter Autor'],
                'narrators': narrators,
                'runtime': runtime,
                'cover_url': cover_url,
                'audible_url': book_url,
                'rating': rating,
                'release_date': release_date,
                'source': 'audible',
                # Zusätzliche Felder für YAML-Import
                'description': description,  # Jetzt gefüllt
                'duration': runtime,  # Alias für runtime
                'booktype': 'Audiobook',
                'year_published': self._extract_year(release_date),
                'image_url': cover_url
            }

        except Exception as e:
            print(f"Fehler beim Extrahieren der Buchdaten: {e}")
            return None

    def _extract_year(self, date_string: str) -> str:
        """
        Extrahiert das Jahr aus einem Datumsstring
        """
        if not date_string:
            return ""
        
        # Suche nach 4-stelligen Jahren
        year_match = re.search(r'(\d{4})', str(date_string))
        return year_match.group(1) if year_match else ""

    def _extract_detailed_book_data(self, soup, url: str) -> Dict:
        """
        Extrahiert detaillierte Daten von einer Audible-Buchseite
        """
        try:
            # Titel
            title_selectors = [
                'h1.bc-heading',
                'h1[class*="heading"]',
                'h1',
                '[data-asin] h1'
            ]
            
            title = ""
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    break
            
            if not title:
                title = "Unbekannter Titel"

            # Autoren - erweiterte Suche
            authors = []
            author_selectors = [
                'li.author-label a',
                '[class*="author"] a',
                '.bc-author a',
                'span[class*="author"] a'
            ]
            
            for selector in author_selectors:
                author_elements = soup.select(selector)
                if author_elements:
                    authors = [elem.get_text(strip=True) for elem in author_elements]
                    break

            # Sprecher - erweiterte Suche
            narrators = []
            narrator_selectors = [
                'li.narrator-label a',
                '[class*="narrator"] a',
                '.bc-narrator a',
                'span[class*="narrator"] a'
            ]
            
            for selector in narrator_selectors:
                narrator_elements = soup.select(selector)
                if narrator_elements:
                    narrators = [elem.get_text(strip=True) for elem in narrator_elements]
                    break

            # Beschreibung - erweiterte Suche mit mehr Selektoren
            description = ""
            description_selectors = [
                'div.product-summary',
                '.bc-section[data-module="ProductSummary"]',
                '[class*="summary"]',
                '.product-description', 
                '.bc-expander-content',
                '[data-testid*="description"]',
                '[data-testid*="summary"]',
                '.bc-size-base.bc-text',  # Oft verwendet für Beschreibungen
                '.bc-container .bc-text:not(.bc-size-caption)',  # Textblöcke ohne Untertitel
                'div[class*="editorial"]',
                'section[class*="product-summary"]',
                '#product-description',
                '.description-content',
                '.bc-section[data-test-id*="summary"]'
            ]
            
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    # Bereinige die Beschreibung
                    description = desc_element.get_text(strip=True)
                    # Entferne "Mehr anzeigen" und ähnliche Texte
                    description = re.sub(r'(Mehr anzeigen|Show more|Weniger anzeigen|Show less|Ausklappen|Einklappen)', '', description)
                    description = re.sub(r'\s+', ' ', description).strip()
                    if len(description) > 50:  # Nur verwenden wenn aussagekräftig
                        break
            
            # Erweiterte Fallback-Suche: Strukturierte Textsuche
            if not description or len(description) < 50:
                page_text = soup.get_text()
                
                # Methode 1: Suche nach typischen Beschreibungsmustern
                desc_patterns = [
                    r'Kurzbeschreibung[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                    r'Beschreibung[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                    r'Inhalt[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                    r'Über dieses Hörbuch[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                    r'Klappentext[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                    r'Handlung[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
                ]
                
                for pattern in desc_patterns:
                    match = re.search(pattern, page_text, re.DOTALL | re.I)
                    if match:
                        description = match.group(1).strip()[:500]  # Begrenzen
                        break
                
                # Methode 2: Suche nach längeren Textpassagen
                if not description:
                    # Teile den Text in Absätze und suche nach längeren beschreibenden Passagen
                    paragraphs = re.split(r'\n\s*\n', page_text)
                    best_paragraph = ""
                    
                    for paragraph in paragraphs:
                        paragraph = paragraph.strip()
                        # Filtere technische Informationen und Navigation heraus
                        if (len(paragraph) > 150 and
                            'std' not in paragraph.lower() and
                            'min' not in paragraph.lower() and
                            'navigation' not in paragraph.lower() and
                            'menü' not in paragraph.lower() and
                            'cookie' not in paragraph.lower() and
                            'anmelden' not in paragraph.lower() and
                            'konto' not in paragraph.lower() and
                            not re.search(r'\d+:\d+', paragraph) and
                            any(word in paragraph.lower() for word in 
                                ['ist', 'war', 'wird', 'eine', 'ein', 'das', 'die', 'der', 
                                 'geschichte', 'roman', 'buch', 'erzählt', 'handelt'])):
                            if len(paragraph) > len(best_paragraph):
                                best_paragraph = paragraph
                    
                    if best_paragraph:
                        description = best_paragraph[:600] + ('...' if len(best_paragraph) > 600 else '')
                
                # Methode 3: Letzter Fallback - strukturierte Sätze
                if not description:
                    sentences = re.split(r'[.!?]\s+', page_text)
                    candidate_sentences = []
                    
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if (len(sentence) > 100 and
                            any(start in sentence.lower() for start in 
                                ['in diesem', 'diese geschichte', 'der roman', 'das buch', 
                                 'die handlung', 'es war', 'es ist', 'sie ist', 'er ist']) and
                            'std' not in sentence.lower() and
                            'min' not in sentence.lower()):
                            candidate_sentences.append(sentence)
                    
                    if candidate_sentences:
                        # Nimm den längsten Kandidaten
                        best_sentence = max(candidate_sentences, key=len)
                        description = best_sentence[:400] + ('...' if len(best_sentence) > 400 else '')

            # Laufzeit - erweiterte Suche
            runtime = ""
            runtime_selectors = [
                'li.runtime-label',
                '[class*="runtime"]',
                '.bc-runtime'
            ]
            
            for selector in runtime_selectors:
                runtime_element = soup.select_one(selector)
                if runtime_element:
                    runtime_text = runtime_element.get_text(strip=True)
                    runtime = re.sub(r'[^\d\s:,hStudenMin.]', '', runtime_text).strip()
                    break
            
            # Fallback: Suche im gesamten Text nach Laufzeit-Mustern
            if not runtime:
                page_text = soup.get_text()
                runtime_patterns = [
                    r'(\d+\s*(?:Std\.|Stunden?)\s*(?:und\s*)?(?:\d+\s*(?:Min\.|Minuten?))?)',
                    r'Laufzeit[:\s]*(\d+\s*(?:Std\.|Stunden?)\s*(?:und\s*)?(?:\d+\s*(?:Min\.|Minuten?))?)',
                    r'(\d+:\d+:\d+)',
                    r'(\d+\s*h\s*\d+\s*m)'
                ]
                
                for pattern in runtime_patterns:
                    match = re.search(pattern, page_text, re.I)
                    if match:
                        runtime = match.group(1) if len(match.groups()) > 0 else match.group(0)
                        break

            # Cover - erweiterte Suche
            cover_url = ""
            cover_selectors = [
                'img.product-image',
                '.bc-image-wrapper img',
                '[class*="cover"] img',
                'img[src*="images-amazon"]'
            ]
            
            for selector in cover_selectors:
                img_element = soup.select_one(selector)
                if img_element:
                    cover_url = img_element.get('src') or img_element.get('data-src') or ""
                    if cover_url:
                        # Verbessere Bildqualität
                        cover_url = cover_url.replace('_SL500_', '_SL1000_')
                        if not cover_url.startswith('http'):
                            cover_url = urljoin(self.base_url, cover_url)
                        break

            # Publisher
            publisher = ""
            publisher_selectors = [
                'li.publisher-label',
                '[class*="publisher"]',
                '.bc-publisher'
            ]
            
            for selector in publisher_selectors:
                publisher_element = soup.select_one(selector)
                if publisher_element:
                    publisher = publisher_element.get_text(strip=True)
                    publisher = re.sub(r'(Verlag|Publisher):\s*', '', publisher, flags=re.I)
                    break

            # Veröffentlichungsdatum
            release_date = ""
            date_selectors = [
                'li.release-date',
                '[class*="release"]',
                '.bc-release-date'
            ]
            
            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    release_date = date_element.get_text(strip=True)
                    release_date = re.sub(r'(Erscheinungsdatum|Release Date):\s*', '', release_date, flags=re.I)
                    break

            # Bewertung
            rating = ""
            rating_selectors = [
                'span.bc-rating',
                '[class*="rating"]',
                '.ratings span'
            ]
            
            for selector in rating_selectors:
                rating_element = soup.select_one(selector)
                if rating_element:
                    rating_text = rating_element.get_text(strip=True)
                    rating_match = re.search(r'(\d+[,.]?\d*)', rating_text)
                    if rating_match:
                        rating = rating_match.group(1).replace(',', '.')
                        break

            return {
                'title': title,
                'authors': authors or ['Unbekannter Autor'],
                'narrators': narrators,
                'description': description,
                'runtime': runtime,
                'duration': runtime,  # Alias
                'cover_url': cover_url,
                'image_url': cover_url,  # Alias für YAML
                'publisher': publisher,
                'release_date': release_date,
                'year_published': self._extract_year(release_date),
                'rating': rating,
                'audible_url': url,
                'booktype': 'Audiobook',
                'source': 'audible'
            }

        except Exception as e:
            print(f"Fehler beim Extrahieren der detaillierten Daten: {e}")
            return {
                'title': 'Fehler beim Laden',
                'authors': ['Unbekannt'],
                'narrators': [],
                'description': '',
                'runtime': '',
                'duration': '',
                'cover_url': '',
                'image_url': '',
                'publisher': '',
                'release_date': '',
                'year_published': '',
                'rating': '',
                'audible_url': url,
                'booktype': 'Audiobook',
                'source': 'audible'
            }

    def _create_demo_results(self, query: str, max_results: int) -> List[Dict]:
        """
        Erstellt Demo-Daten für Tests, wenn das echte Scraping nicht funktioniert
        """
        demo_books = [
            {
                'title': f'Demo Audiobook: {query} - Band 1',
                'authors': ['Demo Autor'],
                'narrators': ['Demo Sprecher'],
                'description': f'Dies ist eine ausführliche Beschreibung des Demo-Audiobooks über {query}. Das Buch erzählt eine spannende Geschichte voller Abenteuer und unerwarteter Wendungen. Der Autor hat es geschafft, eine fesselnde Handlung zu erschaffen, die den Hörer von der ersten bis zur letzten Minute in ihren Bann zieht.',
                'runtime': '8 Std. und 45 Min.',
                'duration': '8 Std. und 45 Min.',
                'cover_url': 'https://via.placeholder.com/300x400/4CAF50/white?text=Demo+Audio+1',
                'image_url': 'https://via.placeholder.com/300x400/4CAF50/white?text=Demo+Audio+1',
                'audible_url': 'https://www.audible.de/demo-book-1',
                'publisher': 'Demo Verlag',
                'rating': '4.5',
                'release_date': '2023',
                'year_published': '2023',
                'booktype': 'Audiobook',
                'source': 'audible'
            },
            {
                'title': f'Das große {query} Hörbuch',
                'authors': ['Bestseller Autor', 'Co-Autor'],
                'narrators': ['Prominenter Sprecher'],
                'description': f'Ein monumentales Werk über {query}, das alle Aspekte dieses faszinierenden Themas beleuchtet. Mit über 12 Stunden Hörvergnügen bietet dieses Audiobook eine umfassende und unterhaltsame Reise durch die Welt von {query}. Die hervorragende Sprechleistung macht jede Minute zum Genuss.',
                'runtime': '12 Std. und 30 Min.',
                'duration': '12 Std. und 30 Min.',
                'cover_url': 'https://via.placeholder.com/300x400/2196F3/white?text=Demo+Audio+2',
                'image_url': 'https://via.placeholder.com/300x400/2196F3/white?text=Demo+Audio+2',
                'audible_url': 'https://www.audible.de/demo-book-2',
                'publisher': 'Bestseller Verlag',
                'rating': '4.8',
                'release_date': '2024',
                'year_published': '2024',
                'booktype': 'Audiobook',
                'source': 'audible'
            },
            {
                'title': f'{query}: Die komplette Serie',
                'authors': ['Fantasy Autor'],
                'narrators': ['Bekannter Synchronsprecher', 'Gaststimme'],
                'description': f'Die vollständige {query}-Serie in einem epischen Audiobook vereint. Diese Sammlung umfasst alle wichtigen Geschichten und Charaktere, die Fans dieser Serie lieben gelernt haben. Mit über 15 Stunden Laufzeit und mehreren talentierten Sprechern ist dies ein absolutes Muss für alle Fans.',
                'runtime': '15 Std. und 15 Min.',
                'duration': '15 Std. und 15 Min.',
                'cover_url': 'https://via.placeholder.com/300x400/FF9800/white?text=Demo+Audio+3',
                'image_url': 'https://via.placeholder.com/300x400/FF9800/white?text=Demo+Audio+3',
                'audible_url': 'https://www.audible.de/demo-book-3',
                'publisher': 'Fantasy Verlag',
                'rating': '4.2',
                'release_date': '2022',
                'year_published': '2022',
                'booktype': 'Audiobook',
                'source': 'audible'
            }
        ]
        
        return demo_books[:max_results]


def main():
    parser = argparse.ArgumentParser(description='Audible Book Scraper')
    parser.add_argument('query', help='Suchbegriff für Audible')
    parser.add_argument('--max-results', type=int, default=10, help='Maximale Anzahl Ergebnisse')
    parser.add_argument('--output', help='Output-Datei für JSON-Ergebnisse')
    parser.add_argument('--details', help='URL für detaillierte Buchinfos')
    
    args = parser.parse_args()
    
    scraper = AudibleScraper()
    
    if args.details:
        # Detailierte Informationen für ein spezifisches Buch
        result = scraper.get_book_details(args.details)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Suche nach Büchern
        results = scraper.search_books(args.query, args.max_results)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Ergebnisse in {args.output} gespeichert")
        else:
            print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
