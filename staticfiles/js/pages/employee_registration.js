// Employee Registration Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize registration page
    initializeRegistrationPage();
    
    // Toggle password visibility
    window.togglePassword = function(inputId) {
        const input = document.getElementById(inputId);
        const button = input.nextElementSibling;
        const icon = button.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    };
    
    // Initialize registration page
    function initializeRegistrationPage() {
        // Password strength checker
        const passwordInput = document.querySelector('input[name="password"]');
        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                checkPasswordStrength(this.value);
            });
        }
        
        // Confirm password checker
        const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', function() {
                checkPasswordMatch();
            });
        }
        
        // Username availability checker
        const usernameInput = document.querySelector('input[name="username"]');
        if (usernameInput) {
            usernameInput.addEventListener('blur', function() {
                checkUsernameAvailability(this.value);
            });
        }
        
        // Form submission
        const form = document.querySelector('.registration-form');
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
    }
    
    // Check password strength
    function checkPasswordStrength(password) {
        const strengthFill = document.getElementById('passwordStrengthFill');
        const strengthText = document.getElementById('passwordStrengthText');
        
        if (!strengthFill || !strengthText) return;
        
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
        
        // Determine strength level
        if (strength < 3) {
            strengthFill.className = 'password-strength-fill weak';
            strengthText.className = 'password-strength-text weak';
            strengthText.textContent = 'Weak password';
        } else if (strength < 5) {
            strengthFill.className = 'password-strength-fill fair';
            strengthText.className = 'password-strength-text fair';
            strengthText.textContent = 'Fair password';
        } else if (strength < 6) {
            strengthFill.className = 'password-strength-fill good';
            strengthText.className = 'password-strength-text good';
            strengthText.textContent = 'Good password';
        } else {
            strengthFill.className = 'password-strength-fill strong';
            strengthText.className = 'password-strength-text strong';
            strengthText.textContent = 'Strong password';
        }
    }
    
    // Check password match
    function checkPasswordMatch() {
        const password = document.querySelector('input[name="password"]').value;
        const confirmPassword = document.querySelector('input[name="confirm_password"]').value;
        const confirmInput = document.querySelector('input[name="confirm_password"]');
        
        if (confirmPassword && password !== confirmPassword) {
            confirmInput.setCustomValidity('Passwords do not match');
            confirmInput.classList.add('is-invalid');
        } else {
            confirmInput.setCustomValidity('');
            confirmInput.classList.remove('is-invalid');
        }
    }
    
    // Check username availability (placeholder)
    function checkUsernameAvailability(username) {
        if (!username) return;
        
        // This would typically make an AJAX call to check username availability
        // For now, we'll just simulate it
        const usernameInput = document.querySelector('input[name="username"]');
        
        // Basic validation
        if (username.length < 3) {
            usernameInput.setCustomValidity('Username must be at least 3 characters');
            usernameInput.classList.add('is-invalid');
        } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            usernameInput.setCustomValidity('Username can only contain letters, numbers, and underscores');
            usernameInput.classList.add('is-invalid');
        } else {
            usernameInput.setCustomValidity('');
            usernameInput.classList.remove('is-invalid');
        }
    }
    
    // Validate form
    function validateForm() {
        const form = document.querySelector('.registration-form');
        const password = document.querySelector('input[name="password"]').value;
        const confirmPassword = document.querySelector('input[name="confirm_password"]').value;
        const termsCheck = document.getElementById('termsCheck');
        
        let isValid = true;
        
        // Check password match
        if (password !== confirmPassword) {
            isValid = false;
        }
        
        // Check terms acceptance
        if (!termsCheck.checked) {
            isValid = false;
            showNotification('Please accept the Terms of Service and Privacy Policy', 'error');
        }
        
        // Check password strength
        if (password.length < 8) {
            isValid = false;
            showNotification('Password must be at least 8 characters long', 'error');
        }
        
        return isValid;
    }
    
    // Show loading state
    function showLoadingState() {
        const submitBtn = document.querySelector('.registration-button');
        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Account...';
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
    
    // Real-time form validation
    const inputs = document.querySelectorAll('.registration-form input');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid') && this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });
    
    // Smooth scroll to errors
    function scrollToFirstError() {
        const firstError = document.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
    
    // Form submission error handling
    const form = document.querySelector('.registration-form');
    if (form) {
        form.addEventListener('invalid', function(e) {
            e.preventDefault();
            scrollToFirstError();
        });
    }
    
    console.log('Employee registration JavaScript initialized successfully!');
});
