// Payment Test Helper JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Payment test helper loaded');
    
    // Test payment data
    const testPaymentData = {
        visa: {
            cardNumber: '4111 1111 1111 1111',
            cardholderName: 'Test User',
            expiryDate: '12/25',
            cvv: '123',
            billingAddress: '123 Test Street\nTest City, TC 12345\nUnited States'
        },
        mastercard: {
            cardNumber: '5555 5555 5555 4444',
            cardholderName: 'Test User',
            expiryDate: '12/25',
            cvv: '123',
            billingAddress: '123 Test Street\nTest City, TC 12345\nUnited States'
        },
        amex: {
            cardNumber: '3782 822463 10005',
            cardholderName: 'Test User',
            expiryDate: '12/25',
            cvv: '1234',
            billingAddress: '123 Test Street\nTest City, TC 12345\nUnited States'
        }
    };
    
    // Test registration data
    const testRegistrationData = {
        fullName: 'Test User',
        email: 'test@example.com',
        password: 'TestPassword123!',
        confirmPassword: 'TestPassword123!'
    };
    
    // Auto-fill payment form with test data
    function fillPaymentForm(cardType = 'visa') {
        const data = testPaymentData[cardType];
        if (!data) return;
        
        document.getElementById('cardNumber').value = data.cardNumber;
        document.getElementById('cardholderName').value = data.cardholderName;
        document.getElementById('expiryDate').value = data.expiryDate;
        document.getElementById('cvv').value = data.cvv;
        document.getElementById('billingAddress').value = data.billingAddress;
        
        console.log(`Payment form filled with ${cardType} test data`);
    }
    
    // Auto-fill registration form with test data
    function fillRegistrationForm() {
        document.getElementById('fullName').value = testRegistrationData.fullName;
        document.getElementById('email').value = testRegistrationData.email;
        document.getElementById('password').value = testRegistrationData.password;
        document.getElementById('confirmPassword').value = testRegistrationData.confirmPassword;
        
        console.log('Registration form filled with test data');
    }
    
    // Add test buttons to the page
    function addTestButtons() {
        // Check if we're on payment page
        const paymentForm = document.getElementById('paymentForm');
        const registrationForm = document.getElementById('registrationForm');
        
        if (paymentForm) {
            // Add test buttons for payment form
            const testButtonContainer = document.createElement('div');
            testButtonContainer.className = 'test-buttons mb-3';
            testButtonContainer.innerHTML = `
                <div class="alert alert-warning">
                    <h6><i class="fas fa-flask me-2"></i>Test Mode</h6>
                    <p class="mb-2">Use these buttons to quickly fill the form with test data:</p>
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="fillPaymentForm('visa')">
                            <i class="fab fa-cc-visa me-1"></i>Visa Test
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="fillPaymentForm('mastercard')">
                            <i class="fab fa-cc-mastercard me-1"></i>Mastercard Test
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="fillPaymentForm('amex')">
                            <i class="fab fa-cc-amex me-1"></i>Amex Test
                        </button>
                    </div>
                </div>
            `;
            
            paymentForm.insertBefore(testButtonContainer, paymentForm.firstChild);
        }
        
        if (registrationForm) {
            // Add test button for registration form
            const testButtonContainer = document.createElement('div');
            testButtonContainer.className = 'test-buttons mb-3';
            testButtonContainer.innerHTML = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-user-plus me-2"></i>Test Registration</h6>
                    <p class="mb-2">Click the button below to fill the form with test data:</p>
                    <button type="button" class="btn btn-sm btn-outline-info" onclick="fillRegistrationForm()">
                        <i class="fas fa-magic me-1"></i>Fill Test Data
                    </button>
                </div>
            `;
            
            registrationForm.insertBefore(testButtonContainer, registrationForm.firstChild);
        }
    }
    
    // Make functions globally available
    window.fillPaymentForm = fillPaymentForm;
    window.fillRegistrationForm = fillRegistrationForm;
    
    // Add test buttons to the page
    addTestButtons();
    
    // Add keyboard shortcuts for testing
    document.addEventListener('keydown', function(e) {
        // Ctrl + Shift + V for Visa test data
        if (e.ctrlKey && e.shiftKey && e.key === 'V') {
            e.preventDefault();
            fillPaymentForm('visa');
        }
        
        // Ctrl + Shift + M for Mastercard test data
        if (e.ctrlKey && e.shiftKey && e.key === 'M') {
            e.preventDefault();
            fillPaymentForm('mastercard');
        }
        
        // Ctrl + Shift + A for Amex test data
        if (e.ctrlKey && e.shiftKey && e.key === 'A') {
            e.preventDefault();
            fillPaymentForm('amex');
        }
        
        // Ctrl + Shift + R for registration test data
        if (e.ctrlKey && e.shiftKey && e.key === 'R') {
            e.preventDefault();
            fillRegistrationForm();
        }
    });
    
    // Add form validation simulation
    function simulatePaymentProcessing() {
        const submitButton = document.querySelector('#submitPayment');
        if (submitButton) {
            submitButton.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Show loading state
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                this.disabled = true;
                
                // Simulate processing delay
                setTimeout(() => {
                    // Redirect to dashboard without popup
                    window.location.href = '/company/dashboard/';
                }, 1000);
            });
        }
    }
    
    // Add registration simulation
    function simulateRegistrationProcessing() {
        const submitButton = document.querySelector('#submitRegistration');
        if (submitButton) {
            submitButton.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Show loading state
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Account...';
                this.disabled = true;
                
                // Simulate processing delay
                setTimeout(() => {
                    // Redirect to dashboard without popup
                    window.location.href = '/company/dashboard/';
                }, 1000);
            });
        }
    }
    
    // Initialize simulations
    simulatePaymentProcessing();
    simulateRegistrationProcessing();
    
    console.log('Payment test helper initialized');
    console.log('Keyboard shortcuts: Ctrl+Shift+V (Visa), Ctrl+Shift+M (Mastercard), Ctrl+Shift+A (Amex), Ctrl+Shift+R (Registration)');
});
