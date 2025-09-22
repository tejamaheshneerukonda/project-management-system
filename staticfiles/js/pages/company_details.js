// Company Details Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize company details page
    initializeCompanyDetails();
    
    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Company key copied to clipboard!', 'success');
        }, function(err) {
            console.error('Could not copy text: ', err);
            showNotification('Failed to copy to clipboard', 'error');
        });
    };

    // Company deletion confirmation
    window.confirmDeleteCompany = function(companyId, companyName) {
        if (confirm(`Are you sure you want to delete "${companyName}"? This action cannot be undone and will delete all associated data including employees and their accounts.`)) {
            // Redirect to delete URL
            window.location.href = `/owner/company/${companyId}/delete/`;
        }
    };

    // Initialize company details page
    function initializeCompanyDetails() {
        // Auto-hide alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
        
        // Table row hover effects
        const tableRows = document.querySelectorAll('#employeesTable tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(37, 99, 235, 0.05)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
        
        // Search functionality for employees table
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'Search employees...';
        
        const tableContainer = document.querySelector('.table-responsive');
        if (tableContainer) {
            tableContainer.parentNode.insertBefore(searchInput, tableContainer);
            
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = document.querySelectorAll('#employeesTable tbody tr');
                
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
        animateCounters();
        
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Animate counters
    function animateCounters() {
        // Only animate counters that don't have data-no-animate attribute
        const counters = document.querySelectorAll('.h5.mb-0:not([data-no-animate])');
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
    
    // Export employees functionality
    window.exportEmployees = function() {
        showNotification('Export employees functionality coming soon!', 'info');
    };
    
    // Refresh employees
    window.refreshEmployees = function() {
        showNotification('Refreshing employees data...', 'info');
        location.reload();
    };
    
    // Print company details
    window.printCompanyDetails = function() {
        window.print();
    };
    
    // Share company information
    window.shareCompanyInfo = function() {
        if (navigator.share) {
            navigator.share({
                title: 'Company Information',
                text: `Company: ${document.querySelector('h1').textContent}`,
                url: window.location.href
            });
        } else {
            // Fallback: copy URL to clipboard
            navigator.clipboard.writeText(window.location.href).then(function() {
                showNotification('Company details URL copied to clipboard!', 'success');
            });
        }
    };
    
    console.log('Company details JavaScript initialized successfully!');
});
