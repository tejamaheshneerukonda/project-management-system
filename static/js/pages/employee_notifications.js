/**
 * Employee Notifications JavaScript
 * Handles notification management and auto-refresh functionality for employees
 */

// Notification Management Functions
function markAsRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.classList.remove('unread');
                notificationElement.classList.add('read');
            }
            updateUnreadCount();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function markAllAsRead() {
    fetch('/api/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const unreadNotifications = document.querySelectorAll('.notification-item.unread');
            unreadNotifications.forEach(notification => {
                notification.classList.remove('unread');
                notification.classList.add('read');
            });
            updateUnreadCount();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function deleteNotification(notificationId) {
    if (confirm('Are you sure you want to delete this notification?')) {
        fetch(`/api/notifications/${notificationId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
                if (notificationElement) {
                    notificationElement.remove();
                }
                updateUnreadCount();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function filterNotifications(filter) {
    const notifications = document.querySelectorAll('.notification-item');
    
    notifications.forEach(notification => {
        if (filter === 'all') {
            notification.style.display = 'block';
        } else if (filter === 'unread') {
            notification.style.display = notification.classList.contains('unread') ? 'block' : 'none';
        } else if (filter === 'read') {
            notification.style.display = notification.classList.contains('read') ? 'block' : 'none';
        } else {
            // Filter by type
            const type = notification.dataset.type;
            notification.style.display = type === filter ? 'block' : 'none';
        }
    });
}

function refreshNotifications() {
    location.reload();
}

function updateUnreadCount() {
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;
    const countElement = document.getElementById('unreadCount');
    if (countElement) {
        countElement.textContent = unreadCount;
        countElement.style.display = unreadCount > 0 ? 'inline' : 'none';
    }
}

function startAutoRefresh() {
    let autoRefreshInterval;
    
    function refresh() {
        if (document.getElementById('autoRefresh').checked) {
            autoRefreshInterval = setInterval(refreshNotifications, 30000); // 30 seconds
        } else {
            clearInterval(autoRefreshInterval);
        }
    }
    
    const autoRefreshCheckbox = document.getElementById('autoRefresh');
    if (autoRefreshCheckbox) {
        autoRefreshCheckbox.addEventListener('change', refresh);
        refresh();
    }
}

function viewNotificationDetails(notificationId) {
    console.log('Viewing notification details:', notificationId);
    // This would open a notification details modal
}

function archiveNotification(notificationId) {
    fetch(`/api/notifications/${notificationId}/archive/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.remove();
            }
            updateUnreadCount();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Initialize notification management functionality
function initNotificationManagement() {
    console.log('Notification management initialized');
    
    // Auto-refresh functionality
    startAutoRefresh();
    
    // Filter functionality
    const filterRadios = document.querySelectorAll('input[name="notificationFilter"]');
    filterRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            filterNotifications(this.id);
        });
    });
    
    // Update unread count
    updateUnreadCount();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initNotificationManagement();
});

// Export functions for global access
window.markAsRead = markAsRead;
window.markAllAsRead = markAllAsRead;
window.deleteNotification = deleteNotification;
window.filterNotifications = filterNotifications;
window.refreshNotifications = refreshNotifications;
window.viewNotificationDetails = viewNotificationDetails;
window.archiveNotification = archiveNotification;
