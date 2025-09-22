/**
 * Employee Documents JavaScript
 * Handles document management functionality for employees
 */

// Document Management Functions
function filterDocuments() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    
    const rows = document.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const category = row.querySelector('td:nth-child(3)').textContent;
        const type = row.querySelector('td:nth-child(4)').textContent;
        
        let show = true;
        
        // Search filter
        if (searchTerm && !name.includes(searchTerm)) {
            show = false;
        }
        
        // Category filter
        if (categoryFilter && category !== categoryFilter) {
            show = false;
        }
        
        // Type filter
        if (typeFilter && type !== typeFilter) {
            show = false;
        }
        
        row.style.display = show ? 'table-row' : 'none';
    });
}

function filterByCategory(category) {
    document.getElementById('categoryFilter').value = category;
    filterDocuments();
}

function toggleView(view) {
    const table = document.getElementById('documentsTable');
    if (view === 'grid') {
        // Implement grid view
        console.log('Switching to grid view');
    } else {
        // Implement list view
        console.log('Switching to list view');
    }
}

function uploadDocument() {
    // Implement document upload modal
    console.log('Uploading document');
    // This would open a file upload modal
}

function createFolder() {
    // Implement folder creation modal
    console.log('Creating folder');
    // This would open a folder creation modal
}

function shareDocument(documentName = null) {
    // Implement document sharing modal
    console.log('Sharing document:', documentName);
    // This would open a sharing modal
}

function viewDocument(documentName) {
    // Implement document viewer
    console.log('Viewing document:', documentName);
    // This would open a document viewer modal
}

function downloadDocument(documentName) {
    // Implement document download
    console.log('Downloading document:', documentName);
    // This would trigger a download
}

function editDocument(documentName) {
    // Implement document editing
    console.log('Editing document:', documentName);
    // This would open an editor
}

function viewRecent() {
    // Implement recent activity view
    console.log('Viewing recent activity');
    // This would show recent document activity
}

// Initialize document management functionality
function initDocumentManagement() {
    console.log('Document management initialized');
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterDocuments();
        });
    }
    
    // Filter functionality
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterDocuments);
    }
    
    const typeFilter = document.getElementById('typeFilter');
    if (typeFilter) {
        typeFilter.addEventListener('change', filterDocuments);
    }
    
    // Select all functionality
    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initDocumentManagement();
});

// Export functions for global access
window.filterDocuments = filterDocuments;
window.filterByCategory = filterByCategory;
window.toggleView = toggleView;
window.uploadDocument = uploadDocument;
window.createFolder = createFolder;
window.shareDocument = shareDocument;
window.viewDocument = viewDocument;
window.downloadDocument = downloadDocument;
window.editDocument = editDocument;
window.viewRecent = viewRecent;
