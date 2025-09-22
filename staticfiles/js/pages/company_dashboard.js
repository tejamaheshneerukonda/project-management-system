// Company Dashboard Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Copy functionality
    window.copyCompanyKey = function() {
        const keyInput = document.getElementById('companyKeyInput');
        navigator.clipboard.writeText(keyInput.value).then(function() {
            showNotification('Company key copied to clipboard!', 'success');
        }, function(err) {
            console.error('Could not copy text: ', err);
            showNotification('Failed to copy to clipboard', 'error');
        });
    };
    
    window.copyRegistrationUrl = function() {
        const urlInput = document.getElementById('registrationUrlInput');
        navigator.clipboard.writeText(urlInput.value).then(function() {
            showNotification('Registration URL copied to clipboard!', 'success');
        }, function(err) {
            console.error('Could not copy text: ', err);
            showNotification('Failed to copy to clipboard', 'error');
        });
    };
    
    // Show company key modal
    window.showCompanyKey = function() {
        const modal = new bootstrap.Modal(document.getElementById('companyKeyModal'));
        modal.show();
    };
    
    // Employee management functions
    window.viewEmployee = function(employeeId) {
        console.log('Viewing employee:', employeeId);
        showNotification('Employee details functionality coming soon!', 'info');
    };
    
    window.editEmployee = function(employeeId) {
        console.log('Editing employee:', employeeId);
        showNotification('Edit employee functionality coming soon!', 'info');
    };
    
    window.deleteEmployee = function(employeeId) {
        if (confirm('Are you sure you want to delete this employee? This action cannot be undone.')) {
            console.log('Deleting employee:', employeeId);
            showNotification('Delete employee functionality coming soon!', 'info');
        }
    };
    
    // Export functions
    window.exportEmployees = function() {
        console.log('Exporting employees...');
        showNotification('Export functionality coming soon!', 'info');
    };
    
    // Settings function
    window.showSettings = function() {
        console.log('Showing settings...');
        showNotification('Settings functionality coming soon!', 'info');
    };
    
    // Refresh employees
    window.refreshEmployees = function() {
        location.reload();
    };
    
    // Send instructions
    window.sendInstructions = function() {
        console.log('Sending instructions...');
        showNotification('Email instructions functionality coming soon!', 'info');
    };
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification ${type}`;
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
    
    // Initialize dashboard
    function initializeDashboard() {
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
    
    // Quick action buttons animation
    const quickActionBtns = document.querySelectorAll('.quick-actions .btn');
    quickActionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    console.log('Company dashboard JavaScript initialized successfully!');
});
