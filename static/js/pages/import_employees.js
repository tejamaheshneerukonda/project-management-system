// Import Employees Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize import page
    initializeImportPage();
    
    // Download template function
    window.downloadTemplate = function() {
        const csvContent = 'employee_id,first_name,last_name,email,department,position\nEMP001,John,Doe,john.doe@company.com,IT,Developer\nEMP002,Jane,Smith,jane.smith@company.com,HR,Manager\nEMP003,Bob,Johnson,bob.johnson@company.com,Finance,Analyst';
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'employee_template.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('Template downloaded successfully!', 'success');
    };
    
    // Initialize import page
    function initializeImportPage() {
        // File upload enhancement
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            enhanceFileUpload(fileInput);
        }
        
        // Form validation
        const form = document.querySelector('.needs-validation');
        if (form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        }
        
        // Auto-hide alerts
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
        
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Enhance file upload
    function enhanceFileUpload(fileInput) {
        // Create drag and drop zone
        const dropZone = document.createElement('div');
        dropZone.className = 'file-drop-zone';
        dropZone.innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <h5>Drag & Drop CSV File Here</h5>
            <p class="text-muted">or click to browse</p>
        `;
        
        // Insert drop zone before file input
        fileInput.parentNode.insertBefore(dropZone, fileInput);
        fileInput.style.display = 'none';
        
        // Click to upload
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Drag and drop events
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                    fileInput.files = files;
                    updateFileDisplay(file.name, file.size);
                } else {
                    showNotification('Please select a CSV file.', 'error');
                }
            }
        });
        
        // File input change
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const file = this.files[0];
                updateFileDisplay(file.name, file.size);
            }
        });
    }
    
    // Update file display
    function updateFileDisplay(fileName, fileSize) {
        const dropZone = document.querySelector('.file-drop-zone');
        const fileSizeKB = (fileSize / 1024).toFixed(2);
        
        dropZone.innerHTML = `
            <i class="fas fa-file-csv text-success"></i>
            <h5 class="text-success">${fileName}</h5>
            <p class="text-muted">Size: ${fileSizeKB} KB</p>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="clearFile()">
                <i class="fas fa-times me-1"></i>Remove
            </button>
        `;
        
        dropZone.style.borderColor = 'var(--success-color)';
        dropZone.style.backgroundColor = 'rgba(34, 197, 94, 0.1)';
    }
    
    // Clear file
    window.clearFile = function() {
        const fileInput = document.querySelector('input[type="file"]');
        const dropZone = document.querySelector('.file-drop-zone');
        
        fileInput.value = '';
        dropZone.innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <h5>Drag & Drop CSV File Here</h5>
            <p class="text-muted">or click to browse</p>
        `;
        dropZone.style.borderColor = 'var(--gray-300)';
        dropZone.style.backgroundColor = 'var(--gray-50)';
    };
    
    // Form submission with loading state
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('btn-loading');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Importing...';
            }
        });
    }
    
    // CSV validation
    function validateCSV(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function(e) {
                const text = e.target.result;
                const lines = text.split('\n');
                const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
                
                const requiredHeaders = ['employee_id', 'first_name', 'last_name', 'email'];
                const missingHeaders = requiredHeaders.filter(h => !headers.includes(h));
                
                if (missingHeaders.length > 0) {
                    reject(`Missing required columns: ${missingHeaders.join(', ')}`);
                } else {
                    resolve(true);
                }
            };
            reader.readAsText(file);
        });
    }
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification ${type}`;
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
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
    
    // Preview CSV data
    window.previewCSV = function() {
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput.files.length === 0) {
            showNotification('Please select a CSV file first.', 'warning');
            return;
        }
        
        const file = fileInput.files[0];
        validateCSV(file).then(() => {
            showNotification('CSV file is valid!', 'success');
        }).catch(error => {
            showNotification(error, 'error');
        });
    };
    
    console.log('Import employees JavaScript initialized successfully!');
});
