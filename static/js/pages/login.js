// Login Page Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Login page specific functionality
    
    // Form validation
    const loginForm = document.querySelector('.login-form');
    const usernameInput = document.querySelector('#username');
    const passwordInput = document.querySelector('#password');
    const loginButton = document.querySelector('.login-button');
    
    if (loginForm) {
        // Real-time validation
        usernameInput.addEventListener('input', validateUsername);
        passwordInput.addEventListener('input', validatePassword);
        
        // Form submission
        loginForm.addEventListener('submit', function(e) {
            if (validateForm()) {
                // Let the form submit normally to the server
                // Django will handle the authentication and redirect
                // No need to show loading state as page will redirect
            } else {
                e.preventDefault();
            }
        });
    }
    
    function validateUsername() {
        const username = usernameInput.value.trim();
        const isValid = username.length >= 3;
        
        updateInputState(usernameInput, isValid);
        return isValid;
    }
    
    function validatePassword() {
        const password = passwordInput.value;
        const isValid = password.length >= 6;
        
        updateInputState(passwordInput, isValid);
        return isValid;
    }
    
    function validateForm() {
        const usernameValid = validateUsername();
        const passwordValid = validatePassword();
        
        return usernameValid && passwordValid;
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
    
    // Loading state functions removed - Django handles redirect after login
    
    // Password visibility toggle
    const passwordToggle = document.createElement('button');
    passwordToggle.type = 'button';
    passwordToggle.className = 'password-toggle';
    passwordToggle.innerHTML = '<i class="fas fa-eye"></i>';
    passwordToggle.style.cssText = `
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
    
    if (passwordInput) {
        passwordInput.parentNode.style.position = 'relative';
        passwordInput.parentNode.appendChild(passwordToggle);
        
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }
    
    // Auto-focus on username field
    if (usernameInput) {
        usernameInput.focus();
    }
    
    // Enter key navigation
    usernameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            passwordInput.focus();
        }
    });
    
    passwordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Remember me functionality
    const rememberCheckbox = document.querySelector('#remember');
    if (rememberCheckbox) {
        // Load saved username if remember me was checked
        const savedUsername = localStorage.getItem('rememberedUsername');
        if (savedUsername) {
            usernameInput.value = savedUsername;
            rememberCheckbox.checked = true;
        }
        
        // Save username when form is submitted
        loginForm.addEventListener('submit', function() {
            if (rememberCheckbox.checked) {
                localStorage.setItem('rememberedUsername', usernameInput.value);
            } else {
                localStorage.removeItem('rememberedUsername');
            }
        });
    }
    
    // Form animation on load
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.opacity = '0';
        loginCard.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            loginCard.style.transition = 'all 0.6s ease';
            loginCard.style.opacity = '1';
            loginCard.style.transform = 'translateY(0)';
        }, 100);
    }
    
    console.log('Login page JavaScript initialized successfully!');
});
