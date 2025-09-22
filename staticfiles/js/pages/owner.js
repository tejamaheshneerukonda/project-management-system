// Owner Dashboard Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Company key copied to clipboard!', 'success');
        }, function(err) {
            console.error('Could not copy text: ', err);
            showNotification('Failed to copy to clipboard', 'error');
        });
    };

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }, 3000);
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Table row hover effects
    const tableRows = document.querySelectorAll('#companiesTable tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(37, 99, 235, 0.05)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Search functionality for companies table
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Search companies...';
    
    const tableContainer = document.querySelector('.table-responsive');
    if (tableContainer) {
        tableContainer.parentNode.insertBefore(searchInput, tableContainer);
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#companiesTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Stats counter animation
    function animateCounters() {
        const counters = document.querySelectorAll('.h5.mb-0');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
            if (target > 0) {
                const duration = 2000;
                const increment = target / (duration / 16);
                let current = 0;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    counter.textContent = Math.floor(current);
                }, 16);
            }
        });
    }

    // Trigger counter animation when page loads
    setTimeout(animateCounters, 500);

    // Modal enhancement
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const input = this.querySelector('input[readonly]');
            if (input) {
                input.select();
            }
        });
    });

    // Export functionality (placeholder)
    window.exportCompanies = function(format) {
        console.log('Exporting companies in', format, 'format');
        showNotification('Export functionality coming soon!', 'info');
    };

    // Bulk selection functionality
    window.toggleSelectAll = function() {
        const selectAll = document.getElementById('selectAll');
        const checkboxes = document.querySelectorAll('.company-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll.checked;
        });
        
        updateBulkActions();
    };

    // Update bulk actions visibility
    function updateBulkActions() {
        const checkboxes = document.querySelectorAll('.company-checkbox:checked');
        const bulkActions = document.getElementById('bulkActions');
        const selectedCount = document.getElementById('selectedCount');
        
        if (checkboxes.length > 0) {
            bulkActions.style.display = 'block';
            selectedCount.textContent = `${checkboxes.length} companies selected`;
        } else {
            bulkActions.style.display = 'none';
        }
    }

    // Individual checkbox change
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('company-checkbox')) {
            updateBulkActions();
        }
    });

    // Bulk operations
    window.bulkActivate = function() {
        const selectedIds = getSelectedCompanyIds();
        if (selectedIds.length === 0) {
            showNotification('Please select companies first', 'warning');
            return;
        }
        
        if (confirm(`Activate ${selectedIds.length} selected companies?`)) {
            performBulkAction('activate', selectedIds);
        }
    };

    window.bulkDeactivate = function() {
        const selectedIds = getSelectedCompanyIds();
        if (selectedIds.length === 0) {
            showNotification('Please select companies first', 'warning');
            return;
        }
        
        if (confirm(`Deactivate ${selectedIds.length} selected companies?`)) {
            performBulkAction('deactivate', selectedIds);
        }
    };

    window.bulkDelete = function() {
        const selectedIds = getSelectedCompanyIds();
        if (selectedIds.length === 0) {
            showNotification('Please select companies first', 'warning');
            return;
        }
        
        if (confirm(`Delete ${selectedIds.length} selected companies? This action cannot be undone!`)) {
            performBulkAction('delete', selectedIds);
        }
    };

    // Get selected company IDs
    function getSelectedCompanyIds() {
        const checkboxes = document.querySelectorAll('.company-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    // Perform bulk action
    function performBulkAction(action, companyIds) {
        showNotification(`Performing bulk ${action} operation...`, 'info');
        
        // This would typically make AJAX calls to the server
        // For now, we'll simulate the operation
        setTimeout(() => {
            showNotification(`Bulk ${action} operation completed!`, 'success');
            location.reload(); // Refresh the page
        }, 2000);
    }

    // Company deletion confirmation
    window.confirmDeleteCompany = function(companyId, companyName) {
        if (confirm(`Are you sure you want to delete "${companyName}"? This action cannot be undone and will delete all associated data.`)) {
            // Redirect to delete URL
            window.location.href = `/owner/company/${companyId}/delete/`;
        }
    };

    // Dashboard refresh
    window.refreshDashboard = function() {
        showNotification('Refreshing dashboard data...', 'info');
        location.reload();
    };

    window.refreshCompanies = function() {
        showNotification('Refreshing companies data...', 'info');
        location.reload();
    };

    // System settings
    window.showSystemSettings = function() {
        showNotification('System settings functionality coming soon!', 'info');
    };

    console.log('Owner dashboard JavaScript initialized successfully!');
});
