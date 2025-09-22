/**
 * WebSocket Manager for real-time updates
 * 
 * This module handles WebSocket connections for real-time updates in the application.
 * It provides a central interface for establishing and managing WebSocket connections
 * for different features like notifications, project updates, and dashboard metrics.
 */

class WebSocketManager {
    /**
     * Initialize the WebSocket manager
     */
    constructor() {
        this.connections = {};
        this.reconnectTimeouts = {};
        this.maxReconnectDelay = 30000; // Maximum reconnect delay in ms (30 seconds)
        this.baseReconnectDelay = 1000; // Base reconnect delay in ms (1 second)
    }

    /**
     * Get WebSocket URL for the given path
     * @param {string} path - The WebSocket path
     * @returns {string} The complete WebSocket URL
     */
    getWebSocketUrl(path) {
        // Determine if we're using secure WebSockets based on the current protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}${path}`;
    }

    /**
     * Connect to a WebSocket endpoint
     * @param {string} name - Unique name for this connection
     * @param {string} path - The WebSocket path
     * @param {Object} handlers - Event handlers for the connection
     * @returns {WebSocket} The WebSocket connection
     */
    connect(name, path, handlers = {}) {
        if (this.connections[name]) {
            console.log(`WebSocket connection '${name}' already exists`);
            return this.connections[name];
        }

        const url = this.getWebSocketUrl(path);
        const ws = new WebSocket(url);
        let reconnectAttempt = 0;

        // Setup event handlers
        ws.onopen = (event) => {
            console.log(`WebSocket connection '${name}' established`);
            reconnectAttempt = 0; // Reset reconnect attempts on successful connection
            if (handlers.onOpen) handlers.onOpen(event);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (handlers.onMessage) handlers.onMessage(data);
                
                // Handle specific message types
                if (data.type && handlers[`on${this.capitalizeFirstLetter(data.type)}`]) {
                    handlers[`on${this.capitalizeFirstLetter(data.type)}`](data);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.onerror = (event) => {
            console.error(`WebSocket '${name}' error:`, event);
            if (handlers.onError) handlers.onError(event);
        };

        ws.onclose = (event) => {
            console.log(`WebSocket '${name}' connection closed`);
            
            // Remove from active connections
            delete this.connections[name];
            
            if (handlers.onClose) handlers.onClose(event);
            
            // Attempt to reconnect with exponential backoff
            if (!event.wasClean) {
                const delay = Math.min(
                    this.baseReconnectDelay * Math.pow(2, reconnectAttempt),
                    this.maxReconnectDelay
                );
                
                console.log(`Attempting to reconnect '${name}' in ${delay}ms`);
                
                this.reconnectTimeouts[name] = setTimeout(() => {
                    reconnectAttempt++;
                    console.log(`Reconnecting '${name}', attempt ${reconnectAttempt}`);
                    this.connect(name, path, handlers);
                }, delay);
            }
        };

        // Store the connection
        this.connections[name] = ws;
        return ws;
    }

    /**
     * Disconnect a WebSocket connection
     * @param {string} name - The name of the connection to disconnect
     */
    disconnect(name) {
        if (this.connections[name]) {
            this.connections[name].close();
            delete this.connections[name];
        }
        
        // Clear any pending reconnect attempts
        if (this.reconnectTimeouts[name]) {
            clearTimeout(this.reconnectTimeouts[name]);
            delete this.reconnectTimeouts[name];
        }
    }

    /**
     * Send data through a WebSocket connection
     * @param {string} name - The name of the connection
     * @param {Object} data - The data to send (will be JSON stringified)
     * @returns {boolean} True if sent successfully, false otherwise
     */
    send(name, data) {
        if (!this.connections[name]) {
            console.error(`WebSocket connection '${name}' not found`);
            return false;
        }

        if (this.connections[name].readyState !== WebSocket.OPEN) {
            console.error(`WebSocket connection '${name}' not open`);
            return false;
        }

        this.connections[name].send(JSON.stringify(data));
        return true;
    }

    /**
     * Capitalize the first letter of a string
     * @param {string} string - The string to capitalize
     * @returns {string} The capitalized string
     */
    capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    /**
     * Initialize notification WebSocket
     * @returns {WebSocket} The notification WebSocket connection
     */
    initNotifications() {
        // Skip WebSocket initialization in development if Redis is not available
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('WebSocket notifications disabled for development');
            return null;
        }
        
        return this.connect('notifications', '/ws/notifications/', {
            onOpen: () => {
                // Request initial unread count
                this.send('notifications', { type: 'fetch_unread_count' });
            },
            onNotification: (data) => {
                // Display a browser notification if supported
                if ('Notification' in window && Notification.permission === 'granted') {
                    const notification = new Notification('New Notification', {
                        body: data.notification.message,
                        icon: document.getElementById('static-url').getAttribute('data-icon-192')
                    });
                    
                    // Close the notification after 5 seconds
                    setTimeout(() => notification.close(), 5000);
                }
                
                // Update UI notification indicator
                this.updateNotificationUI(data.notification);
            },
            onUnreadCount: (data) => {
                // Update the notification badge
                const badge = document.getElementById('notification-badge');
                if (badge) {
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.classList.remove('d-none');
                    } else {
                        badge.classList.add('d-none');
                    }
                }
            },
            onError: (event) => {
                console.error('Notification WebSocket error:', event);
            }
        });
    }

    /**
     * Initialize owner dashboard WebSocket
     * @returns {WebSocket} The owner dashboard WebSocket connection
     */
    initOwnerDashboard() {
        // Skip WebSocket initialization in development if Redis is not available
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('WebSocket owner dashboard disabled for development');
            return null;
        }
        
        return this.connect('ownerDashboard', '/ws/dashboard/owner/', {
            onDashboardUpdate: (data) => {
                this.updateDashboardUI(data.update);
            },
            onSystemAlert: (data) => {
                this.showSystemAlert(data.alert);
            },
            onMetricUpdate: (data) => {
                this.updateMetricUI(data.metric);
            }
        });
    }

    /**
     * Initialize project WebSocket
     * @param {number} projectId - The project ID
     * @returns {WebSocket} The project WebSocket connection
     */
    initProject(projectId) {
        return this.connect(`project_${projectId}`, `/ws/projects/${projectId}/`, {
            onProjectUpdate: (data) => {
                this.updateProjectUI(data.update);
            },
            onTaskUpdate: (data) => {
                this.updateTaskUI(data.update);
            }
        });
    }

    /**
     * Initialize team WebSocket
     * @param {number} teamId - The team ID
     * @returns {WebSocket} The team WebSocket connection
     */
    initTeam(teamId) {
        return this.connect(`team_${teamId}`, `/ws/teams/${teamId}/`, {
            onTeamUpdate: (data) => {
                this.updateTeamUI(data.update);
            }
        });
    }

    /**
     * Update the notification UI with new notification data
     * @param {Object} notification - The notification data
     */
    updateNotificationUI(notification) {
        // Get the notification container
        const container = document.getElementById('notification-container');
        if (!container) return;

        // Create notification element
        const element = document.createElement('div');
        element.className = 'notification-item new-notification';
        element.innerHTML = `
            <div class="notification-header">
                <span class="notification-type">${notification.type}</span>
                <span class="notification-time">${notification.timestamp}</span>
            </div>
            <div class="notification-body">
                ${notification.message}
            </div>
        `;

        // Add to the container at the top
        container.insertBefore(element, container.firstChild);

        // Add animation
        setTimeout(() => element.classList.remove('new-notification'), 100);

        // Update the notification count
        this.send('notifications', { type: 'fetch_unread_count' });
    }

    /**
     * Update the dashboard UI with new data
     * @param {Object} update - The dashboard update data
     */
    updateDashboardUI(update) {
        // Handle different types of dashboard updates
        if (update.type === 'company_metric') {
            // Update company metrics display
            const metricElement = document.getElementById(`metric-${update.metric_id}`);
            if (metricElement) {
                const valueElement = metricElement.querySelector('.metric-value');
                if (valueElement) {
                    valueElement.textContent = update.value;
                }
                
                // Update trend indicator
                const trendElement = metricElement.querySelector('.metric-trend');
                if (trendElement) {
                    trendElement.className = 'metric-trend';
                    if (update.trend > 0) {
                        trendElement.classList.add('trend-up');
                        trendElement.innerHTML = `<i class="fas fa-arrow-up"></i> ${update.trend}%`;
                    } else if (update.trend < 0) {
                        trendElement.classList.add('trend-down');
                        trendElement.innerHTML = `<i class="fas fa-arrow-down"></i> ${Math.abs(update.trend)}%`;
                    } else {
                        trendElement.classList.add('trend-neutral');
                        trendElement.innerHTML = `<i class="fas fa-minus"></i> 0%`;
                    }
                }
            }
        } else if (update.type === 'activity_log') {
            // Update activity log
            const logContainer = document.getElementById('activity-log-container');
            if (logContainer) {
                const logItem = document.createElement('div');
                logItem.className = 'activity-log-item new-log';
                logItem.innerHTML = `
                    <div class="activity-log-time">${update.timestamp}</div>
                    <div class="activity-log-details">
                        <span class="activity-user">${update.user}</span>
                        <span class="activity-action">${update.action}</span>
                        <span class="activity-resource">${update.resource}</span>
                    </div>
                `;
                
                // Add to the container at the top
                logContainer.insertBefore(logItem, logContainer.firstChild);
                
                // Limit the number of log items to avoid excessive DOM size
                const maxItems = 50;
                while (logContainer.children.length > maxItems) {
                    logContainer.removeChild(logContainer.lastChild);
                }
                
                // Add animation
                setTimeout(() => logItem.classList.remove('new-log'), 100);
            }
        }
        // Add more update type handlers as needed
    }

    /**
     * Show a system alert notification
     * @param {Object} alert - The alert data
     */
    showSystemAlert(alert) {
        // Create alert element
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${alert.level} alert-dismissible fade show system-alert`;
        alertElement.innerHTML = `
            <strong>${alert.title}</strong> ${alert.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to the alerts container
        const container = document.getElementById('system-alerts-container');
        if (container) {
            container.appendChild(alertElement);
            
            // Auto dismiss after a delay for non-critical alerts
            if (alert.level !== 'danger') {
                setTimeout(() => {
                    alertElement.classList.remove('show');
                    setTimeout(() => alertElement.remove(), 150);
                }, 5000);
            }
        }
    }

    /**
     * Update metric UI with new data
     * @param {Object} metric - The metric data
     */
    updateMetricUI(metric) {
        // Find the metric chart
        const chartElement = document.getElementById(`chart-${metric.id}`);
        if (!chartElement) return;
        
        // If using Chart.js, update the chart data
        const chartInstance = Chart.getChart(chartElement);
        if (chartInstance) {
            // Update chart data
            if (metric.data_type === 'time_series') {
                // Update time series data
                chartInstance.data.labels = metric.labels;
                chartInstance.data.datasets.forEach((dataset, index) => {
                    if (metric.datasets && metric.datasets[index]) {
                        dataset.data = metric.datasets[index].data;
                    }
                });
            } else if (metric.data_type === 'pie') {
                // Update pie chart data
                chartInstance.data.labels = metric.labels;
                chartInstance.data.datasets[0].data = metric.data;
                if (metric.colors) {
                    chartInstance.data.datasets[0].backgroundColor = metric.colors;
                }
            }
            
            // Update the chart
            chartInstance.update();
        }
    }

    /**
     * Update project UI with new data
     * @param {Object} update - The project update data
     */
    updateProjectUI(update) {
        // Update project details or status
        const projectElement = document.getElementById(`project-${update.id}`);
        if (!projectElement) return;
        
        // Update project name if changed
        if (update.name) {
            const nameElement = projectElement.querySelector('.project-name');
            if (nameElement) nameElement.textContent = update.name;
        }
        
        // Update project status if changed
        if (update.status) {
            const statusElement = projectElement.querySelector('.project-status');
            if (statusElement) {
                statusElement.textContent = update.status;
                
                // Update status class
                statusElement.className = 'project-status';
                statusElement.classList.add(`status-${update.status.toLowerCase()}`);
            }
        }
        
        // Update progress if changed
        if (update.progress !== undefined) {
            const progressBar = projectElement.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${update.progress}%`;
                progressBar.setAttribute('aria-valuenow', update.progress);
                progressBar.textContent = `${update.progress}%`;
            }
        }
    }

    /**
     * Update task UI with new data
     * @param {Object} update - The task update data
     */
    updateTaskUI(update) {
        // Update task details or status
        const taskElement = document.getElementById(`task-${update.id}`);
        if (!taskElement) return;
        
        // Update task title if changed
        if (update.title) {
            const titleElement = taskElement.querySelector('.task-title');
            if (titleElement) titleElement.textContent = update.title;
        }
        
        // Update task status if changed
        if (update.status) {
            const statusElement = taskElement.querySelector('.task-status');
            if (statusElement) {
                statusElement.textContent = update.status;
                
                // Update status class
                statusElement.className = 'task-status';
                statusElement.classList.add(`status-${update.status.toLowerCase()}`);
            }
        }
        
        // Update assignee if changed
        if (update.assignee) {
            const assigneeElement = taskElement.querySelector('.task-assignee');
            if (assigneeElement) assigneeElement.textContent = update.assignee;
        }
    }

    /**
     * Update team UI with new data
     * @param {Object} update - The team update data
     */
    updateTeamUI(update) {
        // Update team details
        const teamElement = document.getElementById(`team-${update.id}`);
        if (!teamElement) return;
        
        // Update team name if changed
        if (update.name) {
            const nameElement = teamElement.querySelector('.team-name');
            if (nameElement) nameElement.textContent = update.name;
        }
        
        // Update member count if changed
        if (update.member_count !== undefined) {
            const countElement = teamElement.querySelector('.member-count');
            if (countElement) countElement.textContent = update.member_count;
        }
        
        // Update members list if provided
        if (update.members) {
            const membersContainer = teamElement.querySelector('.team-members');
            if (membersContainer) {
                // Clear existing members
                membersContainer.innerHTML = '';
                
                // Add updated members
                update.members.forEach(member => {
                    const memberElement = document.createElement('div');
                    memberElement.className = 'team-member';
                    memberElement.innerHTML = `
                        <div class="member-avatar">
                            <img src="${member.avatar || document.getElementById('static-url').getAttribute('data-default-avatar')}" alt="${member.name}">
                        </div>
                        <div class="member-info">
                            <div class="member-name">${member.name}</div>
                            <div class="member-role">${member.role}</div>
                        </div>
                    `;
                    membersContainer.appendChild(memberElement);
                });
            }
        }
    }
}

// Create a global instance of the WebSocketManager
const wsManager = new WebSocketManager();

// Initialize notifications when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page that needs WebSockets
    const body = document.body;
    
    // Initialize notifications on all authenticated pages
    if (!body.classList.contains('login-page') && !body.classList.contains('register-page')) {
        wsManager.initNotifications();
    }
    
    // Initialize owner dashboard WebSocket if on owner dashboard
    if (body.classList.contains('owner-dashboard')) {
        wsManager.initOwnerDashboard();
    }
    
    // Initialize project WebSocket if on a project page
    const projectIdElement = document.getElementById('project-id');
    if (projectIdElement) {
        const projectId = projectIdElement.value;
        if (projectId) {
            wsManager.initProject(projectId);
        }
    }
    
    // Initialize team WebSocket if on a team page
    const teamIdElement = document.getElementById('team-id');
    if (teamIdElement) {
        const teamId = teamIdElement.value;
        if (teamId) {
            wsManager.initTeam(teamId);
        }
    }
});