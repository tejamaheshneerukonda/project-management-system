// ProjectManager Pro - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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

    // Add fade-in animation to elements
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

    // Observe all feature boxes and cards
    document.querySelectorAll('.feature-box, .stat-box, .card').forEach(el => {
        observer.observe(el);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Loading button functionality
    document.querySelectorAll('.btn-loading').forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading"></span> Loading...';
            this.disabled = true;
            
            // Re-enable after 3 seconds (adjust as needed)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }

    // Counter animation for stats
    function animateCounters() {
        const counters = document.querySelectorAll('.stat-box h3');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
            const duration = 2000; // 2 seconds
            const increment = target / (duration / 16); // 60fps
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                // Format the number based on original text
                const originalText = counter.textContent;
                if (originalText.includes('K')) {
                    counter.textContent = Math.floor(current / 1000) + 'K+';
                } else if (originalText.includes('%')) {
                    counter.textContent = Math.floor(current) + '%';
                } else if (originalText.includes('/')) {
                    counter.textContent = Math.floor(current) + '/7';
                } else {
                    counter.textContent = Math.floor(current) + '+';
                }
            }, 16);
        });
    }

    // Trigger counter animation when stats section is visible
    const statsSection = document.querySelector('.bg-light');
    if (statsSection) {
        const statsObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    statsObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        statsObserver.observe(statsSection);
    }

    // Search functionality (if search input exists)
    const searchInput = document.querySelector('#searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const searchableElements = document.querySelectorAll('[data-searchable]');
            
            searchableElements.forEach(element => {
                const text = element.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    element.style.display = '';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    }

    // Theme toggle (if theme toggle exists)
    const themeToggle = document.querySelector('#themeToggle');
    const themeIcon = document.querySelector('#themeIcon');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            // Update icon
            if (themeIcon) {
                themeIcon.className = isDark ? 'fas fa-moon' : 'fas fa-sun';
            }
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            if (themeIcon) {
                themeIcon.className = 'fas fa-moon';
            }
        } else {
            if (themeIcon) {
                themeIcon.className = 'fas fa-sun';
            }
        }
    }

    // Universal readability fix for all pages
    function applyUniversalReadabilityFix() {
        // Force all modals to be light theme
        const modals = document.querySelectorAll('.modal-content');
        modals.forEach(modal => {
            modal.style.backgroundColor = '#ffffff';
            modal.style.color = '#1f2937';
        });
        
        const modalHeaders = document.querySelectorAll('.modal-header');
        modalHeaders.forEach(header => {
            header.style.backgroundColor = '#f9fafb';
            header.style.color = '#1f2937';
        });
        
        const modalBodies = document.querySelectorAll('.modal-body');
        modalBodies.forEach(body => {
            body.style.backgroundColor = '#ffffff';
            body.style.color = '#1f2937';
        });
        
        const modalFooters = document.querySelectorAll('.modal-footer');
        modalFooters.forEach(footer => {
            footer.style.backgroundColor = '#f9fafb';
            footer.style.color = '#1f2937';
        });
        
        // Force all cards to be light theme
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.backgroundColor = '#ffffff';
            card.style.color = '#1f2937';
            card.style.borderColor = '#e5e7eb';
        });
        
        const cardHeaders = document.querySelectorAll('.card-header');
        cardHeaders.forEach(header => {
            header.style.backgroundColor = '#f9fafb';
            header.style.color = '#1f2937';
        });
        
        // Force all form elements to be light theme
        const formLabels = document.querySelectorAll('.form-label');
        formLabels.forEach(label => {
            label.style.color = '#374151';
        });
        
        const formControls = document.querySelectorAll('.form-control, .form-select');
        formControls.forEach(control => {
            control.style.backgroundColor = '#ffffff';
            control.style.borderColor = '#d1d5db';
            control.style.color = '#1f2937';
        });
        
        const formCheckLabels = document.querySelectorAll('.form-check-label');
        formCheckLabels.forEach(label => {
            label.style.color = '#374151';
        });
        
        console.log('Applied universal readability fixes to all elements');
    }

    // Apply fixes on page load
    document.addEventListener('DOMContentLoaded', function() {
        applyUniversalReadabilityFix();
        
        // Apply fixes when modals are shown
        document.addEventListener('shown.bs.modal', function() {
            setTimeout(applyUniversalReadabilityFix, 100);
        });
        
        // Apply fixes when content changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    setTimeout(applyUniversalReadabilityFix, 100);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });

    // Force light theme function (for accessibility)
    window.forceLightTheme = function() {
        document.body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
        if (themeIcon) {
            themeIcon.className = 'fas fa-sun';
        }
        applyUniversalReadabilityFix();
        console.log('Forced light theme for better readability');
    };

    // Auto-detect and fix readability issues
    function checkReadability() {
        const body = document.body;
        if (body.classList.contains('dark-theme')) {
            // Check if text is readable
            const testElement = document.createElement('div');
            testElement.style.position = 'absolute';
            testElement.style.left = '-9999px';
            testElement.style.color = 'inherit';
            testElement.style.backgroundColor = 'inherit';
            testElement.textContent = 'Test';
            body.appendChild(testElement);
            
            const computedStyle = window.getComputedStyle(testElement);
            const textColor = computedStyle.color;
            const bgColor = computedStyle.backgroundColor;
            
            body.removeChild(testElement);
            
            // If colors are too similar, force light theme
            if (textColor === bgColor || textColor === 'rgb(0, 0, 0)' || bgColor === 'rgb(0, 0, 0)') {
                console.warn('Detected readability issues, switching to light theme');
                window.forceLightTheme();
            }
        }
    }

    // Run readability check after page load
    setTimeout(checkReadability, 1000);

    // Print functionality
    window.printPage = function() {
        window.print();
    };

    // Export functionality placeholder
    window.exportData = function(format) {
        console.log('Exporting data in', format, 'format');
        // Implement export functionality here
    };

    // Notification system
    window.showNotification = function(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }, duration);
    };

    console.log('ProjectManager Pro initialized successfully!');
});
