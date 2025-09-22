// Home Page Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Home page specific functionality
    
    // Counter animation for stats
    function animateHomeCounters() {
        const counters = document.querySelectorAll('.home-stat-box h3');
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
    const statsSection = document.querySelector('.home-stat-box');
    if (statsSection) {
        const statsObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateHomeCounters();
                    statsObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        statsObserver.observe(statsSection);
    }

    // Enhanced hover effects for feature boxes
    const featureBoxes = document.querySelectorAll('.home-feature-box');
    featureBoxes.forEach(box => {
        box.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.02)';
        });
        
        box.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        });
    }

    // Smooth scroll for anchor links on home page
    const homeLinks = document.querySelectorAll('a[href^="#"]');
    homeLinks.forEach(link => {
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

    // Add animation classes when elements come into view
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

    // Observe home page elements
    document.querySelectorAll('.home-feature-box, .home-stat-box').forEach(el => {
        observer.observe(el);
    });

    // Hero section typing effect (optional)
    function typeWriter(element, text, speed = 100) {
        let i = 0;
        element.innerHTML = '';
        
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }

    // Initialize typing effect for hero title (if desired)
    const heroTitle = document.querySelector('.hero-content h1');
    if (heroTitle && window.innerWidth > 768) {
        const originalText = heroTitle.textContent;
        // Uncomment the line below to enable typing effect
        // typeWriter(heroTitle, originalText, 50);
    }

    // Add fade-in animation to pricing overview cards
    const pricingCards = document.querySelectorAll('.pricing-card-overview');
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

    console.log('Home page JavaScript initialized successfully!');
});
