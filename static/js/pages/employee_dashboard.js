/**
 * Employee Dashboard JavaScript
 * Handles dashboard functionality, time tracking, and real-time updates
 */

// Global variables
let timerInterval;
let startTime;
let isRunning = false;
let isPaused = false;
let pausedTime = 0;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Employee Dashboard loaded');
    initializeDashboard();
    initializeTimeTracking();
    initializeRealTimeUpdates();
    addAnimationClasses();
});

/**
 * Initialize dashboard components
 */
function initializeDashboard() {
    // Add loading states to cards
    const cards = document.querySelectorAll('.dashboard-card, .stat-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize progress bars animation
    animateProgressBars();
    
    // Initialize task status indicators
    initializeTaskStatusIndicators();
}

/**
 * Initialize time tracking functionality
 */
function initializeTimeTracking() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    
    if (startBtn) {
        startBtn.addEventListener('click', startTimeTracking);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopTimeTracking);
    }
    
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pauseTimeTracking);
    }
    
    // Load saved timer state from localStorage
    loadTimerState();
}

/**
 * Start time tracking
 */
function startTimeTracking() {
    if (!isRunning) {
        startTime = new Date();
        isRunning = true;
        isPaused = false;
        pausedTime = 0;
        
        // Update button states
        updateTimerButtons();
        
        // Start timer interval
        timerInterval = setInterval(updateTimer, 1000);
        
        // Save state to localStorage
        saveTimerState();
        
        // Show success message
        showToast('Timer started!', 'success');
        
        console.log('Time tracking started');
    }
}

/**
 * Stop time tracking
 */
function stopTimeTracking() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
        isPaused = false;
        
        // Calculate total time
        const totalTime = new Date() - startTime - pausedTime;
        const hours = Math.floor(totalTime / (1000 * 60 * 60));
        const minutes = Math.floor((totalTime % (1000 * 60 * 60)) / (1000 * 60));
        
        // Update button states
        updateTimerButtons();
        
        // Reset timer display
        document.getElementById('currentTimer').textContent = '00:00:00';
        
        // Clear saved state
        clearTimerState();
        
        // Show completion message
        showToast(`Session completed: ${hours}h ${minutes}m`, 'info');
        
        // Update today's hours (simulate)
        updateTodayHours(totalTime);
        
        console.log('Time tracking stopped');
    }
}

/**
 * Pause/Resume time tracking
 */
function pauseTimeTracking() {
    if (isRunning && !isPaused) {
        // Pause
        clearInterval(timerInterval);
        isPaused = true;
        pausedTime += new Date() - startTime;
        
        document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-play me-2"></i>Resume';
        document.getElementById('pauseBtn').onclick = resumeTimeTracking;
        
        showToast('Timer paused', 'warning');
        console.log('Time tracking paused');
    }
}

/**
 * Resume time tracking
 */
function resumeTimeTracking() {
    if (isRunning && isPaused) {
        // Resume
        startTime = new Date();
        isPaused = false;
        
        timerInterval = setInterval(updateTimer, 1000);
        
        document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-pause me-2"></i>Pause';
        document.getElementById('pauseBtn').onclick = pauseTimeTracking;
        
        showToast('Timer resumed', 'success');
        console.log('Time tracking resumed');
    }
}

/**
 * Update timer display
 */
function updateTimer() {
    if (isRunning && !isPaused) {
        const now = new Date();
        const elapsed = now - startTime - pausedTime;
        
        const hours = Math.floor(elapsed / (1000 * 60 * 60));
        const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
        
        const timeString = 
            String(hours).padStart(2, '0') + ':' + 
            String(minutes).padStart(2, '0') + ':' + 
            String(seconds).padStart(2, '0');
        
        document.getElementById('currentTimer').textContent = timeString;
    }
}

/**
 * Update timer button states
 */
function updateTimerButtons() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    
    if (isRunning) {
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'inline-block';
    } else {
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        pauseBtn.style.display = 'none';
    }
}

/**
 * Update today's hours display
 */
function updateTodayHours(additionalTime) {
    const todayHoursElement = document.getElementById('todayHours');
    if (todayHoursElement) {
        const currentHours = parseFloat(todayHoursElement.textContent) || 0;
        const additionalHours = additionalTime / (1000 * 60 * 60);
        const newTotal = currentHours + additionalHours;
        
        todayHoursElement.textContent = newTotal.toFixed(1);
        
        // Add animation effect
        todayHoursElement.classList.add('text-gradient');
        setTimeout(() => {
            todayHoursElement.classList.remove('text-gradient');
        }, 2000);
    }
}

/**
 * Initialize real-time updates
 */
function initializeRealTimeUpdates() {
    // Check for new notifications every 30 seconds
    setInterval(checkForNotifications, 30000);
    
    // Update dashboard data every 5 minutes
    setInterval(updateDashboardData, 300000);
    
    // Initialize WebSocket connection for real-time updates
    initializeWebSocket();
}

/**
 * Initialize WebSocket connection
 */
function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/employee-dashboard/`;
    
    try {
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = function(event) {
            console.log('WebSocket connected for dashboard updates');
        };
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        socket.onclose = function(event) {
            console.log('WebSocket disconnected, attempting to reconnect...');
            setTimeout(initializeWebSocket, 5000);
        };
        
        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
    } catch (error) {
        console.log('WebSocket not available, using polling fallback');
        // Fallback to polling if WebSocket fails
        setInterval(pollForUpdates, 10000);
    }
}

/**
 * Handle WebSocket messages
 */
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'task_update':
            updateTaskDisplay(data.task);
            break;
        case 'notification':
            showNotification(data.notification);
            break;
        case 'timer_update':
            updateTimerDisplay(data.timer);
            break;
        default:
            console.log('Unknown WebSocket message type:', data.type);
    }
}

/**
 * Poll for updates (fallback)
 */
function pollForUpdates() {
    fetch('/api/dashboard/updates/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.updated) {
            updateDashboardData();
        }
    })
    .catch(error => {
        console.error('Error polling for updates:', error);
    });
}

/**
 * Update dashboard data
 */
function updateDashboardData() {
    fetch('/api/dashboard/data/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        updateTaskCounts(data.tasks);
        updateProjectCounts(data.projects);
        updateTimeTracking(data.time_tracking);
    })
    .catch(error => {
        console.error('Error updating dashboard data:', error);
    });
}

/**
 * Update task counts
 */
function updateTaskCounts(taskData) {
    const myTasksElement = document.querySelector('.h5.mb-0.font-weight-bold.text-gray-800');
    if (myTasksElement && taskData) {
        myTasksElement.textContent = taskData.total || 0;
        
        // Update completed and in-progress counts
        const completedSpan = document.querySelector('.text-success');
        const inProgressSpan = document.querySelector('.text-warning');
        
        if (completedSpan) completedSpan.textContent = taskData.completed || 0;
        if (inProgressSpan) inProgressSpan.textContent = taskData.in_progress || 0;
    }
}

/**
 * Update project counts
 */
function updateProjectCounts(projectData) {
    const activeProjectsElement = document.querySelector('.col-xl-3.col-md-6:nth-child(2) .h5.mb-0.font-weight-bold.text-gray-800');
    if (activeProjectsElement && projectData) {
        activeProjectsElement.textContent = projectData.active || 0;
    }
}

/**
 * Update time tracking data
 */
function updateTimeTracking(timeData) {
    if (timeData) {
        const todayHoursElement = document.getElementById('todayHours');
        const weekHoursElement = document.getElementById('weekHours');
        const monthHoursElement = document.getElementById('monthHours');
        
        if (todayHoursElement) todayHoursElement.textContent = timeData.today || 0;
        if (weekHoursElement) weekHoursElement.textContent = timeData.week || 0;
        if (monthHoursElement) monthHoursElement.textContent = timeData.month || 0;
    }
}

/**
 * Animate progress bars
 */
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar-custom');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
}

/**
 * Initialize task status indicators
 */
function initializeTaskStatusIndicators() {
    const statusElements = document.querySelectorAll('.task-status');
    statusElements.forEach(element => {
        const status = element.textContent.toLowerCase().trim();
        element.classList.add(status);
    });
}

/**
 * Add animation classes to elements
 */
function addAnimationClasses() {
    // Add staggered animations to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add slide animations to lists
    const listItems = document.querySelectorAll('.task-list-item, .announcement-item, .goal-item');
    listItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.05}s`;
        item.classList.add('slide-in-left');
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Create toast container
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Save timer state to localStorage
 */
function saveTimerState() {
    const state = {
        isRunning: isRunning,
        startTime: startTime,
        isPaused: isPaused,
        pausedTime: pausedTime
    };
    localStorage.setItem('timerState', JSON.stringify(state));
}

/**
 * Load timer state from localStorage
 */
function loadTimerState() {
    const savedState = localStorage.getItem('timerState');
    if (savedState) {
        const state = JSON.parse(savedState);
        if (state.isRunning && !state.isPaused) {
            // Resume timer if it was running
            startTime = new Date(state.startTime);
            isRunning = true;
            isPaused = false;
            pausedTime = state.pausedTime;
            
            updateTimerButtons();
            timerInterval = setInterval(updateTimer, 1000);
        }
    }
}

/**
 * Clear timer state from localStorage
 */
function clearTimerState() {
    localStorage.removeItem('timerState');
}

/**
 * Check for notifications
 */
function checkForNotifications() {
    fetch('/api/notifications/unread/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.notifications && data.notifications.length > 0) {
            data.notifications.forEach(notification => {
                showNotification(notification);
            });
        }
    })
    .catch(error => {
        console.error('Error checking notifications:', error);
    });
}

/**
 * Show notification
 */
function showNotification(notification) {
    showToast(notification.message, notification.type || 'info');
}

// Export functions for global access
window.startTimeTracking = startTimeTracking;
window.stopTimeTracking = stopTimeTracking;
window.pauseTimeTracking = pauseTimeTracking;
window.resumeTimeTracking = resumeTimeTracking;
