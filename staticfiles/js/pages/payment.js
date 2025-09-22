// Payment Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Card number formatting
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            if (formattedValue.length > 19) {
                formattedValue = formattedValue.substr(0, 19);
            }
            e.target.value = formattedValue;
        });
    }

    // Expiry date formatting
    const expiryInput = document.getElementById('expiryDate');
    if (expiryInput) {
        expiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }

    // CVV formatting
    const cvvInput = document.getElementById('cvv');
    if (cvvInput) {
        cvvInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        });
    }

    // Plan selection handling
    const planOptions = document.querySelectorAll('input[name="plan_selection"]');
    planOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Remove active class from all options
            document.querySelectorAll('.plan-option').forEach(plan => {
                plan.classList.remove('selected');
            });
            
            // Add active class to selected option
            this.closest('.plan-option').classList.add('selected');
            
            // Update form with selected plan
            updateSelectedPlan(this.value);
        });
    });

    // Set default selection
    const defaultOption = document.querySelector('input[name="plan_selection"]:checked');
    if (defaultOption) {
        defaultOption.closest('.plan-option').classList.add('selected');
        updateSelectedPlan(defaultOption.value);
    }

    // Form submission
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (validateForm()) {
                processPayment();
            }
        });
    }

    // Add loading state to submit button
    const submitButton = document.getElementById('submitPayment');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            this.classList.add('loading');
            this.disabled = true;
            
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            // Reset after 3 seconds (in real app, this would be handled by server response)
            setTimeout(() => {
                this.classList.remove('loading');
                this.disabled = false;
                this.innerHTML = originalContent;
            }, 3000);
        });
    }

    // Add hover effects to plan options
    const planOptionsElements = document.querySelectorAll('.plan-option');
    planOptionsElements.forEach(option => {
        option.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        option.addEventListener('mouseleave', function() {
            if (!this.classList.contains('selected')) {
                this.style.transform = 'translateY(0)';
            }
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add animation to form elements
    const formElements = document.querySelectorAll('.form-control');
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.3s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Add animation to plan options
    planOptionsElements.forEach((option, index) => {
        option.style.opacity = '0';
        option.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            option.style.transition = 'all 0.3s ease';
            option.style.opacity = '1';
            option.style.transform = 'translateX(0)';
        }, index * 150);
    });

    // Add tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Free plan access function
    window.accessFreePlan = function() {
        // For free plan, redirect directly to registration or dashboard
        if (confirm('Get free access to ProjectManager Pro? You can start using it immediately!')) {
            // Redirect to registration for new users, or dashboard for existing users
            window.location.href = '/register/';
        }
    };

    // Functions
    function updateSelectedPlan(planId) {
        // In a real application, this would update the form with plan details
        console.log('Selected plan:', planId);
        
        // Update any hidden fields or display selected plan info
        const selectedPlan = document.querySelector(`input[value="${planId}"]`);
        if (selectedPlan) {
            const planName = selectedPlan.closest('.plan-option').querySelector('.plan-name').textContent;
            const planPrice = selectedPlan.closest('.plan-option').querySelector('.billing-price').textContent;
            
            // Update form or display selected plan info
            console.log(`Selected: ${planName} - ${planPrice}`);
        }
    }

    function validateForm() {
        const cardNumber = document.getElementById('cardNumber').value;
        const cardholderName = document.getElementById('cardholderName').value;
        const expiryDate = document.getElementById('expiryDate').value;
        const cvv = document.getElementById('cvv').value;
        const billingAddress = document.getElementById('billingAddress').value;
        const termsCheck = document.getElementById('termsCheck').checked;
        const selectedPlan = document.querySelector('input[name="plan_selection"]:checked');

        let isValid = true;
        let errorMessage = '';

        // Validate card number (basic Luhn algorithm check)
        if (!cardNumber || cardNumber.replace(/\s/g, '').length < 13) {
            isValid = false;
            errorMessage += 'Please enter a valid card number.\n';
        }

        // Validate cardholder name
        if (!cardholderName || cardholderName.trim().length < 2) {
            isValid = false;
            errorMessage += 'Please enter a valid cardholder name.\n';
        }

        // Validate expiry date
        if (!expiryDate || !/^\d{2}\/\d{2}$/.test(expiryDate)) {
            isValid = false;
            errorMessage += 'Please enter a valid expiry date (MM/YY).\n';
        }

        // Validate CVV
        if (!cvv || cvv.length < 3) {
            isValid = false;
            errorMessage += 'Please enter a valid CVV.\n';
        }

        // Validate billing address
        if (!billingAddress || billingAddress.trim().length < 10) {
            isValid = false;
            errorMessage += 'Please enter a valid billing address.\n';
        }

        // Validate terms acceptance
        if (!termsCheck) {
            isValid = false;
            errorMessage += 'Please accept the terms and conditions.\n';
        }

        // Validate plan selection
        if (!selectedPlan) {
            isValid = false;
            errorMessage += 'Please select a plan.\n';
        }

        if (!isValid) {
            showNotification(errorMessage, 'error');
        }

        return isValid;
    }

    function processPayment() {
        // In a real application, this would send the payment data to a secure server
        // For demo purposes, we'll simulate a successful payment
        
        showNotification('Payment processed successfully! Starting your free trial...', 'success');
        
        // Redirect to dashboard after successful payment
        setTimeout(() => {
            window.location.href = '/dashboard/';
        }, 2000);
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 500px;';
        notification.innerHTML = `
            ${message.replace(/\n/g, '<br>')}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(102, 126, 234, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .plan-option.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(102, 126, 234, 0.1));
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        }
        
        .form-control {
            transition: all 0.3s ease;
        }
        
        .btn {
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-1px);
        }
        
        .plan-option {
            transition: all 0.3s ease;
        }
        
        .billing-content {
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);

    console.log('Payment page JavaScript initialized successfully!');
});
