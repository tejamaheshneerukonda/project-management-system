// Pricing Page Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Pricing toggle functionality
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
            const confirmation = confirm(`Select ${planType} plan?\n\nPrice: $${planPrice} ${planPeriod}\n\nThis will redirect to registration.`);

            if (confirmation) {
                // Add loading state
                const button = event.target;
                button.classList.add('loading');
                button.disabled = true;

                // Simulate API call
                setTimeout(() => {
                    // Redirect to company admin registration with plan info
                    window.location.href = `/company-admin-register/?plan=${planId}`;

                    // Remove loading state
                    button.classList.remove('loading');
                    button.disabled = false;
                }, 1000);
            }
        } else {
            alert('Please select a billing cycle first.');
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

    // Ensure toggle switches start in correct state (Monthly default)
    const toggleSwitches = document.querySelectorAll('.toggle-switch');
    toggleSwitches.forEach(switchEl => {
        // Remove any existing yearly-active class to ensure Monthly is default
        switchEl.classList.remove('yearly-active');

        // Find the Monthly option and ensure it's active
        const monthlyOption = switchEl.querySelector('input[value="MONTHLY"]');
        if (monthlyOption && !monthlyOption.checked) {
            monthlyOption.checked = true;
            monthlyOption.dispatchEvent(new Event('change'));
        }
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

    // Add animation to FAQ accordion
    const accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.no-plans-card, .contact-cta, .accordion').forEach(el => {
        observer.observe(el);
    });

    // Add loading state styles
    const style = document.createElement('style');
    style.textContent = `
        .cta-button.loading {
            position: relative;
            color: transparent !important;
        }
        
        .cta-button.loading::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 20px;
            height: 20px;
            border: 2px solid transparent;
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
        }
        
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
        
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);

    console.log('Pricing page JavaScript initialized successfully!');
});
