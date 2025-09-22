document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add fade-in animation to pricing cards
    const pricingCards = document.querySelectorAll('.pricing-card');
    pricingCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
            card.classList.add('fade-in');
        }, index * 200);
    });

    // Add hover effects to pricing cards
    pricingCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Billing toggle functionality
    const toggleOptions = document.querySelectorAll('.toggle-option');
    toggleOptions.forEach(option => {
        const radioInput = option.querySelector('input[type="radio"]');
        
        // Handle radio button change
        radioInput.addEventListener('change', function() {
            if (this.checked) {
                // Remove active class from all options in the same card
                const card = option.closest('.pricing-card');
                const allOptions = card.querySelectorAll('.toggle-option');
                allOptions.forEach(opt => opt.classList.remove('active'));

                // Add active class to selected option
                option.classList.add('active');

                // Update toggle switch indicator
                const toggleSwitch = card.querySelector('.toggle-switch');
                if (this.value === 'YEARLY') {
                    toggleSwitch.classList.add('yearly-active');
                } else {
                    toggleSwitch.classList.remove('yearly-active');
                }

                // Update pricing display
                updatePricingDisplay(card, this.value);

                // Update the select plan button with selected plan info
                const planId = option.getAttribute('data-plan-id');
                const selectBtn = card.querySelector('.cta-button');
                if (selectBtn) {
                    selectBtn.setAttribute('data-plan-id', planId);
                }
            }
        });

        // Handle click on option (for better UX)
        option.addEventListener('click', function(e) {
            if (e.target !== radioInput) {
                radioInput.checked = true;
                radioInput.dispatchEvent(new Event('change'));
            }
        });
    });

    // Update pricing display based on selected billing cycle
    function updatePricingDisplay(card, billingCycle) {
        const priceSections = card.querySelectorAll('.price-section');
        priceSections.forEach(section => {
            section.classList.remove('active');
            if (section.getAttribute('data-plan') === billingCycle) {
                section.classList.add('active');
            }
        });
    }

    // Plan selection function
    window.selectPlan = function(planType) {
        const card = event.target.closest('.pricing-card');
        const activeOption = card.querySelector('.toggle-option.active');

        if (activeOption) {
            const planId = activeOption.getAttribute('data-plan-id');
            const activePriceSection = card.querySelector('.price-section.active');
            const planPrice = activePriceSection.querySelector('.amount').textContent;
            const planPeriod = activePriceSection.querySelector('.price-period').textContent;

            // Show selection confirmation
            const confirmation = confirm(`Select ${planType} plan?\n\nPrice: $${planPrice} ${planPeriod}\n\nThis will redirect to company subscription assignment.`);

            if (confirmation) {
                // Add loading state
                const button = event.target;
                button.classList.add('loading');
                button.disabled = true;

                // Simulate API call
                setTimeout(() => {
                    showSuccessToast(`Selected ${planType} plan!\n\nPrice: $${planPrice} ${planPeriod}\n\nPlan ID: ${planId}\n\nIn a real implementation, this would redirect to subscription assignment.`);
                    
                    // Remove loading state
                    button.classList.remove('loading');
                    button.disabled = false;
                }, 1000);
            }
        } else {
            showWarningToast('Please select a billing cycle first.');
        }
    };

    // Initialize active states
    toggleOptions.forEach(option => {
        if (option.classList.contains('active')) {
            const card = option.closest('.pricing-card');
            const selectBtn = card.querySelector('.cta-button');
            if (selectBtn) {
                const planId = option.getAttribute('data-plan-id');
                selectBtn.setAttribute('data-plan-id', planId);
            }
        }
    });

    // Add keyboard navigation for toggle options
    toggleOptions.forEach(option => {
        option.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const radioInput = this.querySelector('input[type="radio"]');
                radioInput.checked = true;
                radioInput.dispatchEvent(new Event('change'));
            }
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.cta-button, .action-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add ripple effect CSS
    const style = document.createElement('style');
    style.textContent = `
        .cta-button, .action-btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    console.log('Dark Theme Subscription Plans page loaded successfully!');
});