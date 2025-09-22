// Subscription Analytics Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Animate counters
    function animateCounters() {
        const counters = document.querySelectorAll('.stats-number, .revenue-amount, .growth-number');
        
        counters.forEach(counter => {
            const target = parseFloat(counter.textContent.replace(/[^\d.]/g, ''));
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
                if (originalText.includes('$')) {
                    counter.textContent = '$' + Math.floor(current).toLocaleString();
                } else if (originalText.includes('%')) {
                    counter.textContent = Math.floor(current) + '%';
                } else {
                    counter.textContent = Math.floor(current).toLocaleString();
                }
            }, 16);
        });
    }

    // Trigger counter animation when page loads
    setTimeout(animateCounters, 500);

    // Add hover effects to cards
    const cards = document.querySelectorAll('.stats-card, .growth-card, .conversion-card, .revenue-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
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

    // Add animation to plan stats
    const planItems = document.querySelectorAll('.plan-stat-item');
    planItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, index * 100);
    });

    // Animate progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach((bar, index) => {
        const width = bar.getAttribute('data-width');
        const total = bar.getAttribute('data-total');
        const percentage = total > 0 ? (width / total) * 100 : 0;
        
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 0.8s ease';
            bar.style.width = percentage + '%';
        }, index * 200);
    });

    // Add tooltips to elements
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Export analytics function
    window.exportAnalytics = function() {
        const data = {
            monthly_revenue: document.querySelector('.revenue-card.monthly .revenue-amount').textContent,
            annual_revenue: document.querySelector('.revenue-card.annual .revenue-amount').textContent,
            total_subscriptions: document.querySelector('.stats-card:nth-child(1) .stats-number').textContent,
            active_subscriptions: document.querySelector('.stats-card:nth-child(2) .stats-number').textContent,
            trial_subscriptions: document.querySelector('.stats-card:nth-child(3) .stats-number').textContent,
            expired_subscriptions: document.querySelector('.stats-card:nth-child(4) .stats-number').textContent,
            export_date: new Date().toISOString()
        };

        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `subscription_analytics_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        // Show success message
        showNotification('Analytics data exported successfully!', 'success');
    };

    // Notification function
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
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

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + E to export
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            exportAnalytics();
        }
        
        // Ctrl/Cmd + R to refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            window.location.reload();
        }
    });

    // Add auto-refresh functionality
    let autoRefreshInterval;
    
    function startAutoRefresh() {
        autoRefreshInterval = setInterval(() => {
            // Only refresh if no user interaction in last 60 seconds
            if (Date.now() - lastUserInteraction > 60000) {
                window.location.reload();
            }
        }, 300000); // Refresh every 5 minutes
    }
    
    function stopAutoRefresh() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
    }
    
    let lastUserInteraction = Date.now();
    
    // Track user interaction
    document.addEventListener('click', () => {
        lastUserInteraction = Date.now();
    });
    
    document.addEventListener('keydown', () => {
        lastUserInteraction = Date.now();
    });
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Stop auto-refresh when page becomes hidden
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            startAutoRefresh();
        }
    });

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
        
        .stats-card,
        .growth-card,
        .conversion-card,
        .revenue-card {
            transition: all 0.3s ease;
        }
        
        .plan-stat-item {
            transition: all 0.3s ease;
        }
        
        .btn {
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-1px);
        }
        
        .progress-bar {
            transition: width 0.8s ease;
        }
        
        .conversion-circle {
            transition: all 0.3s ease;
        }
        
        .conversion-circle:hover {
            transform: scale(1.1);
        }
        
        .plan-icon {
            transition: all 0.3s ease;
        }
        
        .plan-icon:hover {
            transform: scale(1.1);
        }
    `;
    document.head.appendChild(style);

    console.log('Subscription analytics page JavaScript initialized successfully!');
});
