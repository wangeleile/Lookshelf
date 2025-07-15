class BookTableEditor {
    constructor() {
        this.books = [];
        this.filteredBooks = [];
        this.currentPage = 1;
        this.rowsPerPage = 50;
        this.columns = [
            { key: 'id', title: 'ID', type: 'number', width: '80px', visible: true, sticky: true },
            { key: 'title', title: 'Titel', type: 'text', width: '200px', visible: true, sticky: false },
            { key: 'author', title: 'Autor', type: 'text', width: '150px', visible: true, sticky: false },
            { key: 'year', title: 'Jahr', type: 'number', width: '80px', visible: true, sticky: false },
            { key: 'rating', title: 'Bewertung', type: 'number', width: '100px', visible: true, sticky: false },
            { key: 'My Rating', title: 'Meine Bewertung', type: 'number', width: '120px', visible: true, sticky: false },
            { key: 'genre', title: 'Genre', type: 'select', options: ['Fiction', 'Nonfiction'], width: '100px', visible: true, sticky: false },
            { key: 'pages', title: 'Seiten', type: 'number', width: '80px', visible: true, sticky: false },
            { key: 'bookType', title: 'Typ', type: 'select', options: ['Book', 'Audiobook', 'eBook'], width: '100px', visible: true, sticky: false },
            { key: 'publisher', title: 'Verlag', type: 'text', width: '150px', visible: true, sticky: false },
            { key: 'isbn', title: 'ISBN', type: 'text', width: '120px', visible: true, sticky: false },
            { key: 'Serie', title: 'Serie', type: 'text', width: '120px', visible: true, sticky: false },
            { key: 'Serien Nr.', title: 'Serie Nr.', type: 'number', width: '80px', visible: true, sticky: false },
            { key: 'bookshelves', title: 'Regal', type: 'text', width: '100px', visible: true, sticky: false },
            { key: 'bestseller', title: 'Bestseller', type: 'checkbox', width: '100px', visible: true, sticky: false },
            { key: 'language', title: 'Sprache', type: 'text', width: '100px', visible: false, sticky: false },
            { key: 'duration', title: 'Dauer', type: 'text', width: '100px', visible: false, sticky: false },
            { key: 'narrator', title: 'Sprecher', type: 'text', width: '120px', visible: false, sticky: false },
            { key: 'rating_count', title: 'Bewertungen', type: 'text', width: '100px', visible: false, sticky: false },
            { key: 'image_url', title: 'Bild', type: 'image', width: '80px', visible: true, sticky: false },
            { key: 'Description', title: 'Beschreibung', type: 'textarea', width: '200px', visible: false, sticky: false },
            { key: 'My_Review', title: 'Meine Rezension', type: 'textarea', width: '200px', visible: false, sticky: false },
            { key: 'actions', title: 'Aktionen', type: 'actions', width: '120px', visible: true, sticky: false }
        ];
        this.editingCell = null;
        this.hasUnsavedChanges = false;
        this.init();
    }

    async init() {
        await this.loadBooks();
        this.setupEventListeners();
        this.renderColumnDropdown();
        this.applyFilters();
        this.updateStats();
    }

    async loadBooks() {
        try {
            // Zuerst versuchen, vom API-Server zu laden
            let response;
            let data;
            
            try {
                response = await fetch('http://localhost:5002/api/books');
                if (response.ok) {
                    data = await response.json();
                    this.books = data.books || [];
                    console.log(`${this.books.length} Bücher vom API-Server geladen`);
                    this.showNotification(`📡 ${this.books.length} Bücher vom Server geladen`, 'is-info');
                    return;
                }
            } catch (serverError) {
                console.log('API-Server nicht erreichbar, lade von lokaler Datei');
            }
            
            // Fallback: Von lokaler YAML-Datei laden
            response = await fetch('data/Meine_Buchliste.yaml');
            const yamlText = await response.text();
            data = jsyaml.load(yamlText);
            this.books = data.books || [];
            console.log(`${this.books.length} Bücher von lokaler Datei geladen`);
            this.showNotification(`📁 ${this.books.length} Bücher von lokaler Datei geladen`, 'is-info');
            
        } catch (error) {
            console.error('Fehler beim Laden der Buchdaten:', error);
            this.showNotification('❌ Fehler beim Laden der Buchdaten', 'is-danger');
            this.books = [];
        }
    }

    setupEventListeners() {
        // Search and filters
        document.getElementById('searchInput').addEventListener('input', (e) => this.handleSearch(e.target.value));
        document.getElementById('genreFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('bookTypeFilter').addEventListener('change', () => this.applyFilters());
        
        // Pagination
        document.getElementById('prevPage').addEventListener('click', () => this.changePage(this.currentPage - 1));
        document.getElementById('nextPage').addEventListener('click', () => this.changePage(this.currentPage + 1));
        document.getElementById('rowsPerPage').addEventListener('change', (e) => {
            this.rowsPerPage = e.target.value === 'all' ? this.filteredBooks.length : parseInt(e.target.value);
            this.currentPage = 1;
            this.renderTable();
            this.renderPagination();
        });
        
        // Buttons
        document.getElementById('addBookBtn').addEventListener('click', () => this.addNewBook());
        document.getElementById('saveAllBtn').addEventListener('click', () => this.saveAllBooks());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportYAML());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadYAML());
        document.getElementById('copyBtn').addEventListener('click', () => this.copyYAML());
        document.getElementById('columnsBtn').addEventListener('click', () => this.toggleColumnDropdown());
        
        // Click outside to close column dropdown
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.column-toggle')) {
                document.getElementById('columnDropdown').classList.remove('is-active');
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // Warn before leaving if there are unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'Sie haben ungespeicherte Änderungen. Möchten Sie wirklich die Seite verlassen?';
            }
        });
    }

    handleSearch(query) {
        this.searchQuery = query.toLowerCase();
        this.applyFilters();
    }

    applyFilters() {
        const genreFilter = document.getElementById('genreFilter').value;
        const bookTypeFilter = document.getElementById('bookTypeFilter').value;
        const searchQuery = this.searchQuery || '';

        this.filteredBooks = this.books.filter(book => {
            // Genre filter
            if (genreFilter && book.genre !== genreFilter) return false;
            
            // Book type filter
            if (bookTypeFilter && book.bookType !== bookTypeFilter) return false;
            
            // Search filter
            if (searchQuery) {
                const searchText = `${book.title || ''} ${book.author || ''} ${book.isbn || ''} ${book.publisher || ''}`.toLowerCase();
                if (!searchText.includes(searchQuery)) return false;
            }
            
            return true;
        });

        this.currentPage = 1;
        this.renderTable();
        this.renderPagination();
        this.updateStats();
    }

    renderColumnDropdown() {
        const dropdown = document.getElementById('columnDropdown');
        dropdown.innerHTML = this.columns.map(col => 
            col.key !== 'actions' ? `
                <div class="column-option">
                    <input type="checkbox" ${col.visible ? 'checked' : ''} 
                           onchange="bookTableEditor.toggleColumn('${col.key}', this.checked)">
                    <span>${col.title}</span>
                </div>
            ` : ''
        ).join('');
    }

    toggleColumn(key, visible) {
        const column = this.columns.find(col => col.key === key);
        if (column) {
            column.visible = visible;
            this.renderTable();
        }
    }

    toggleColumnDropdown() {
        document.getElementById('columnDropdown').classList.toggle('is-active');
    }

    renderTable() {
        this.renderHeader();
        this.renderBody();
    }

    renderHeader() {
        const header = document.getElementById('tableHeader');
        const visibleColumns = this.columns.filter(col => col.visible);
        
        header.innerHTML = visibleColumns.map(col => `
            <th class="${col.sticky ? 'sticky-column' : ''}" 
                style="width: ${col.width}; min-width: ${col.width};">
                ${col.title}
                ${col.key !== 'actions' && col.key !== 'image_url' ? 
                    `<button class="button is-small is-white ml-1" onclick="bookTableEditor.sortBy('${col.key}')">
                        <span class="icon is-small"><i>↕️</i></span>
                    </button>` : ''
                }
            </th>
        `).join('');
    }

    renderBody() {
        const tbody = document.getElementById('tableBody');
        const startIndex = (this.currentPage - 1) * this.rowsPerPage;
        const endIndex = this.rowsPerPage === this.filteredBooks.length ? 
                        this.filteredBooks.length : 
                        Math.min(startIndex + this.rowsPerPage, this.filteredBooks.length);
        const visibleBooks = this.filteredBooks.slice(startIndex, endIndex);
        const visibleColumns = this.columns.filter(col => col.visible);

        tbody.innerHTML = visibleBooks.map((book, index) => {
            const globalIndex = startIndex + index;
            return `
                <tr data-book-index="${globalIndex}">
                    ${visibleColumns.map(col => this.renderCell(book, col, globalIndex)).join('')}
                </tr>
            `;
        }).join('');
    }

    renderCell(book, column, bookIndex) {
        const value = book[column.key];
        const cellClass = column.sticky ? 'sticky-column' : '';
        
        switch (column.type) {
            case 'image':
                return `<td class="${cellClass}">
                    ${value ? `<img src="${value}" alt="Cover" class="book-image" onerror="this.style.display='none'">` : ''}
                </td>`;
                
            case 'checkbox':
                return `<td class="${cellClass} checkbox-cell">
                    <input type="checkbox" ${value ? 'checked' : ''} 
                           onchange="bookTableEditor.updateBookField(${bookIndex}, '${column.key}', this.checked)">
                </td>`;
                
            case 'select':
                return `<td class="${cellClass}">
                    <div class="select is-small is-fullwidth">
                        <select onchange="bookTableEditor.updateBookField(${bookIndex}, '${column.key}', this.value)">
                            <option value="">--</option>
                            ${column.options.map(option => 
                                `<option value="${option}" ${value === option ? 'selected' : ''}>${option}</option>`
                            ).join('')}
                        </select>
                    </div>
                </td>`;
                
            case 'actions':
                return `<td class="${cellClass}">
                    <div class="book-actions">
                        <button class="button is-small is-info" onclick="bookTableEditor.editBookDetails(${bookIndex})" title="Details bearbeiten">
                            <span class="icon"><i>✏️</i></span>
                        </button>
                        <button class="button is-small is-danger" onclick="bookTableEditor.deleteBook(${bookIndex})" title="Löschen">
                            <span class="icon"><i>🗑️</i></span>
                        </button>
                        <button class="button is-small is-success" onclick="bookTableEditor.duplicateBook(${bookIndex})" title="Duplizieren">
                            <span class="icon"><i>📋</i></span>
                        </button>
                    </div>
                </td>`;
                
            case 'number':
                return `<td class="${cellClass}">
                    <div class="editable-cell" onclick="bookTableEditor.startEdit(this, ${bookIndex}, '${column.key}', 'number')">
                        ${value || ''}
                    </div>
                </td>`;
                
            case 'textarea':
                const truncated = value ? (value.length > 50 ? value.substring(0, 50) + '...' : value) : '';
                return `<td class="${cellClass}" title="${value || ''}">
                    <div class="editable-cell" onclick="bookTableEditor.startEdit(this, ${bookIndex}, '${column.key}', 'textarea')">
                        ${truncated}
                    </div>
                </td>`;
                
            default: // text
                return `<td class="${cellClass}">
                    <div class="editable-cell" onclick="bookTableEditor.startEdit(this, ${bookIndex}, '${column.key}', 'text')">
                        ${column.key === 'rating' && value ? 
                            `<span class="rating-display">${value} ⭐</span>` :
                            (value || '')
                        }
                    </div>
                </td>`;
        }
    }

    startEdit(cell, bookIndex, field, type) {
        if (this.editingCell) {
            this.finishEdit();
        }

        this.editingCell = { cell, bookIndex, field, type };
        const currentValue = this.filteredBooks[bookIndex][field] || '';
        
        cell.classList.add('editing');
        
        if (type === 'textarea') {
            cell.innerHTML = `<textarea class="edit-input" rows="3">${currentValue}</textarea>`;
        } else {
            cell.innerHTML = `<input type="${type}" class="edit-input" value="${currentValue}">`;
        }
        
        const input = cell.querySelector('.edit-input');
        input.focus();
        
        if (type === 'text') {
            input.select();
        }
        
        input.addEventListener('blur', () => this.finishEdit());
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && type !== 'textarea') {
                this.finishEdit();
            } else if (e.key === 'Escape') {
                this.cancelEdit();
            }
        });
    }

    finishEdit() {
        if (!this.editingCell) return;
        
        const { cell, bookIndex, field, type } = this.editingCell;
        const input = cell.querySelector('.edit-input');
        const newValue = input.value;
        
        this.updateBookField(bookIndex, field, newValue);
        this.editingCell = null;
    }

    cancelEdit() {
        if (!this.editingCell) return;
        
        const { cell, bookIndex, field } = this.editingCell;
        const originalValue = this.filteredBooks[bookIndex][field] || '';
        
        cell.classList.remove('editing');
        cell.innerHTML = originalValue;
        this.editingCell = null;
    }

    updateBookField(bookIndex, field, value) {
        const book = this.filteredBooks[bookIndex];
        const realIndex = this.books.findIndex(b => b.id === book.id);
        
        if (realIndex !== -1) {
            // Convert value based on field type
            let convertedValue = value;
            if (['year', 'pages', 'rating', 'My Rating', 'id', 'Serien Nr.'].includes(field)) {
                convertedValue = value ? parseFloat(value) : null;
            } else if (field === 'bestseller') {
                convertedValue = Boolean(value);
            }
            
            this.books[realIndex][field] = convertedValue;
            this.filteredBooks[bookIndex][field] = convertedValue;
            
            // Update computed fields
            if (field === 'year' && convertedValue) {
                this.books[realIndex].year_asc = convertedValue;
                this.books[realIndex].year_desc = -convertedValue;
            } else if (field === 'rating' && convertedValue) {
                this.books[realIndex].rating_asc = convertedValue;
                this.books[realIndex].rating_desc = -convertedValue;
            }
            
            this.hasUnsavedChanges = true;
            this.showNotification('📝 Feld aktualisiert (nicht gespeichert)', 'is-warning');
            
            // Re-render the specific cell
            setTimeout(() => this.renderTable(), 10);
        }
    }

    addNewBook() {
        const newBook = {
            id: Math.max(...this.books.map(b => b.id || 0)) + 1,
            title: 'Neues Buch',
            author: '',
            year: new Date().getFullYear(),
            genre: 'Fiction',
            rating: 0,
            'My Rating': 0,
            pages: 0,
            bookType: 'Book',
            publisher: '',
            isbn: '',
            Serie: '',
            'Serien Nr.': null,
            bookshelves: '',
            bestseller: false,
            language: 'Deutsch',
            duration: '',
            narrator: '',
            rating_count: '0',
            image_url: '',
            Description: '',
            My_Review: '',
            book_color: '#8B4513',
            'Date Read': null,
            'Date Added': new Date().toISOString().split('T')[0],
            year_asc: new Date().getFullYear(),
            year_desc: -new Date().getFullYear(),
            rating_asc: 0,
            rating_desc: 0
        };
        
        this.books.unshift(newBook);
        this.hasUnsavedChanges = true;
        this.applyFilters();
        this.showNotification('➕ Neues Buch hinzugefügt', 'is-success');
    }

    deleteBook(bookIndex) {
        const book = this.filteredBooks[bookIndex];
        if (confirm(`Sind Sie sicher, dass Sie "${book.title}" löschen möchten?`)) {
            const realIndex = this.books.findIndex(b => b.id === book.id);
            if (realIndex !== -1) {
                this.books.splice(realIndex, 1);
                this.hasUnsavedChanges = true;
                this.applyFilters();
                this.showNotification('🗑️ Buch gelöscht', 'is-success');
            }
        }
    }

    duplicateBook(bookIndex) {
        const book = this.filteredBooks[bookIndex];
        const newBook = { ...book };
        newBook.id = Math.max(...this.books.map(b => b.id || 0)) + 1;
        newBook.title = `${book.title} (Kopie)`;
        
        this.books.push(newBook);
        this.hasUnsavedChanges = true;
        this.applyFilters();
        this.showNotification('📋 Buch dupliziert', 'is-success');
    }

    editBookDetails(bookIndex) {
        const book = this.filteredBooks[bookIndex];
        // Öffne den normalen Book Editor mit diesem Buch
        window.open(`book-editor.html?bookId=${book.id}`, '_blank');
    }

    sortBy(field) {
        this.filteredBooks.sort((a, b) => {
            const aVal = a[field] || '';
            const bVal = b[field] || '';
            
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return aVal - bVal;
            }
            
            return aVal.toString().localeCompare(bVal.toString());
        });
        
        this.renderTable();
    }

    changePage(page) {
        const totalPages = Math.ceil(this.filteredBooks.length / this.rowsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderTable();
            this.renderPagination();
        }
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredBooks.length / this.rowsPerPage);
        const pagination = document.getElementById('paginationList');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const pageInfo = document.getElementById('pageInfo');
        
        // Update buttons
        prevBtn.disabled = this.currentPage <= 1;
        nextBtn.disabled = this.currentPage >= totalPages;
        
        // Update page info
        pageInfo.textContent = `Seite ${this.currentPage} von ${totalPages}`;
        
        // Update pagination list
        pagination.innerHTML = '';
        for (let i = Math.max(1, this.currentPage - 2); i <= Math.min(totalPages, this.currentPage + 2); i++) {
            const li = document.createElement('li');
            li.innerHTML = `
                <button class="pagination-link ${i === this.currentPage ? 'is-current' : ''}" 
                        onclick="bookTableEditor.changePage(${i})">
                    ${i}
                </button>
            `;
            pagination.appendChild(li);
        }
    }

    updateStats() {
        const total = this.books.length;
        const filtered = this.filteredBooks.length;
        const avgRating = this.books.length > 0 ? 
            (this.books.reduce((sum, book) => sum + (book.rating || 0), 0) / this.books.length).toFixed(1) : 0;
        const fictionCount = this.books.filter(book => book.genre === 'Fiction').length;
        const nonfictionCount = this.books.filter(book => book.genre === 'Nonfiction').length;
        
        document.getElementById('totalBooks').textContent = total;
        document.getElementById('filteredBooks').textContent = filtered;
        document.getElementById('avgRating').textContent = avgRating;
        document.getElementById('fictionCount').textContent = fictionCount;
        document.getElementById('nonfictionCount').textContent = nonfictionCount;
    }

    async saveAllBooks() {
        try {
            const data = {
                books: this.books,
                generation_date: new Date().toLocaleDateString('de-DE')
            };

            const response = await fetch('http://localhost:5002/api/books', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                this.hasUnsavedChanges = false;
                this.showNotification(`✅ ${result.message} (${result.book_count} Bücher)`, 'is-success');
                
                if (result.backup_file) {
                    console.log(`Backup erstellt: ${result.backup_file}`);
                }
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Unbekannter Server-Fehler');
            }
        } catch (error) {
            console.error('Fehler beim Speichern an Server:', error);
            this.showNotification(`❌ Speichern fehlgeschlagen: ${error.message}`, 'is-danger');
            
            // Fallback: Zeige Export-Bereich für manuelles Speichern
            this.exportYAML();
            this.showNotification('💡 Bitte YAML manuell herunterladen und speichern', 'is-warning');
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
        
        this.showNotification('📥 YAML-Datei heruntergeladen', 'is-success');
    }

    async copyYAML() {
        const yamlText = document.getElementById('yamlOutput').textContent;
        try {
            await navigator.clipboard.writeText(yamlText);
            this.showNotification('📋 YAML in Zwischenablage kopiert', 'is-success');
        } catch (err) {
            console.error('Fehler beim Kopieren:', err);
            this.showNotification('❌ Fehler beim Kopieren', 'is-danger');
        }
    }

    handleKeyboard(e) {
        // Don't handle shortcuts when editing
        if (this.editingCell) return;
        
        switch(e.key) {
            case 'n':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.addNewBook();
                }
                break;
            case 's':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.saveAllBooks();
                }
                break;
            case 'f':
                if (e.ctrlKey) {
                    e.preventDefault();
                    document.getElementById('searchInput').focus();
                }
                break;
        }
    }

    showNotification(message, type = 'is-info') {
        const indicator = document.getElementById('saveIndicator');
        indicator.innerHTML = `
            <div class="notification ${type} is-light">
                <button class="delete" onclick="this.parentElement.remove()"></button>
                ${message}
            </div>
        `;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (indicator.firstElementChild) {
                indicator.firstElementChild.remove();
            }
        }, 5000);
    }
}

// Initialize the editor when the page loads
let bookTableEditor;
document.addEventListener('DOMContentLoaded', () => {
    bookTableEditor = new BookTableEditor();
});
