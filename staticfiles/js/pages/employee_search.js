/**
 * Employee Search JavaScript
 * Handles global search functionality for employees
 */

// Search Management Functions
function performSearch() {
    const query = document.getElementById('globalSearchInput').value.trim();
    
    if (query.length < 3) {
        clearSearchResults();
        return;
    }
    
    // Show loading state
    showSearchLoading();
    
    // Perform search via API
    fetch(`/api/search/?q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        hideSearchLoading();
        displaySearchResults(data.results, query);
    })
    .catch(error => {
        hideSearchLoading();
        console.error('Error:', error);
        showSearchError();
    });
}

function displaySearchResults(results, query) {
    const resultsContainer = document.getElementById('searchResults');
    const resultsCount = document.getElementById('resultsCount');
    
    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No results found</h5>
                <p class="text-muted">Try adjusting your search terms or check the spelling.</p>
            </div>
        `;
        resultsCount.textContent = '0 results';
        return;
    }
    
    let html = '';
    results.forEach(result => {
        html += `
            <div class="search-result-item mb-3">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="card-title">
                                    <i class="${getResultIcon(result.type)} me-2"></i>
                                    ${highlightSearchTerm(result.title, query)}
                                </h6>
                                <p class="card-text text-muted">${result.description}</p>
                                <small class="text-muted">
                                    <i class="fas fa-tag me-1"></i>${result.type}
                                    ${result.date ? `<i class="fas fa-calendar ms-3 me-1"></i>${result.date}` : ''}
                                </small>
                            </div>
                            <div class="search-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="viewResult('${result.id}', '${result.type}')">
                                    <i class="fas fa-eye"></i> View
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
    resultsCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''} found`;
}

function highlightSearchTerm(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function getResultIcon(type) {
    const iconMap = {
        'task': 'fas fa-tasks',
        'project': 'fas fa-project-diagram',
        'document': 'fas fa-file',
        'employee': 'fas fa-user',
        'announcement': 'fas fa-bullhorn',
        'meeting': 'fas fa-calendar',
        'goal': 'fas fa-bullseye',
        'timesheet': 'fas fa-clock'
    };
    return iconMap[type] || 'fas fa-file';
}

function clearSearchResults() {
    const resultsContainer = document.getElementById('searchResults');
    const resultsCount = document.getElementById('resultsCount');
    
    resultsContainer.innerHTML = `
        <div class="text-center py-5">
            <i class="fas fa-search fa-3x text-muted mb-3"></i>
            <h5 class="text-muted">Start searching</h5>
            <p class="text-muted">Enter at least 3 characters to search across tasks, projects, documents, and more.</p>
        </div>
    `;
    resultsCount.textContent = '';
}

function showSearchLoading() {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Searching...</span>
            </div>
            <h5 class="text-muted">Searching...</h5>
        </div>
    `;
}

function hideSearchLoading() {
    // Loading state will be replaced by results
}

function showSearchError() {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = `
        <div class="text-center py-5">
            <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
            <h5 class="text-muted">Search Error</h5>
            <p class="text-muted">There was an error performing the search. Please try again.</p>
        </div>
    `;
}

function viewResult(resultId, resultType) {
    console.log('Viewing result:', resultId, resultType);
    
    // Navigate based on result type
    const typeMap = {
        'task': `/employee/tasks/?id=${resultId}`,
        'project': `/employee/projects/?id=${resultId}`,
        'document': `/employee/documents/?id=${resultId}`,
        'employee': `/employee/team/?id=${resultId}`,
        'announcement': `/employee/notifications/?id=${resultId}`,
        'meeting': `/employee/calendar/?id=${resultId}`,
        'goal': `/employee/goals/?id=${resultId}`,
        'timesheet': `/employee/timesheet/?id=${resultId}`
    };
    
    const url = typeMap[resultType];
    if (url) {
        window.location.href = url;
    } else {
        showErrorToast('Cannot navigate to this result type.');
    }
}

function filterSearchResults(filter) {
    const resultItems = document.querySelectorAll('.search-result-item');
    
    resultItems.forEach(item => {
        const resultType = item.querySelector('.fas').className;
        const shouldShow = filter === 'all' || resultType.includes(filter);
        
        item.style.display = shouldShow ? 'block' : 'none';
    });
    
    // Update active filter button
    const filterButtons = document.querySelectorAll('.search-filter-btn');
    filterButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === filter) {
            btn.classList.add('active');
        }
    });
}

function clearSearch() {
    document.getElementById('globalSearchInput').value = '';
    clearSearchResults();
}

function searchShortcuts() {
    const shortcuts = [
        { key: 'Ctrl + K', description: 'Focus search box' },
        { key: 'Enter', description: 'Perform search' },
        { key: 'Esc', description: 'Clear search' },
        { key: 'Tab', description: 'Navigate results' }
    ];
    
    let html = '<div class="search-shortcuts">';
    shortcuts.forEach(shortcut => {
        html += `
            <div class="d-flex justify-content-between mb-2">
                <kbd>${shortcut.key}</kbd>
                <span class="text-muted">${shortcut.description}</span>
            </div>
        `;
    });
    html += '</div>';
    
    showInfoToast('Search Shortcuts:\n\n' + shortcuts.map(s => `${s.key}: ${s.description}`).join('\n'));
}

// Initialize search functionality
function initSearch() {
    console.log('Search initialized');
    
    // Initialize search functionality
    const searchInput = document.getElementById('globalSearchInput');
    
    // Search on Enter key
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Auto-search as user types (with debounce)
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3) {
                    performSearch();
                } else if (this.value.length === 0) {
                    clearSearchResults();
                }
            }, 500);
        });
        
        // Clear search on Escape
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                clearSearch();
            }
        });
    }
    
    // Set up filter buttons
    const filterButtons = document.querySelectorAll('.search-filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.filter;
            filterSearchResults(filter);
        });
    });
    
    // Initialize with empty state
    clearSearchResults();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
});

// Export functions for global access
window.performSearch = performSearch;
window.clearSearch = clearSearch;
window.viewResult = viewResult;
window.filterSearchResults = filterSearchResults;
window.searchShortcuts = searchShortcuts;
