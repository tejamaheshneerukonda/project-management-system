// Register Company Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize register company page
    initializeRegisterCompanyPage();
    
    // Initialize register company page
    function initializeRegisterCompanyPage() {
        // Form validation
        const form = document.querySelector('.needs-validation');
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
        
        // Real-time validation
        const inputs = document.querySelectorAll('.form-control');
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
        
        // Domain validation
        const domainInput = document.querySelector('input[name="domain"]');
        if (domainInput) {
            domainInput.addEventListener('input', function() {
                formatDomain(this);
            });
        }
        
        // Email validation
        const emailInput = document.querySelector('input[name="admin_email"]');
        if (emailInput) {
            emailInput.addEventListener('blur', function() {
                validateEmail(this);
            });
        }
        
        // Username validation
        const usernameInput = document.querySelector('input[name="admin_username"]');
        if (usernameInput) {
            usernameInput.addEventListener('blur', function() {
                validateUsername(this);
            });
        }
        
        // Password strength checker
        const passwordInput = document.querySelector('input[name="admin_password"]');
        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                checkPasswordStrength(this.value);
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
    
    // Format domain input
    function formatDomain(input) {
        let value = input.value.toLowerCase();
        // Remove protocol if present
        value = value.replace(/^https?:\/\//, '');
        // Remove www if present
        value = value.replace(/^www\./, '');
        // Remove trailing slash
        value = value.replace(/\/$/, '');
        input.value = value;
    }
    
    // Validate email
    function validateEmail(input) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (input.value && !emailRegex.test(input.value)) {
            input.setCustomValidity('Please enter a valid email address');
            input.classList.add('is-invalid');
        } else {
            input.setCustomValidity('');
            input.classList.remove('is-invalid');
        }
    }
    
    // Validate username
    function validateUsername(input) {
        if (input.value && input.value.length < 3) {
            input.setCustomValidity('Username must be at least 3 characters');
            input.classList.add('is-invalid');
        } else if (input.value && !/^[a-zA-Z0-9_]+$/.test(input.value)) {
            input.setCustomValidity('Username can only contain letters, numbers, and underscores');
            input.classList.add('is-invalid');
        } else {
            input.setCustomValidity('');
            input.classList.remove('is-invalid');
        }
    }
    
    // Check password strength
    function checkPasswordStrength(password) {
        let strength = 0;
        let strengthLabel = '';
        
        // Length check
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        
        // Character variety checks
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        // Update UI if password strength indicator exists
        const strengthIndicator = document.getElementById('passwordStrength');
        if (strengthIndicator) {
            if (strength < 3) {
                strengthIndicator.textContent = 'Weak password';
                strengthIndicator.className = 'text-danger';
            } else if (strength < 5) {
                strengthIndicator.textContent = 'Fair password';
                strengthIndicator.className = 'text-warning';
            } else if (strength < 6) {
                strengthIndicator.textContent = 'Good password';
                strengthIndicator.className = 'text-info';
            } else {
                strengthIndicator.textContent = 'Strong password';
                strengthIndicator.className = 'text-success';
            }
        }
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
        const companyName = document.querySelector('input[name="name"]').value;
        const domain = document.querySelector('input[name="domain"]').value;
        const adminUsername = document.querySelector('input[name="admin_username"]').value;
        const adminEmail = document.querySelector('input[name="admin_email"]').value;
        const adminPassword = document.querySelector('input[name="admin_password"]').value;
        
        let isValid = true;
        
        // Validate company name
        if (!companyName || companyName.length < 2) {
            isValid = false;
            showNotification('Please enter a valid company name', 'error');
        }
        
        // Validate domain
        const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
        if (!domain || !domainRegex.test(domain)) {
            isValid = false;
            showNotification('Please enter a valid domain (e.g., company.com)', 'error');
        }
        
        // Validate admin username
        if (!adminUsername || adminUsername.length < 3) {
            isValid = false;
            showNotification('Admin username must be at least 3 characters', 'error');
        }
        
        // Validate admin email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!adminEmail || !emailRegex.test(adminEmail)) {
            isValid = false;
            showNotification('Please enter a valid admin email address', 'error');
        }
        
        // Validate admin password
        if (!adminPassword || adminPassword.length < 8) {
            isValid = false;
            showNotification('Admin password must be at least 8 characters', 'error');
        }
        
        return isValid;
    }
    
    // Show loading state
    function showLoadingState() {
        const submitBtn = document.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Registering Company...';
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
    const form = document.querySelector('.needs-validation');
    if (form) {
        form.addEventListener('invalid', function(e) {
            e.preventDefault();
            scrollToFirstError();
        });
    }
    
    // Auto-focus first input
    const firstInput = document.querySelector('.form-control');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Enter key handling
    const inputs = document.querySelectorAll('.form-control');
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
    
    // Generate company key preview (for demo purposes)
    window.generateKeyPreview = function() {
        const preview = document.getElementById('keyPreview');
        if (preview) {
            const key = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
            preview.textContent = key;
        }
    };
    
    console.log('Register company JavaScript initialized successfully!');
});
