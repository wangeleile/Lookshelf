class BookEditor {
    constructor() {
        this.books = [];
        this.currentIndex = 0;
        this.isNewBook = false;
        this.init();
    }

    async init() {
        await this.loadBooks();
        this.setupEventListeners();
        this.showBook(0);
        this.updateCounter();
    }

    async loadBooks() {
        try {
            const response = await fetch('data/Meine_Buchliste.yaml');
            const yamlText = await response.text();
            const data = jsyaml.load(yamlText);
            this.books = data.books || [];
            console.log(`${this.books.length} Bücher geladen`);
        } catch (error) {
            console.error('Fehler beim Laden der YAML-Datei:', error);
            this.showNotification('Fehler beim Laden der Buchdaten', 'is-danger');
            this.books = [];
        }
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('prevBtn').addEventListener('click', () => this.previousBook());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextBook());
        document.getElementById('firstBtn').addEventListener('click', () => this.firstBook());
        document.getElementById('lastBtn').addEventListener('click', () => this.lastBook());
        document.getElementById('jumpBtn').addEventListener('click', () => this.jumpToBook());
        
        // CRUD Operations
        document.getElementById('newBookBtn').addEventListener('click', () => this.newBook());
        document.getElementById('deleteBtn').addEventListener('click', () => this.deleteBook());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetForm());
        
        // Form
        document.getElementById('bookForm').addEventListener('submit', (e) => this.saveBook(e));
        
        // Search
        document.getElementById('searchInput').addEventListener('input', (e) => this.search(e.target.value));
        
        // External Search
        document.getElementById('externalSearchBtn').addEventListener('click', () => this.searchExternalBooks());
        document.getElementById('externalSearchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchExternalBooks();
        });
        
        // Export
        document.getElementById('exportBtn').addEventListener('click', () => this.exportYAML());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadYAML());
        document.getElementById('copyBtn').addEventListener('click', () => this.copyYAML());
        
        // Image preview
        document.querySelector('input[name="image_url"]').addEventListener('input', (e) => this.updateImagePreview(e.target.value));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    showBook(index) {
        if (index < 0 || index >= this.books.length) return;
        
        this.currentIndex = index;
        this.isNewBook = false;
        const book = this.books[index];
        
        // Fill form
        const form = document.getElementById('bookForm');
        const formData = new FormData(form);
        
        // Clear form first
        form.reset();
        
        // Fill with book data
        Object.keys(book).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = book[key] === true;
                } else {
                    input.value = book[key] || '';
                }
            }
        });
        
        this.updateImagePreview(book.image_url);
        this.updateCounter();
    }

    nextBook() {
        if (this.currentIndex < this.books.length - 1) {
            this.showBook(this.currentIndex + 1);
        }
    }

    previousBook() {
        if (this.currentIndex > 0) {
            this.showBook(this.currentIndex - 1);
        }
    }

    firstBook() {
        this.showBook(0);
    }

    lastBook() {
        this.showBook(this.books.length - 1);
    }

    jumpToBook() {
        const index = parseInt(document.getElementById('jumpToIndex').value) - 1;
        if (index >= 0 && index < this.books.length) {
            this.showBook(index);
        }
    }

    newBook() {
        this.isNewBook = true;
        document.getElementById('bookForm').reset();
        document.getElementById('imagePreview').innerHTML = '';
        this.updateCounter();
        this.showNotification('Neues Buch erstellen', 'is-info');
    }

    deleteBook() {
        if (this.isNewBook) {
            this.showNotification('Kein Buch zum Löschen ausgewählt', 'is-warning');
            return;
        }

        if (confirm('Sind Sie sicher, dass Sie dieses Buch löschen möchten?')) {
            this.books.splice(this.currentIndex, 1);
            
            // Adjust current index if needed
            if (this.currentIndex >= this.books.length) {
                this.currentIndex = this.books.length - 1;
            }
            
            if (this.books.length > 0) {
                this.showBook(this.currentIndex);
            } else {
                this.newBook();
            }
            
            this.showNotification('Buch gelöscht', 'is-success');
        }
    }

    resetForm() {
        if (this.isNewBook) {
            document.getElementById('bookForm').reset();
            document.getElementById('imagePreview').innerHTML = '';
        } else {
            this.showBook(this.currentIndex);
        }
    }

    saveBook(e) {
        e.preventDefault();
        
        const form = document.getElementById('bookForm');
        const formData = new FormData(form);
        const book = {};
        
        // Convert form data to book object
        for (let [key, value] of formData.entries()) {
            if (key === 'bestseller') {
                book[key] = form.querySelector(`[name="${key}"]`).checked;
            } else if (['year', 'pages', 'rating', 'My Rating', 'id', 'Serien Nr.'].includes(key)) {
                book[key] = value ? parseFloat(value) : null;
            } else {
                book[key] = value || null;
            }
        }

        // Add computed fields
        if (book.year) {
            book.year_asc = book.year;
            book.year_desc = -book.year;
        }
        if (book.rating) {
            book.rating_asc = book.rating;
            book.rating_desc = -book.rating;
        }

        // Add missing fields with defaults
        const defaultFields = {
            'Date Read': null,
            'Date Added': null,
            'My_Review': null,
            'Private Notes': null,
            'Read Count': 0,
            'PublishedDate': null,
            'PageCount': book.pages,
            'Categories': null,
            'Description': book.Description || null,
            'duration': book.duration || null,
            'gender': 'unknown',
            'language': book.language || 'Deutsch',
            'tags': null,
            'narrator': '',
            'rating_count': book.rating_count || '0',
            'myFav': false,
            'first_name': 'False',
            'last_name': 'False',
            'book_color': book.book_color || '#8B4513',
            'Binding': 'Paperback'
        };

        Object.keys(defaultFields).forEach(key => {
            if (!(key in book)) {
                book[key] = defaultFields[key];
            }
        });

        if (this.isNewBook) {
            // Generate new ID if not provided
            if (!book.id) {
                book.id = Math.max(...this.books.map(b => b.id || 0)) + 1;
            }
            
            this.books.push(book);
            this.currentIndex = this.books.length - 1;
            this.isNewBook = false;
            this.showNotification('Neues Buch hinzugefügt', 'is-success');
        } else {
            this.books[this.currentIndex] = book;
            this.showNotification('Buch aktualisiert', 'is-success');
        }
        
        this.updateCounter();
    }

    search(query) {
        const results = document.getElementById('searchResults');
        const resultsList = document.getElementById('searchResultsList');
        
        if (query.length < 2) {
            results.style.display = 'none';
            return;
        }

        const matches = this.books.filter((book, index) => {
            const searchText = `${book.title} ${book.author} ${book.isbn} ${book.publisher}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        }).map((book, originalIndex) => {
            const realIndex = this.books.findIndex(b => b.id === book.id);
            return { book, index: realIndex };
        });

        if (matches.length > 0) {
            resultsList.innerHTML = matches.map(({book, index}) => 
                `<li><a href="#" onclick="bookEditor.showBook(${index}); document.getElementById('searchResults').style.display='none'">
                    <strong>${book.title}</strong> von ${book.author} (${book.year || 'n/a'})
                </a></li>`
            ).join('');
            results.style.display = 'block';
        } else {
            resultsList.innerHTML = '<li>Keine Ergebnisse gefunden</li>';
            results.style.display = 'block';
        }
    }

    updateImagePreview(url) {
        const preview = document.getElementById('imagePreview');
        if (url) {
            preview.innerHTML = `<img src="${url}" alt="Buchcover Vorschau" class="book-image-preview">`;
        } else {
            preview.innerHTML = '';
        }
    }

    updateCounter() {
        const counter = document.getElementById('bookCounter');
        if (this.isNewBook) {
            counter.textContent = `Neues Buch (${this.books.length + 1})`;
        } else {
            counter.textContent = `Buch ${this.currentIndex + 1} von ${this.books.length}`;
        }
    }

    exportYAML() {
        const data = {
            books: this.books,
            generation_date: new Date().toLocaleDateString('de-DE')
        };
        
        const yamlString = jsyaml.dump(data, {
            indent: 2,
            lineWidth: -1,
            noRefs: true,
            sortKeys: false
        });
        
        document.getElementById('yamlOutput').textContent = yamlString;
        document.getElementById('exportArea').style.display = 'block';
    }

    downloadYAML() {
        const data = {
            books: this.books,
            generation_date: new Date().toLocaleDateString('de-DE')
        };
        
        const yamlString = jsyaml.dump(data, {
            indent: 2,
            lineWidth: -1,
            noRefs: true,
            sortKeys: false
        });
        
        const blob = new Blob([yamlString], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Meine_Buchliste_${new Date().toISOString().split('T')[0]}.yaml`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('YAML-Datei heruntergeladen', 'is-success');
    }

    async copyYAML() {
        const yamlText = document.getElementById('yamlOutput').textContent;
        try {
            await navigator.clipboard.writeText(yamlText);
            this.showNotification('YAML in Zwischenablage kopiert', 'is-success');
        } catch (err) {
            console.error('Fehler beim Kopieren:', err);
            this.showNotification('Fehler beim Kopieren', 'is-danger');
        }
    }

    handleKeyboard(e) {
        // Don't handle shortcuts when typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        switch(e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                this.previousBook();
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.nextBook();
                break;
            case 'Home':
                e.preventDefault();
                this.firstBook();
                break;
            case 'End':
                e.preventDefault();
                this.lastBook();
                break;
            case 'n':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.newBook();
                }
                break;
            case 's':
                if (e.ctrlKey) {
                    e.preventDefault();
                    document.getElementById('bookForm').dispatchEvent(new Event('submit'));
                }
                break;
        }
    }

    showNotification(message, type = 'is-info') {
        const indicator = document.getElementById('saveIndicator');
        indicator.innerHTML = `
            <div class="notification ${type}">
                <button class="delete" onclick="this.parentElement.remove()"></button>
                ${message}
            </div>
        `;
        
        setTimeout(() => {
            const notification = indicator.querySelector('.notification');
            if (notification) notification.remove();
        }, 3000);
    }

    async searchExternalBooks() {
        const query = document.getElementById('externalSearchInput').value.trim();
        const source = document.getElementById('searchSourceSelect').value;
        
        if (!query) {
            this.showNotification('Bitte geben Sie einen Suchbegriff ein', 'is-warning');
            return;
        }

        const loadingDiv = document.getElementById('externalSearchLoading');
        const resultsDiv = document.getElementById('externalSearchResults');
        const resultsList = document.getElementById('externalResultsList');

        loadingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        resultsList.innerHTML = '';

        try {
            let searchSource = source;
            
            // Auto-detection logic
            if (source === 'auto') {
                searchSource = this.detectSearchSource(query);
            }

            let results = [];
            
            switch (searchSource) {
                case 'googlebooks':
                    results = await this.searchGoogleBooks(query);
                    break;
                case 'openlibrary':
                    results = await this.searchOpenLibrary(query);
                    break;
                case 'amazon':
                    results = await this.searchAmazonASIN(query);
                    break;
                case 'audible':
                    results = await this.searchAudible(query);
                    break;
                default:
                    results = await this.searchGoogleBooks(query);
            }
            
            loadingDiv.style.display = 'none';

            if (results && results.length > 0) {
                this.displayExternalSearchResults(results);
                resultsDiv.style.display = 'block';
            } else {
                this.showNotification('Keine Bücher gefunden', 'is-warning');
            }

        } catch (error) {
            console.error('Fehler bei der externen Suche:', error);
            loadingDiv.style.display = 'none';
            this.showNotification('Fehler bei der Buchsuche: ' + error.message, 'is-danger');
        }
    }

    detectSearchSource(query) {
        // Audible URL detection
        if (query.includes('audible.de') || query.includes('audible.com')) {
            return 'audible';
        }
        
        // ASIN detection (10 characters, starts with B or is all digits)
        if (query.length === 10 && (query.startsWith('B') || /^\d{10}$/.test(query))) {
            return 'amazon';
        }
        
        // ISBN detection (13 digits, sometimes with dashes)
        const cleanQuery = query.replace(/[-\s]/g, '');
        if (/^\d{13}$/.test(cleanQuery) || /^\d{10}$/.test(cleanQuery)) {
            return 'googlebooks';
        }
        
        // Audiobook-related keywords -> Audible
        const audioKeywords = ['audiobook', 'hörbuch', 'narrator', 'sprecher', 'audible'];
        if (audioKeywords.some(keyword => query.toLowerCase().includes(keyword))) {
            return 'audible';
        }
        
        // Default to Google Books for text searches
        return 'googlebooks';
    }

    async searchGoogleBooks(query) {
        const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(query)}&maxResults=10&langRestrict=de`);
        
        if (!response.ok) {
            throw new Error('Fehler bei der Google Books API-Anfrage');
        }

        const data = await response.json();
        return data.items || [];
    }

    async searchOpenLibrary(query) {
        // Open Library API for additional book data
        const response = await fetch(`https://openlibrary.org/search.json?q=${encodeURIComponent(query)}&limit=10`);
        
        if (!response.ok) {
            throw new Error('Fehler bei der Open Library API-Anfrage');
        }

        const data = await response.json();
        
        // Convert Open Library format to Google Books-like format
        return data.docs.map(doc => ({
            volumeInfo: {
                title: doc.title,
                authors: doc.author_name,
                publishedDate: doc.first_publish_year ? doc.first_publish_year.toString() : '',
                pageCount: doc.number_of_pages_median,
                publisher: doc.publisher ? doc.publisher[0] : '',
                description: doc.first_sentence ? doc.first_sentence.join(' ') : '',
                imageLinks: {
                    thumbnail: doc.cover_i ? `https://covers.openlibrary.org/b/id/${doc.cover_i}-M.jpg` : ''
                },
                industryIdentifiers: this.buildOpenLibraryIdentifiers(doc.isbn),
                categories: doc.subject ? doc.subject.slice(0, 3) : [],
                language: doc.language ? doc.language[0] : 'de'
            }
        }));
    }

    async searchAmazonASIN(asin) {
        // Since direct Amazon API requires authentication, we'll use alternative approaches
        // Method 1: Try to find the book via Open Library using ASIN
        try {
            const response = await fetch(`https://openlibrary.org/search.json?q=${asin}&limit=5`);
            
            if (response.ok) {
                const data = await response.json();
                if (data.docs && data.docs.length > 0) {
                    return data.docs.map(doc => ({
                        volumeInfo: {
                            title: doc.title,
                            authors: doc.author_name,
                            publishedDate: doc.first_publish_year ? doc.first_publish_year.toString() : '',
                            pageCount: doc.number_of_pages_median,
                            publisher: doc.publisher ? doc.publisher[0] : '',
                            description: doc.first_sentence ? doc.first_sentence.join(' ') : '',
                            imageLinks: {
                                thumbnail: doc.cover_i ? `https://covers.openlibrary.org/b/id/${doc.cover_i}-M.jpg` : ''
                            },
                            industryIdentifiers: [
                                { type: 'ASIN', identifier: asin },
                                ...this.buildOpenLibraryIdentifiers(doc.isbn)
                            ],
                            categories: doc.subject ? doc.subject.slice(0, 3) : [],
                            language: doc.language ? doc.language[0] : 'de'
                        }
                    }));
                }
            }
        } catch (error) {
            console.log('Open Library ASIN search failed, trying alternative method');
        }

        // Method 2: Create a manual entry template for ASIN
        return [{
            volumeInfo: {
                title: `Buch mit ASIN: ${asin}`,
                authors: ['Unbekannter Autor'],
                publishedDate: '',
                pageCount: null,
                publisher: 'Amazon',
                description: `Buch gefunden über Amazon ASIN: ${asin}. Bitte Daten manuell vervollständigen.`,
                imageLinks: {
                    thumbnail: 'https://via.placeholder.com/128x200.png?text=ASIN+Book'
                },
                industryIdentifiers: [
                    { type: 'ASIN', identifier: asin }
                ],
                categories: [],
                language: 'de',
                asin: asin // Custom field for tracking
            }
        }];
    }

    buildOpenLibraryIdentifiers(isbns) {
        if (!isbns) return [];
        
        return isbns.map(isbn => {
            const cleanISBN = isbn.replace(/[-\s]/g, '');
            return {
                type: cleanISBN.length === 13 ? 'ISBN_13' : 'ISBN_10',
                identifier: cleanISBN
            };
        });
    }

    async searchAudible(query) {
        try {
            // Check if local Audible API server is running
            const response = await fetch(`http://localhost:5001/api/audible/search?q=${encodeURIComponent(query)}&limit=10`);
            
            if (!response.ok) {
                throw new Error('Audible API Server nicht erreichbar. Bitte starten Sie den Server mit: python data/audible_api_server.py');
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Fehler bei der Audible-Suche');
            }

            // Convert Audible format to Google Books-like format and fetch descriptions
            const enrichedResults = await Promise.all(data.results.map(async (book) => {
                let description = book.description || '';
                
                // Wenn keine Beschreibung vorhanden, versuche sie von der Detail-Seite zu holen
                if (!description && book.audible_url) {
                    try {
                        const detailResponse = await fetch(`http://localhost:5001/api/audible/details?url=${encodeURIComponent(book.audible_url)}`);
                        if (detailResponse.ok) {
                            const detailData = await detailResponse.json();
                            if (detailData.success && detailData.details.description) {
                                description = detailData.details.description;
                            }
                        }
                    } catch (error) {
                        console.log('Detail-Fetch fehlgeschlagen für:', book.title);
                    }
                }

                const enrichedBook = {
                    volumeInfo: {
                        title: book.title || 'Unbekannter Titel',
                        authors: book.authors || ['Unbekannter Autor'],
                        publishedDate: this.parseAudibleDate(book.release_date || book.year_published),
                        pageCount: null, // Not applicable for audiobooks
                        publisher: book.publisher || 'Audible',
                        description: description || 'Keine Beschreibung verfügbar',
                        imageLinks: {
                            thumbnail: book.cover_url || book.image_url || ''
                        },
                        industryIdentifiers: [
                            { type: 'AUDIBLE_URL', identifier: book.audible_url }
                        ],
                        categories: ['Audiobook'],
                        language: 'de',
                        // Audible-specific fields - alle neuen Felder hinzufügen
                        narrators: book.narrators || [],
                        runtime: book.runtime || book.duration || '',
                        rating: book.rating || '',
                        audible_url: book.audible_url || '',
                        is_audiobook: true,
                        booktype: book.booktype || 'Audiobook',
                        year_published: book.year_published || this.parseAudibleDate(book.release_date),
                        duration: book.duration || book.runtime || '',
                        image_url: book.image_url || book.cover_url || ''
                    }
                };
                
                return enrichedBook;
            }));

            return enrichedResults;

        } catch (error) {
            console.error('Audible search error:', error);
            
            // Fallback: Show error message and suggest manual entry
            throw new Error(`Audible-Suche fehlgeschlagen: ${error.message}\n\nUm die Audible-Suche zu nutzen, starten Sie bitte den lokalen API Server:\n1. Öffnen Sie ein Terminal\n2. Navigieren Sie zum Projektordner\n3. Führen Sie aus: python data/audible_api_server.py`);
        }
    }

    parseAudibleDate(dateString) {
        if (!dateString) return '';
        
        // Try to extract year from various German date formats
        const yearMatch = dateString.match(/(\d{4})/);
        return yearMatch ? yearMatch[1] : '';
    }

    displayExternalSearchResults(items) {
        const resultsList = document.getElementById('externalResultsList');
        
        resultsList.innerHTML = items.map((item, index) => {
            const volumeInfo = item.volumeInfo || {};
            const imageLinks = volumeInfo.imageLinks || {};
            const authors = volumeInfo.authors ? volumeInfo.authors.join(', ') : 'Unbekannter Autor';
            const publishedDate = volumeInfo.publishedDate || '';
            const year = publishedDate ? new Date(publishedDate).getFullYear() : '';
            const description = volumeInfo.description ? 
                (volumeInfo.description.substring(0, 200) + (volumeInfo.description.length > 200 ? '...' : '')) : 
                'Keine Beschreibung verfügbar';
            const isbn = this.extractISBN(volumeInfo.industryIdentifiers);
            const thumbnail = imageLinks.thumbnail || imageLinks.smallThumbnail || '';

            // Audible-specific fields
            const isAudiobook = volumeInfo.is_audiobook || false;
            const narrators = volumeInfo.narrators ? volumeInfo.narrators.join(', ') : '';
            const runtime = volumeInfo.runtime || '';
            const rating = volumeInfo.rating || '';

            return `
                <div class="column is-half">
                    <div class="external-book-card">
                        <div class="media">
                            <div class="media-left">
                                ${thumbnail ? `<img src="${thumbnail}" alt="Buchcover" class="external-book-image">` : '<div class="external-book-image" style="background: #f0f0f0; display: flex; align-items: center; justify-content: center;">📚</div>'}
                            </div>
                            <div class="media-content">
                                <h5 class="title is-6">${volumeInfo.title || 'Unbekannter Titel'}</h5>
                                <p class="subtitle is-7">von ${authors}</p>
                                ${isAudiobook && narrators ? `<p class="is-size-7"><strong>Sprecher:</strong> ${narrators}</p>` : ''}
                                ${isAudiobook && runtime ? `<p class="is-size-7"><strong>Laufzeit:</strong> ${runtime}</p>` : ''}
                                ${rating ? `<p class="is-size-7"><strong>Bewertung:</strong> ${rating} ⭐</p>` : ''}
                                <p class="is-size-7"><strong>Jahr:</strong> ${year}</p>
                                ${isbn ? `<p class="is-size-7"><strong>ISBN:</strong> ${isbn}</p>` : ''}
                                ${isAudiobook ? '<span class="tag is-info is-small">📢 Audiobook</span>' : ''}
                                <details class="is-size-7" style="margin-top: 8px;">
                                    <summary style="cursor: pointer; font-weight: bold;">Beschreibung</summary>
                                    <p style="margin-top: 4px;">${description}</p>
                                </details>
                                <div class="buttons is-right" style="margin-top: 10px;">
                                    <button class="button is-small is-primary" onclick="bookEditor.importExternalBook(${index})">
                                        Importieren
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        // Store results for import
        this.externalSearchResults = items;
    }

    extractISBN(identifiers) {
        if (!identifiers) return '';
        
        const isbn13 = identifiers.find(id => id.type === 'ISBN_13');
        const isbn10 = identifiers.find(id => id.type === 'ISBN_10');
        const asin = identifiers.find(id => id.type === 'ASIN');
        
        return isbn13?.identifier || isbn10?.identifier || asin?.identifier || '';
    }

    importExternalBook(index) {
        if (!this.externalSearchResults || !this.externalSearchResults[index]) {
            this.showNotification('Buch nicht gefunden', 'is-danger');
            return;
        }

        const selectedBook = this.externalSearchResults[index];
        const volumeInfo = selectedBook.volumeInfo;
        
        // Create new book object with external data
        const newBook = {
            title: volumeInfo.title || '',
            author: volumeInfo.authors ? volumeInfo.authors.join(', ') : '',
            year: volumeInfo.year_published || (volumeInfo.publishedDate ? new Date(volumeInfo.publishedDate).getFullYear() : ''),
            publisher: volumeInfo.publisher || '',
            pages: volumeInfo.pageCount || '',
            isbn: this.extractISBN(volumeInfo.industryIdentifiers),
            Description: volumeInfo.description || '', // Großgeschrieben für HTML-Formular
            image_url: volumeInfo.image_url || (volumeInfo.imageLinks?.thumbnail || volumeInfo.imageLinks?.smallThumbnail || '').replace('&zoom=1', '&zoom=0'),
            genre: this.guessGenre(volumeInfo.categories),
            language: volumeInfo.language || 'de',
            book_color: '#3498db', // Default color
            bestseller: false,
            audiobook: volumeInfo.is_audiobook || false,
            read: false,
            narrator: volumeInfo.narrators ? volumeInfo.narrators.join(', ') : '',
            asin: volumeInfo.asin || '',
            // Zusätzliche Audible-Felder
            'Year Published': volumeInfo.year_published || (volumeInfo.publishedDate ? new Date(volumeInfo.publishedDate).getFullYear() : ''),
            duration: volumeInfo.duration || volumeInfo.runtime || '',
            bookType: volumeInfo.booktype || (volumeInfo.is_audiobook ? 'Audiobook' : ''),
            'My Rating': volumeInfo.rating ? parseFloat(volumeInfo.rating) : null
        };

        // Fill form with imported data
        this.fillFormWithBookData(newBook);
        
        // Close external search
        document.getElementById('externalSearchResults').style.display = 'none';
        document.getElementById('externalSearchInput').value = '';
        
        this.showNotification('Buch importiert! Bitte überprüfen Sie die Daten und speichern Sie das Buch.', 'is-success');
    }

    guessGenre(categories) {
        if (!categories) return '';
        
        const categoryStr = categories.join(' ').toLowerCase();
        
        // Fiction keywords
        const fictionKeywords = ['fiction', 'roman', 'fantasy', 'science fiction', 'mystery', 'thriller', 'romance', 'adventure'];
        // Nonfiction keywords  
        const nonfictionKeywords = ['biography', 'history', 'science', 'technology', 'business', 'self-help', 'politics', 'philosophy', 'psychology'];
        
        if (fictionKeywords.some(keyword => categoryStr.includes(keyword))) {
            return 'Fiction';
        } else if (nonfictionKeywords.some(keyword => categoryStr.includes(keyword))) {
            return 'Nonfiction';
        }
        
        return 'Fiction'; // Default
    }

    fillFormWithBookData(book) {
        const form = document.getElementById('bookForm');
        form.reset();
        
        Object.keys(book).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = book[key] === true;
                } else {
                    input.value = book[key] || '';
                }
            }
        });
        
        this.updateImagePreview(book.image_url);
        this.updateCounter();
    }
}

// Initialize the editor when the page loads
let bookEditor;
document.addEventListener('DOMContentLoaded', () => {
    bookEditor = new BookEditor();
});
