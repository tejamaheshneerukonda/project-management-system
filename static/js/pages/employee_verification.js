// Employee Verification Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize verification page
    initializeVerificationPage();
    
    // Initialize verification page
    function initializeVerificationPage() {
        // Form validation
        const form = document.querySelector('.verification-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (!validateForm()) {
                    e.preventDefault();
                    e.stopPropagation();
                } else {
                    showLoadingState();
                }
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
        
        // Real-time validation
        const inputs = document.querySelectorAll('.verification-form input');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    }
    
    // Validate individual field
    function validateField(field) {
        if (field.checkValidity()) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }
    }
    
    // Validate form
    function validateForm() {
        const employeeId = document.querySelector('input[name="employee_id"]').value;
        const email = document.querySelector('input[name="email"]').value;
        
        let isValid = true;
        
        // Validate employee ID
        if (!employeeId || employeeId.length < 2) {
            isValid = false;
            showNotification('Please enter a valid Employee ID', 'error');
        }
        
        // Validate email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
            isValid = false;
            showNotification('Please enter a valid email address', 'error');
        }
        
        return isValid;
    }
    
    // Show loading state
    function showLoadingState() {
        const submitBtn = document.querySelector('.verification-button');
        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Verifying...';
        }
    }
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
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
    
    // Smooth scroll to errors
    function scrollToFirstError() {
        const firstError = document.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
    
    // Form submission error handling
    const form = document.querySelector('.verification-form');
    if (form) {
        form.addEventListener('invalid', function(e) {
            e.preventDefault();
            scrollToFirstError();
        });
    }
    
    // Auto-focus first input
    const firstInput = document.querySelector('.verification-form input');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Enter key handling
    const inputs = document.querySelectorAll('.verification-form input');
    inputs.forEach((input, index) => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                } else {
                    form.submit();
                }
            }
        });
    });
    
    // Input formatting
    const employeeIdInput = document.querySelector('input[name="employee_id"]');
    if (employeeIdInput) {
        employeeIdInput.addEventListener('input', function() {
            // Convert to uppercase
            this.value = this.value.toUpperCase();
        });
    }
    
    const emailInput = document.querySelector('input[name="email"]');
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            // Convert to lowercase
            this.value = this.value.toLowerCase();
        });
    }
    
    console.log('Employee verification JavaScript initialized successfully!');
});
