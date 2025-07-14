#!/usr/bin/env python3
"""
Flask API Server für Audible-Suche
Einfacher Server für den lokalen Betrieb der Audible-Scraping-Funktionalität
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audible_scraper import AudibleScraper

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

scraper = AudibleScraper()

@app.route('/api/audible/search', methods=['GET'])
def search_audible():
    """
    API Endpoint für Audible-Buchsuche
    Parameter: q (query), limit (max_results, default 10)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        results = scraper.search_books(query, limit)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audible/details', methods=['GET'])
def get_audible_details():
    """
    API Endpoint für detaillierte Buchinformationen
    Parameter: url (Audible-URL)
    """
    try:
        url = request.args.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400
        
        details = scraper.get_book_details(url)
        
        if details:
            return jsonify({
                'success': True,
                'details': details
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not fetch book details'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Audible API Server'
    })

@app.route('/', methods=['GET'])
def index():
    """
    API Information
    """
    return jsonify({
        'service': 'Audible API Server',
        'version': '1.0.0',
        'endpoints': {
            '/api/audible/search': 'Search for books (params: q, limit)',
            '/api/audible/details': 'Get book details (params: url)',
            '/api/health': 'Health check'
        }
    })

if __name__ == '__main__':
    print("Starting Audible API Server...")
    print("Server will be available at: http://localhost:5001")
    print("API Endpoints:")
    print("  - Search: http://localhost:5001/api/audible/search?q=QUERY")
    print("  - Details: http://localhost:5001/api/audible/details?url=AUDIBLE_URL")
    print("  - Health: http://localhost:5001/api/health")
    
    app.run(host='127.0.0.1', port=5001, debug=True)
