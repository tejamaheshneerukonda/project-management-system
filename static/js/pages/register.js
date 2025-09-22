// Register Page Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Register page specific functionality
    
    // Form elements
    const registerForm = document.querySelector('.register-form');
    const usernameInput = document.querySelector('#username');
    const emailInput = document.querySelector('#email');
    const passwordInput = document.querySelector('#password');
    const confirmPasswordInput = document.querySelector('#confirm_password');
    const termsCheckbox = document.querySelector('#terms');
    const registerButton = document.querySelector('.register-button');
    
    if (registerForm) {
        // Real-time validation
        usernameInput.addEventListener('input', validateUsername);
        emailInput.addEventListener('input', validateEmail);
        passwordInput.addEventListener('input', validatePassword);
        confirmPasswordInput.addEventListener('input', validateConfirmPassword);
        termsCheckbox.addEventListener('change', validateTerms);
        
        // Form submission
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (validateForm()) {
                showLoadingState();
                
                // Simulate registration process
                setTimeout(() => {
                    hideLoadingState();
                    showSuccessMessage();
                }, 2000);
            }
        });
    }
    
    function validateUsername() {
        const username = usernameInput.value.trim();
        const isValid = username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username);
        
        updateInputState(usernameInput, isValid);
        return isValid;
    }
    
    function validateEmail() {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(email);
        
        updateInputState(emailInput, isValid);
        return isValid;
    }
    
    function validatePassword() {
        const password = passwordInput.value;
        const isValid = password.length >= 8;
        
        updateInputState(passwordInput, isValid);
        updatePasswordStrength(password);
        return isValid;
    }
    
    function validateConfirmPassword() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const isValid = password === confirmPassword && password.length > 0;
        
        updateInputState(confirmPasswordInput, isValid);
        return isValid;
    }
    
    function validateTerms() {
        const isValid = termsCheckbox.checked;
        
        if (isValid) {
            termsCheckbox.classList.remove('is-invalid');
        } else {
            termsCheckbox.classList.add('is-invalid');
        }
        
        return isValid;
    }
    
    function validateForm() {
        const usernameValid = validateUsername();
        const emailValid = validateEmail();
        const passwordValid = validatePassword();
        const confirmPasswordValid = validateConfirmPassword();
        const termsValid = validateTerms();
        
        return usernameValid && emailValid && passwordValid && confirmPasswordValid && termsValid;
    }
    
    function updateInputState(input, isValid) {
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    }
    
    function updatePasswordStrength(password) {
        const strengthIndicator = document.querySelector('.password-strength');
        if (!strengthIndicator) return;
        
        let strength = 0;
        let strengthClass = '';
        
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        switch (strength) {
            case 0:
            case 1:
                strengthClass = 'password-strength-weak';
                break;
            case 2:
                strengthClass = 'password-strength-fair';
                break;
            case 3:
            case 4:
                strengthClass = 'password-strength-good';
                break;
            case 5:
                strengthClass = 'password-strength-strong';
                break;
        }
        
        strengthIndicator.className = `password-strength ${strengthClass}`;
    }
    
    function showLoadingState() {
        registerButton.disabled = true;
        registerButton.innerHTML = '<span class="loading"></span> Creating Account...';
    }
    
    function hideLoadingState() {
        registerButton.disabled = false;
        registerButton.innerHTML = '<i class="fas fa-user-plus me-2"></i>Create Account';
    }
    
    function showSuccessMessage() {
        const successMessage = document.createElement('div');
        successMessage.className = 'alert alert-success alert-dismissible fade show';
        successMessage.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            Account created successfully! Redirecting to dashboard...
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        registerForm.parentNode.insertBefore(successMessage, registerForm);
        
        setTimeout(() => {
            window.location.href = '/dashboard/';
        }, 2000);
    }
    
    // Password visibility toggles
    function createPasswordToggle(input) {
        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'password-toggle';
        toggle.innerHTML = '<i class="fas fa-eye"></i>';
        toggle.style.cssText = `
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--gray-500);
            cursor: pointer;
            z-index: 2;
        `;
        
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(toggle);
        
        toggle.addEventListener('click', function() {
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }
    
    // Add password toggles
    createPasswordToggle(passwordInput);
    createPasswordToggle(confirmPasswordInput);
    
    // Auto-focus on username field
    if (usernameInput) {
        usernameInput.focus();
    }
    
    // Tab navigation
    usernameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            emailInput.focus();
        }
    });
    
    emailInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            passwordInput.focus();
        }
    });
    
    passwordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            confirmPasswordInput.focus();
        }
    });
    
    confirmPasswordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            registerForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Form animation on load
    const registerCard = document.querySelector('.register-card');
    if (registerCard) {
        registerCard.style.opacity = '0';
        registerCard.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            registerCard.style.transition = 'all 0.6s ease';
            registerCard.style.opacity = '1';
            registerCard.style.transform = 'translateY(0)';
        }, 100);
    }
    
    console.log('Register page JavaScript initialized successfully!');
});
