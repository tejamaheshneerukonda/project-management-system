// Employee Dashboard JavaScript Functionality

// Time Tracking Functions
let employeeTimerInterval;
let startTime;
let isRunning = false;

/**
 * Start the time tracking timer
 */
function startTimeTracking() {
    if (!isRunning) {
        startTime = new Date();
        isRunning = true;
        
        // Hide/show buttons
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'inline-block';
        document.getElementById('pauseBtn').style.display = 'inline-block';
        
        // Start timer interval
        employeeTimerInterval = setInterval(updateTimer, 1000);
    }
}

/**
 * Stop the time tracking timer
 */
function stopTimeTracking() {
    if (isRunning) {
        clearInterval(employeeTimerInterval);
        isRunning = false;
        
        // Hide/show buttons
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('stopBtn').style.display = 'none';
        document.getElementById('pauseBtn').style.display = 'none';
        
        // Auto-fill timesheet form
        const now = new Date();
        const duration = now - startTime;
        const hours = Math.floor(duration / (1000 * 60 * 60));
        const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
        
        // Create a hidden form to submit the time entry
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/employee/timesheet/';
        
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
        
        const dateInput = document.createElement('input');
        dateInput.type = 'hidden';
        dateInput.name = 'entry_date';
        dateInput.value = now.toISOString().split('T')[0];
        form.appendChild(dateInput);
        
        const startTimeInput = document.createElement('input');
        startTimeInput.type = 'hidden';
        startTimeInput.name = 'start_time';
        startTimeInput.value = startTime.toTimeString().slice(0, 5);
        form.appendChild(startTimeInput);
        
        const endTimeInput = document.createElement('input');
        endTimeInput.type = 'hidden';
        endTimeInput.name = 'end_time';
        endTimeInput.value = now.toTimeString().slice(0, 5);
        form.appendChild(endTimeInput);
        
        const descriptionInput = document.createElement('input');
        descriptionInput.type = 'hidden';
        descriptionInput.name = 'task_description';
        descriptionInput.value = 'Timer session - ' + hours + 'h ' + minutes + 'm';
        form.appendChild(descriptionInput);
        
        document.body.appendChild(form);
        form.submit();
    }
}

/**
 * Pause the time tracking timer
 */
function pauseTimeTracking() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
        
        document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-play me-2"></i>Resume';
        document.getElementById('pauseBtn').onclick = resumeTimeTracking;
    }
}

/**
 * Resume the time tracking timer
 */
function resumeTimeTracking() {
    if (!isRunning) {
        startTime = new Date(Date.now() - (new Date() - startTime));
        isRunning = true;
        
        document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-pause me-2"></i>Pause';
        document.getElementById('pauseBtn').onclick = pauseTimeTracking;
        
        timerInterval = setInterval(updateTimer, 1000);
    }
}

/**
 * Update the timer display
 */
function updateTimer() {
    if (isRunning) {
        const now = new Date();
        const duration = now - startTime;
        
        const hours = Math.floor(duration / (1000 * 60 * 60));
        const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((duration % (1000 * 60)) / 1000);
        
        document.getElementById('currentTimer').textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

/**
 * Initialize the employee dashboard
 */
function initEmployeeDashboard() {
    // Add event listeners for quick action buttons
    const quickActionButtons = document.querySelectorAll('.quick-action-btn');
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add animation effect
            this.classList.add('btn-clicked');
            setTimeout(() => {
                this.classList.remove('btn-clicked');
            }, 300);
        });
    });
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const href = this.getAttribute('href');
            // Only scroll if href is not just '#' and is a valid selector
            if (href !== '#' && document.querySelector(href)) {
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Initialize notification dropdown
 */
function initNotifications() {
    const notificationDropdown = document.getElementById('notificationDropdown');
    if (notificationDropdown) {
        notificationDropdown.addEventListener('show.bs.dropdown', function() {
            // Mark notifications as read when dropdown is opened
            const unreadNotifications = document.querySelectorAll('.notification-item.unread');
            unreadNotifications.forEach(notification => {
                notification.classList.remove('unread');
                // Here you would typically make an AJAX request to mark notifications as read
                markNotificationAsRead(notification.dataset.notificationId);
            });
        });
        
        // Fetch new notifications when page loads
        fetchNewNotifications();
        
        // Check for new notifications every 30 seconds
        setInterval(checkForNewNotifications, 30000);
    }
}

/**
 * Mark a notification as read
 */
function markNotificationAsRead(notificationId) {
    if (!notificationId) return;
    
    fetch('/api/notifications/' + notificationId + '/read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            console.error('Failed to mark notification as read');
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

/**
 * Fetch new notifications
 */
function fetchNewNotifications() {
    fetch('/api/notifications/unread/', {
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.unread_count > 0) {
            updateUnreadCount(data.unread_count);
            
            // Add new notifications to the dropdown
            if (data.notifications && data.notifications.length > 0) {
                appendNewNotifications(data.notifications);
            }
        }
    })
    .catch(error => {
        console.error('Error fetching notifications:', error);
    });
}

/**
 * Check for new notifications periodically
 */
function checkForNewNotifications() {
    fetch('/api/notifications/check_new/', {
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.has_new && data.unread_count > 0) {
            updateUnreadCount(data.unread_count);
            
            // Show a toast notification
            showNotificationToast('You have new notifications!');
            
            // Play a subtle notification sound if enabled
            playNotificationSound();
        }
    })
    .catch(error => {
        console.error('Error checking for new notifications:', error);
    });
}

/**
 * Update the unread notification count badge
 */
function updateUnreadCount(count) {
    const unreadBadge = document.getElementById('notificationCount');
    if (unreadBadge) {
        if (count > 0) {
            unreadBadge.textContent = count;
            unreadBadge.classList.remove('d-none');
        } else {
            unreadBadge.classList.add('d-none');
        }
    }
}

/**
 * Append new notifications to the dropdown
 */
function appendNewNotifications(notifications) {
    const notificationList = document.getElementById('notificationList');
    if (!notificationList) return;
    
    notifications.forEach(notification => {
        // Create notification element
        const notificationItem = document.createElement('div');
        notificationItem.className = 'notification-item unread';
        notificationItem.dataset.notificationId = notification.id;
        
        // Format notification content based on type
        let iconClass = 'fas fa-bell';
        if (notification.type === 'task') {
            iconClass = 'fas fa-tasks';
        } else if (notification.type === 'meeting') {
            iconClass = 'fas fa-calendar-alt';
        } else if (notification.type === 'project') {
            iconClass = 'fas fa-project-diagram';
        }
        
        notificationItem.innerHTML = `
            <div class="notification-icon">
                <i class="${iconClass}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-time">${formatNotificationTime(notification.created_at)}</div>
            </div>
        `;
        
        // Insert before the "View All" link
        const viewAllLink = notificationList.querySelector('.view-all-link');
        if (viewAllLink) {
            notificationList.insertBefore(notificationItem, viewAllLink);
        } else {
            notificationList.appendChild(notificationItem);
        }
        
        // Add click handler
        notificationItem.addEventListener('click', function() {
            if (notification.url) {
                window.location.href = notification.url;
            }
        });
    });
}

/**
 * Format notification timestamp
 */
function formatNotificationTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) {
        return diffMins + ' min' + (diffMins !== 1 ? 's' : '') + ' ago';
    } else if (diffHours < 24) {
        return diffHours + ' hour' + (diffHours !== 1 ? 's' : '') + ' ago';
    } else if (diffDays < 7) {
        return diffDays + ' day' + (diffDays !== 1 ? 's' : '') + ' ago';
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Show a toast notification
 */
function showNotificationToast(message) {
    // Check if toast container exists, create if not
    let toastContainer = document.getElementById('notificationToastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'notificationToastContainer';
        toastContainer.className = 'position-fixed bottom-0 right-0 p-4 z-50';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = 'toast fade show bg-primary text-white mb-2';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-bell mr-2"></i>
            <strong class="mr-auto">Notification</strong>
            <button type="button" class="ml-2 mb-1 close text-white" data-dismiss="toast" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toastContainer.contains(toast)) {
                toastContainer.removeChild(toast);
            }
        }, 300);
    }, 5000);
    
    // Add close button event listener
    const closeBtn = toast.querySelector('.close');
    closeBtn.addEventListener('click', function() {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toastContainer.contains(toast)) {
                toastContainer.removeChild(toast);
            }
        }, 300);
    });
}

/**
 * Play notification sound if enabled in preferences
 */
function playNotificationSound() {
    // Check if browser notifications are enabled
    if (Notification.permission === 'granted') {
        try {
            // Create an audio element and play
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => {
                // Handle autoplay policy restrictions
                console.log('Auto-play prevented:', e);
            });
        } catch (e) {
            console.error('Error playing notification sound:', e);
        }
    }
}

/**
 * Initialize notification preferences management
 */
function initNotificationPreferences() {
    // Check if we're on the preferences page
    const preferencesForm = document.getElementById('preferencesForm');
    if (preferencesForm) {
        preferencesForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Collect form data
            const formData = new FormData(this);
            const preferences = {};
            formData.forEach((value, key) => {
                preferences[key] = value === 'on' ? true : value;
            });
            
            // Submit form data via AJAX
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(preferences)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotificationToast('Notification preferences updated successfully!');
                } else {
                    showNotificationToast('Failed to update preferences: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error submitting preferences:', error);
                showNotificationToast('Error updating preferences');
            });
        });
        
        // Add reset to defaults functionality
        const resetButton = document.querySelector('button[onclick="resetToDefaults()"]');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                if (confirm('Are you sure you want to reset all notification preferences to defaults?')) {
                    fetch('/api/notification_preferences/reset/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Reset form checkboxes
                            const checkboxes = preferencesForm.querySelectorAll('input[type="checkbox"]');
                            checkboxes.forEach(checkbox => {
                                checkbox.checked = data.defaults[checkbox.name] || false;
                            });
                            showNotificationToast('Preferences reset to defaults!');
                        }
                    })
                    .catch(error => {
                        console.error('Error resetting preferences:', error);
                        showNotificationToast('Error resetting preferences');
                    });
                }
            });
        }
        
        // Add browser notification permission request
        const browserEnabled = document.getElementById('browser_enabled');
        if (browserEnabled) {
            browserEnabled.addEventListener('change', function() {
                if (this.checked && Notification.permission === 'default') {
                    Notification.requestPermission().then(permission => {
                        if (permission !== 'granted') {
                            this.checked = false;
                            showNotificationToast('Browser notifications require permission');
                        }
                    });
                }
            });
        }
    }
}

/**
 * Helper function to get CSRF token
 */
function getCSRFToken() {
    const element = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return element ? element.value : '';
}

/**
 * Initialize dashboard charts if Chart.js is available
 */
function initDashboardCharts() {
    if (typeof Chart !== 'undefined') {
        // Example of a productivity chart
        const productivityCtx = document.getElementById('productivityChart');
        if (productivityCtx) {
            new Chart(productivityCtx, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Hours Worked',
                        data: [7.5, 8.2, 6.8, 9.0, 7.2, 3.5, 0],
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Hours'
                            }
                        }
                    }
                }
            });
        }
        
        // Example of task completion chart
        const taskCompletionCtx = document.getElementById('taskCompletionChart');
        if (taskCompletionCtx) {
            new Chart(taskCompletionCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
                    datasets: [{
                        label: 'Tasks Completed',
                        data: [12, 19, 15, 22, 18],
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Tasks'
                            }
                        }
                    }
                }
            });
        }
        
        // Example of goal progress chart
        const goalProgressCtx = document.getElementById('goalProgressChart');
        if (goalProgressCtx) {
            new Chart(goalProgressCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'In Progress'],
                    datasets: [{
                        data: [65, 35],
                        backgroundColor: [
                            'rgba(153, 102, 255, 0.8)',
                            'rgba(200, 200, 200, 0.8)'
                        ],
                        borderColor: [
                            'rgba(153, 102, 255, 1)',
                            'rgba(200, 200, 200, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
}

/**
 * Initialize all components when document is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initEmployeeDashboard();
    
    // Initialize notifications
    initNotifications();
    
    // Initialize notification preferences
    initNotificationPreferences();
    
    // Initialize charts
    initDashboardCharts();
});