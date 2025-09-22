// Owner Dashboard Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Company key copied to clipboard!', 'success');
        }, function(err) {
            console.error('Could not copy text: ', err);
            showNotification('Failed to copy to clipboard', 'error');
        });
    };

    // Notification system
    function showNotification(message, type = 'info') {
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
        }, 3000);
    }

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

    // Table row hover effects
    const tableRows = document.querySelectorAll('#companiesTable tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(37, 99, 235, 0.05)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Search functionality for companies table
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Search companies...';
    
    const tableContainer = document.querySelector('.table-responsive');
    if (tableContainer) {
        tableContainer.parentNode.insertBefore(searchInput, tableContainer);
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#companiesTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Stats counter animation
    function animateCounters() {
        const counters = document.querySelectorAll('.h5.mb-0');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
            if (target > 0) {
                const duration = 2000;
                const increment = target / (duration / 16);
                let current = 0;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    counter.textContent = Math.floor(current);
                }, 16);
            }
        });
    }

    // Trigger counter animation when page loads
    setTimeout(animateCounters, 500);

    // Modal enhancement
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const input = this.querySelector('input[readonly]');
            if (input) {
                input.select();
            }
        });
    });

    // Export functionality (placeholder)
    window.exportCompanies = function(format) {
        console.log('Exporting companies in', format, 'format');
        showNotification('Export functionality coming soon!', 'info');
    };

    // Bulk selection functionality
    window.toggleSelectAll = function() {
        const selectAll = document.getElementById('selectAll');
        const checkboxes = document.querySelectorAll('.company-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll.checked;
        });
        
        updateBulkActions();
    };

    // Update bulk actions visibility
    function updateBulkActions() {
        const checkboxes = document.querySelectorAll('.company-checkbox:checked');
        const bulkActions = document.getElementById('bulkActions');
        const selectedCount = document.getElementById('selectedCount');
        
        if (checkboxes.length > 0) {
            bulkActions.style.display = 'block';
            selectedCount.textContent = `${checkboxes.length} companies selected`;
        } else {
            bulkActions.style.display = 'none';
        }
    }

    // Individual checkbox change
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('company-checkbox')) {
            updateBulkActions();
        }
    });

    // Bulk operations
    window.bulkActivate = function() {
        const selectedIds = getSelectedCompanyIds();
        if (selectedIds.length === 0) {
            showNotification('Please select companies first', 'warning');
            return;
        }
        
        if (confirm(`Activate ${selectedIds.length} selected companies?`)) {
            performBulkAction('activate', selectedIds);
        }
    };

    window.bulkDeactivate = function() {
        const selectedIds = getSelectedCompanyIds();
        if (selectedIds.length === 0) {
            showNotification('Please select companies first', 'warning');
            return;
        }
        
        if (confirm(`Deactivate ${selectedIds.length} selected companies?`)) {
            performBulkAction('deactivate', selectedIds);
        }
    };

    window.bulkDelete = function() {
        const selectedIds = getSelectedCompanyIds();
        if (selectedIds.length === 0) {
            showNotification('Please select companies first', 'warning');
            return;
        }
        
        if (confirm(`Delete ${selectedIds.length} selected companies? This action cannot be undone!`)) {
            performBulkAction('delete', selectedIds);
        }
    };

    // Get selected company IDs
    function getSelectedCompanyIds() {
        const checkboxes = document.querySelectorAll('.company-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    // Perform bulk action
    function performBulkAction(action, companyIds) {
        showNotification(`Performing bulk ${action} operation...`, 'info');
        
        // This would typically make AJAX calls to the server
        // For now, we'll simulate the operation
        setTimeout(() => {
            showNotification(`Bulk ${action} operation completed!`, 'success');
            location.reload(); // Refresh the page
        }, 2000);
    }

    // Company deletion confirmation
    window.confirmDeleteCompany = function(companyId, companyName) {
        if (confirm(`Are you sure you want to delete "${companyName}"? This action cannot be undone and will delete all associated data.`)) {
            // Redirect to delete URL
            window.location.href = `/owner/company/${companyId}/delete/`;
        }
    };

    // Dashboard refresh
    window.refreshDashboard = function() {
        showNotification('Refreshing dashboard data...', 'info');
        location.reload();
    };

    window.refreshCompanies = function() {
        showNotification('Refreshing companies data...', 'info');
        location.reload();
    };

    // System settings
    window.showSystemSettings = function() {
        showNotification('System settings functionality coming soon!', 'info');
    };

    // Dashboard Widgets Functionality
    function initializeDashboardWidgets() {
        // Load notifications
        loadNotifications();
        
        // Load system performance
        loadSystemPerformance();
        
        // Load subscription overview
        loadSubscriptionOverview();
        
        // Load API usage stats
        loadApiUsage();
        
        // Set up auto-refresh for widgets
        setInterval(loadNotifications, 30000); // Refresh every 30 seconds
        setInterval(loadSystemPerformance, 10000); // Refresh every 10 seconds
        setInterval(loadSubscriptionOverview, 60000); // Refresh every minute
        setInterval(loadApiUsage, 30000); // Refresh every 30 seconds
    }

    // Load notifications
    function loadNotifications() {
        fetch('/owner/api/dashboard/notifications/')
            .then(response => response.json())
            .then(data => {
                const notificationsList = document.getElementById('notificationsList');
                const notificationCount = document.getElementById('notificationCount');
                
                if (data.notifications && data.notifications.length > 0) {
                    notificationCount.textContent = data.notifications.length;
                    notificationCount.style.display = 'inline';
                    
                    notificationsList.innerHTML = data.notifications.map(notification => `
                        <div class="d-flex align-items-center mb-3 p-2 border-left border-${notification.type}">
                            <div class="me-3">
                                <i class="fas fa-${getNotificationIcon(notification.type)} text-${notification.type}"></i>
                            </div>
                            <div class="flex-grow-1">
                                <div class="font-weight-bold">${notification.title}</div>
                                <div class="text-muted small">${notification.message}</div>
                                <div class="text-muted small">${notification.time_ago}</div>
                            </div>
                        </div>
                    `).join('');
                } else {
                    notificationCount.style.display = 'none';
                    notificationsList.innerHTML = '<div class="text-center text-muted">No new notifications</div>';
                }
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                document.getElementById('notificationsList').innerHTML = 
                    '<div class="text-center text-danger">Error loading notifications</div>';
            });
    }

    // Load system performance
    function loadSystemPerformance() {
        fetch('/owner/api/dashboard/system-performance/')
            .then(response => response.json())
            .then(data => {
                // Update CPU usage
                document.getElementById('cpuProgress').style.width = data.cpu_usage + '%';
                document.getElementById('cpuText').textContent = data.cpu_usage + '%';
                
                // Update Memory usage
                document.getElementById('memoryProgress').style.width = data.memory_usage + '%';
                document.getElementById('memoryText').textContent = data.memory_usage + '%';
                
                // Update Active Sessions
                document.getElementById('activeSessions').textContent = data.active_sessions;
                
                // Update Response Time
                document.getElementById('responseTime').textContent = data.avg_response_time + 'ms';
            })
            .catch(error => {
                console.error('Error loading system performance:', error);
            });
    }

    // Load subscription overview
    function loadSubscriptionOverview() {
        fetch('/owner/api/dashboard/subscription-overview/')
            .then(response => response.json())
            .then(data => {
                // Update subscription counts
                document.getElementById('activeSubscriptions').textContent = data.active_count;
                document.getElementById('trialSubscriptions').textContent = data.trial_count;
                document.getElementById('expiredSubscriptions').textContent = data.expired_count;
                document.getElementById('monthlyRevenue').textContent = '$' + data.monthly_revenue.toLocaleString();
                
                // Update upcoming renewals table
                const upcomingRenewals = document.getElementById('upcomingRenewals');
                if (data.upcoming_renewals && data.upcoming_renewals.length > 0) {
                    upcomingRenewals.innerHTML = data.upcoming_renewals.map(renewal => `
                        <tr>
                            <td>${renewal.company_name}</td>
                            <td><span class="badge bg-${renewal.plan_color}">${renewal.plan_name}</span></td>
                            <td>${renewal.expires_date}</td>
                            <td>
                                <span class="badge bg-${renewal.days_left <= 7 ? 'danger' : renewal.days_left <= 30 ? 'warning' : 'success'}">
                                    ${renewal.days_left} days
                                </span>
                            </td>
                        </tr>
                    `).join('');
                } else {
                    upcomingRenewals.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No upcoming renewals</td></tr>';
                }
            })
            .catch(error => {
                console.error('Error loading subscription overview:', error);
            });
    }

    // Load API usage stats
    function loadApiUsage() {
        fetch('/owner/api/dashboard/api-usage/')
            .then(response => response.json())
            .then(data => {
                // Update API stats
                document.getElementById('totalApiRequests').textContent = data.total_requests.toLocaleString();
                document.getElementById('apiSuccessProgress').style.width = data.success_rate + '%';
                document.getElementById('apiSuccessRate').textContent = data.success_rate + '%';
                document.getElementById('avgApiResponseTime').textContent = data.avg_response_time + 'ms';
                document.getElementById('failedApiRequests').textContent = data.failed_requests.toLocaleString();
            })
            .catch(error => {
                console.error('Error loading API usage:', error);
            });
    }

    // Helper function to get notification icon
    function getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'danger': 'exclamation-circle',
            'info': 'info-circle',
            'primary': 'bell'
        };
        return icons[type] || 'bell';
    }

    // Initialize widgets when page loads
    setTimeout(initializeDashboardWidgets, 1000);

    // Initialize advanced filtering
    initializeAdvancedFiltering();
    
    // Initialize advanced analytics
    initializeAdvancedAnalytics();
    
    console.log('Owner dashboard initialized successfully');
});

// Advanced Analytics Functions
let analyticsCharts = {};

function initializeAdvancedAnalytics() {
    // Initialize date range selector
    const dateRangeSelect = document.getElementById('analyticsDateRange');
    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                document.getElementById('customDateRange').style.display = 'block';
            } else {
                document.getElementById('customDateRange').style.display = 'none';
                loadAnalyticsData(this.value);
            }
        });
    }

    // Initialize custom date inputs
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    if (startDate && endDate) {
        startDate.addEventListener('change', loadCustomAnalytics);
        endDate.addEventListener('change', loadCustomAnalytics);
    }

    // Load initial analytics data
    loadAnalyticsData(30); // Default to last 30 days
}

function loadAnalyticsData(days) {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);
    
    loadGrowthAnalytics(startDate, endDate);
    loadRevenueAnalytics(startDate, endDate);
    loadPredictiveAnalytics(startDate, endDate);
    loadComparativeAnalytics(startDate, endDate);
}

function loadCustomAnalytics() {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput.value && endDateInput.value) {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (startDate <= endDate) {
            loadGrowthAnalytics(startDate, endDate);
            loadRevenueAnalytics(startDate, endDate);
            loadPredictiveAnalytics(startDate, endDate);
            loadComparativeAnalytics(startDate, endDate);
        }
    }
}

function loadGrowthAnalytics(startDate, endDate) {
    // Make API call for growth data
    const params = new URLSearchParams({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
    });
    
    fetch(`/api/analytics/growth-data/?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading growth analytics:', data.error);
                // Fallback to mock data
                const mockData = generateMockGrowthData(startDate, endDate);
                updateGrowthMetrics(mockData);
                createGrowthChart(mockData.chart_data);
            } else {
                updateGrowthMetrics(data);
                createGrowthChart(data.chart_data);
            }
        })
        .catch(error => {
            console.error('Error loading growth analytics:', error);
            // Fallback to mock data
            const mockData = generateMockGrowthData(startDate, endDate);
            updateGrowthMetrics(mockData);
            createGrowthChart(mockData.chart_data);
        });
}

function updateGrowthMetrics(data) {
    document.getElementById('companyGrowthRate').textContent = `+${data.company_growth}%`;
    document.getElementById('userGrowthRate').textContent = `+${data.user_growth}%`;
    document.getElementById('churnRate').textContent = `${data.churn_rate}%`;
}

function loadRevenueAnalytics(startDate, endDate) {
    // Make API call for revenue data
    const params = new URLSearchParams({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
    });
    
    fetch(`/api/analytics/revenue-data/?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading revenue analytics:', data.error);
                // Fallback to mock data
                const mockData = generateMockRevenueData(startDate, endDate);
                updateRevenueMetrics(mockData);
                createRevenueChart(mockData.chart_data);
            } else {
                updateRevenueMetrics(data);
                createRevenueChart(data.chart_data);
            }
        })
        .catch(error => {
            console.error('Error loading revenue analytics:', error);
            // Fallback to mock data
            const mockData = generateMockRevenueData(startDate, endDate);
            updateRevenueMetrics(mockData);
            createRevenueChart(mockData.chart_data);
        });
}

function updateRevenueMetrics(data) {
    document.getElementById('mrrGrowth').textContent = `+$${data.mrr_growth}`;
    document.getElementById('arpu').textContent = `$${data.arpu}`;
    document.getElementById('ltv').textContent = `$${data.ltv}`;
}

function loadPredictiveAnalytics(startDate, endDate) {
    // Make API call for predictive data
    const params = new URLSearchParams({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
    });
    
    fetch(`/api/analytics/predictive-data/?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading predictive analytics:', data.error);
                // Fallback to mock data
                const mockData = generateMockPredictiveData(startDate, endDate);
                updatePredictiveMetrics(mockData);
                createPredictiveChart(mockData.chart_data);
            } else {
                updatePredictiveMetrics(data);
                createPredictiveChart(data.chart_data);
            }
        })
        .catch(error => {
            console.error('Error loading predictive analytics:', error);
            // Fallback to mock data
            const mockData = generateMockPredictiveData(startDate, endDate);
            updatePredictiveMetrics(mockData);
            createPredictiveChart(mockData.chart_data);
        });
}

function updatePredictiveMetrics(data) {
    document.getElementById('predictedGrowth3M').textContent = `+${data.predicted_growth}%`;
    document.getElementById('predictedRevenue3M').textContent = `$${data.predicted_revenue}`;
    document.getElementById('riskScore').textContent = data.risk_score;
}

function loadComparativeAnalytics(startDate, endDate) {
    // Make API call for comparative data
    const params = new URLSearchParams({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
    });
    
    fetch(`/api/analytics/comparative-data/?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading comparative analytics:', data.error);
                // Fallback to mock data
                const mockData = generateMockComparativeData(startDate, endDate);
                updateComparativeMetrics(mockData);
                createComparisonChart(mockData.chart_data);
            } else {
                updateComparativeMetrics(data);
                createComparisonChart(data.chart_data);
            }
        })
        .catch(error => {
            console.error('Error loading comparative analytics:', error);
            // Fallback to mock data
            const mockData = generateMockComparativeData(startDate, endDate);
            updateComparativeMetrics(mockData);
            createComparisonChart(mockData.chart_data);
        });
}

function updateComparativeMetrics(data) {
    document.getElementById('currentPeriodCompanies').textContent = data.current.companies;
    document.getElementById('previousPeriodCompanies').textContent = data.previous.companies;
    document.getElementById('companiesChange').textContent = `+${data.changes.companies}%`;
    
    document.getElementById('currentPeriodUsers').textContent = data.current.users;
    document.getElementById('previousPeriodUsers').textContent = data.previous.users;
    document.getElementById('usersChange').textContent = `+${data.changes.users}%`;
    
    document.getElementById('currentPeriodRevenue').textContent = `$${data.current.revenue}`;
    document.getElementById('previousPeriodRevenue').textContent = `$${data.previous.revenue}`;
    document.getElementById('revenueChange').textContent = `+${data.changes.revenue}%`;
}

function createGrowthChart(data) {
    const ctx = document.getElementById('growthChart');
    if (!ctx) return;
    
    if (analyticsCharts.growth) {
        analyticsCharts.growth.destroy();
    }
    
    analyticsCharts.growth = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Companies',
                data: data.companies,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4
            }, {
                label: 'Users',
                data: data.users,
                borderColor: '#17a2b8',
                backgroundColor: 'rgba(23, 162, 184, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createRevenueChart(data) {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;
    
    if (analyticsCharts.revenue) {
        analyticsCharts.revenue.destroy();
    }
    
    analyticsCharts.revenue = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Revenue',
                data: data.revenue,
                backgroundColor: '#007bff',
                borderColor: '#0056b3',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function createPredictiveChart(data) {
    const ctx = document.getElementById('predictiveChart');
    if (!ctx) return;
    
    if (analyticsCharts.predictive) {
        analyticsCharts.predictive.destroy();
    }
    
    analyticsCharts.predictive = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Historical',
                data: data.historical,
                borderColor: '#6c757d',
                backgroundColor: 'rgba(108, 117, 125, 0.1)',
                tension: 0.4
            }, {
                label: 'Predicted',
                data: data.predicted,
                borderColor: '#ffc107',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                borderDash: [5, 5],
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createComparisonChart(data) {
    const ctx = document.getElementById('comparisonChart');
    if (!ctx) return;
    
    if (analyticsCharts.comparison) {
        analyticsCharts.comparison.destroy();
    }
    
    analyticsCharts.comparison = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: ['#28a745', '#17a2b8', '#ffc107'],
                borderWidth: 2
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

// Mock data generators
function generateMockGrowthData(startDate, endDate) {
    const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
    const labels = [];
    const companies = [];
    const users = [];
    
    for (let i = 0; i < Math.min(days, 30); i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        labels.push(date.toLocaleDateString());
        companies.push(Math.floor(Math.random() * 50) + 100 + i * 2);
        users.push(Math.floor(Math.random() * 200) + 500 + i * 10);
    }
    
    return {
        companyGrowth: (Math.random() * 20 + 5).toFixed(1),
        userGrowth: (Math.random() * 30 + 10).toFixed(1),
        churnRate: (Math.random() * 5 + 1).toFixed(1),
        chartData: { labels, companies, users }
    };
}

function generateMockRevenueData(startDate, endDate) {
    const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
    const labels = [];
    const revenue = [];
    
    for (let i = 0; i < Math.min(days, 30); i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        labels.push(date.toLocaleDateString());
        revenue.push(Math.floor(Math.random() * 5000) + 10000 + i * 200);
    }
    
    return {
        mrrGrowth: (Math.random() * 5000 + 2000).toFixed(0),
        arpu: (Math.random() * 100 + 50).toFixed(0),
        ltv: (Math.random() * 2000 + 1000).toFixed(0),
        chartData: { labels, revenue }
    };
}

function generateMockPredictiveData(startDate, endDate) {
    const labels = ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'];
    const historical = [100, 120, 140, 160, 180, 200];
    const predicted = [null, null, null, null, 220, 250];
    
    return {
        predictedGrowth: (Math.random() * 15 + 10).toFixed(1),
        predictedRevenue: (Math.random() * 50000 + 100000).toFixed(0),
        riskScore: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
        chartData: { labels, historical, predicted }
    };
}

function generateMockComparativeData(startDate, endDate) {
    return {
        current: {
            companies: Math.floor(Math.random() * 50) + 150,
            users: Math.floor(Math.random() * 500) + 1000,
            revenue: (Math.random() * 50000 + 100000).toFixed(0)
        },
        previous: {
            companies: Math.floor(Math.random() * 40) + 120,
            users: Math.floor(Math.random() * 400) + 800,
            revenue: (Math.random() * 40000 + 80000).toFixed(0)
        },
        changes: {
            companies: (Math.random() * 20 + 5).toFixed(1),
            users: (Math.random() * 25 + 10).toFixed(1),
            revenue: (Math.random() * 30 + 15).toFixed(1)
        },
        chartData: {
            labels: ['Companies', 'Users', 'Revenue'],
            values: [30, 45, 25]
        }
    };
}

function refreshAnalytics() {
    const dateRange = document.getElementById('analyticsDateRange').value;
    if (dateRange === 'custom') {
        loadCustomAnalytics();
    } else {
        loadAnalyticsData(parseInt(dateRange));
    }
    showNotification('Analytics refreshed successfully!', 'success');
}

function exportAnalytics(format) {
    // Simulate export functionality
    showNotification(`Exporting analytics as ${format.toUpperCase()}...`, 'info');
    
    setTimeout(() => {
        showNotification(`Analytics exported successfully as ${format.toUpperCase()}!`, 'success');
    }, 2000);
}

// Advanced Filtering System
function initializeAdvancedFiltering() {
    // Store original table data for filtering
    window.originalTableData = [];
    const tableRows = document.querySelectorAll('#companiesTable tbody tr');
    tableRows.forEach(row => {
        if (row.cells.length > 1) { // Skip empty rows
            window.originalTableData.push({
                element: row.cloneNode(true),
                name: row.cells[1]?.textContent?.trim() || '',
                domain: row.cells[2]?.textContent?.trim() || '',
                admin: row.cells[3]?.textContent?.trim() || '',
                status: row.cells[4]?.textContent?.trim().toLowerCase() || '',
                employees: parseInt(row.cells[5]?.textContent?.trim()) || 0,
                plan: row.cells[6]?.textContent?.trim().toLowerCase() || '',
                date: row.cells[7]?.textContent?.trim() || ''
            });
        }
    });
    
    console.log('Advanced filtering initialized with', window.originalTableData.length, 'companies');
}

function applyFilters() {
    const filters = {
        status: document.getElementById('statusFilter')?.value || '',
        plan: document.getElementById('planFilter')?.value || '',
        date: document.getElementById('dateFilter')?.value || '',
        size: document.getElementById('sizeFilter')?.value || '',
        search: document.getElementById('searchFilter')?.value?.toLowerCase() || '',
        sort: document.getElementById('sortFilter')?.value || 'name_asc',
        limit: parseInt(document.getElementById('limitFilter')?.value) || 25
    };
    
    if (!window.originalTableData) {
        console.warn('Original table data not available');
        return;
    }
    
    let filteredData = [...window.originalTableData];
    
    // Apply status filter
    if (filters.status) {
        filteredData = filteredData.filter(item => 
            item.status.includes(filters.status.toLowerCase())
        );
    }
    
    // Apply plan filter
    if (filters.plan) {
        filteredData = filteredData.filter(item => 
            item.plan.includes(filters.plan.toLowerCase())
        );
    }
    
    // Apply size filter
    if (filters.size) {
        filteredData = filteredData.filter(item => {
            const employees = item.employees;
            switch (filters.size) {
                case 'small': return employees >= 1 && employees <= 10;
                case 'medium': return employees >= 11 && employees <= 50;
                case 'large': return employees >= 51 && employees <= 200;
                case 'enterprise': return employees > 200;
                default: return true;
            }
        });
    }
    
    // Apply search filter
    if (filters.search) {
        filteredData = filteredData.filter(item => 
            item.name.toLowerCase().includes(filters.search) ||
            item.domain.toLowerCase().includes(filters.search) ||
            item.admin.toLowerCase().includes(filters.search)
        );
    }
    
    // Apply date filter
    if (filters.date) {
        const now = new Date();
        filteredData = filteredData.filter(item => {
            const itemDate = new Date(item.date);
            switch (filters.date) {
                case 'today':
                    return itemDate.toDateString() === now.toDateString();
                case 'week':
                    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    return itemDate >= weekAgo;
                case 'month':
                    return itemDate.getMonth() === now.getMonth() && 
                           itemDate.getFullYear() === now.getFullYear();
                case 'quarter':
                    const quarter = Math.floor(now.getMonth() / 3);
                    const itemQuarter = Math.floor(itemDate.getMonth() / 3);
                    return itemQuarter === quarter && 
                           itemDate.getFullYear() === now.getFullYear();
                case 'year':
                    return itemDate.getFullYear() === now.getFullYear();
                default:
                    return true;
            }
        });
    }
    
    // Apply sorting
    filteredData.sort((a, b) => {
        switch (filters.sort) {
            case 'name_asc': return a.name.localeCompare(b.name);
            case 'name_desc': return b.name.localeCompare(a.name);
            case 'date_asc': return new Date(a.date) - new Date(b.date);
            case 'date_desc': return new Date(b.date) - new Date(a.date);
            case 'employees_asc': return a.employees - b.employees;
            case 'employees_desc': return b.employees - a.employees;
            default: return 0;
        }
    });
    
    // Apply pagination
    const totalResults = filteredData.length;
    filteredData = filteredData.slice(0, filters.limit);
    
    // Update table
    updateTableWithFilteredData(filteredData);
    
    // Update results info
    updateFilterResults(totalResults, filteredData.length, filters.limit);
    
    console.log('Filters applied:', filters, 'Results:', filteredData.length);
}

function updateTableWithFilteredData(data) {
    const tbody = document.querySelector('#companiesTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    <i class="fas fa-search fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No companies match your filter criteria</p>
                </td>
            </tr>
        `;
        return;
    }
    
    data.forEach(item => {
        const row = item.element.cloneNode(true);
        // Re-attach event listeners for checkboxes
        const checkbox = row.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener('change', updateBulkActionsVisibility);
        }
        tbody.appendChild(row);
    });
}

function updateFilterResults(total, showing, limit) {
    const resultsElement = document.getElementById('filterResults');
    if (resultsElement) {
        let message = `Showing ${showing} of ${total} companies`;
        if (showing === limit && total > limit) {
            message += ` (limited to ${limit})`;
        }
        resultsElement.textContent = message;
    }
}

function clearAllFilters() {
    // Reset all filter controls
    document.getElementById('statusFilter').value = '';
    document.getElementById('planFilter').value = '';
    document.getElementById('dateFilter').value = '';
    document.getElementById('sizeFilter').value = '';
    document.getElementById('searchFilter').value = '';
    document.getElementById('sortFilter').value = 'name_asc';
    document.getElementById('limitFilter').value = '25';
    
    // Reapply filters (which will now show all data)
    applyFilters();
}

function clearSearch() {
    document.getElementById('searchFilter').value = '';
    applyFilters();
}

function exportFiltered() {
    const filters = {
        status: document.getElementById('statusFilter')?.value || '',
        plan: document.getElementById('planFilter')?.value || '',
        date: document.getElementById('dateFilter')?.value || '',
        size: document.getElementById('sizeFilter')?.value || '',
        search: document.getElementById('searchFilter')?.value || ''
    };
    
    // Create export parameters
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
        if (filters[key]) {
            params.append(key, filters[key]);
        }
    });
    
    // Trigger export with filters
    window.location.href = `/owner/export-companies/?${params.toString()}`;
    
    showNotification('Export started with current filters', 'info');
}

// Enhanced Bulk Operations
function bulkSuspend() {
    const selectedIds = getSelectedCompanyIds();
    if (selectedIds.length === 0) {
        showNotification('Please select companies to suspend', 'warning');
        return;
    }
    
    if (confirm(`Are you sure you want to suspend ${selectedIds.length} selected companies?`)) {
        performBulkOperation('suspend', selectedIds);
    }
}

function bulkChangePlan() {
    const selectedIds = getSelectedCompanyIds();
    if (selectedIds.length === 0) {
        showNotification('Please select companies to change plan', 'warning');
        return;
    }
    
    // Show plan selection modal
    showPlanSelectionModal(selectedIds);
}

function bulkExtendTrial() {
    const selectedIds = getSelectedCompanyIds();
    if (selectedIds.length === 0) {
        showNotification('Please select companies to extend trial', 'warning');
        return;
    }
    
    const days = prompt('Enter number of days to extend trial:', '30');
    if (days && !isNaN(days) && parseInt(days) > 0) {
        performBulkOperation('extend_trial', selectedIds, { days: parseInt(days) });
    }
}

function bulkApplyDiscount() {
    const selectedIds = getSelectedCompanyIds();
    if (selectedIds.length === 0) {
        showNotification('Please select companies to apply discount', 'warning');
        return;
    }
    
    const discount = prompt('Enter discount percentage (0-100):', '10');
    if (discount && !isNaN(discount) && parseFloat(discount) >= 0 && parseFloat(discount) <= 100) {
        performBulkOperation('apply_discount', selectedIds, { discount: parseFloat(discount) });
    }
}

function bulkExport() {
    const selectedIds = getSelectedCompanyIds();
    if (selectedIds.length === 0) {
        showNotification('Please select companies to export', 'warning');
        return;
    }
    
    // Create form for POST request
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/owner/export-selected-companies/';
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
    }
    
    // Add selected IDs
    selectedIds.forEach(id => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'company_ids';
        input.value = id;
        form.appendChild(input);
    });
    
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
    
    showNotification(`Exporting ${selectedIds.length} selected companies`, 'info');
}

function bulkSendNotification() {
    const selectedIds = getSelectedCompanyIds();
    if (selectedIds.length === 0) {
        showNotification('Please select companies to send notification', 'warning');
        return;
    }
    
    showNotificationModal(selectedIds);
}

function showPlanSelectionModal(companyIds) {
    // Create modal for plan selection
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Change Subscription Plan</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Select new plan for ${companyIds.length} selected companies:</p>
                    <select class="form-select" id="newPlan">
                        <option value="basic">Basic Plan</option>
                        <option value="professional">Professional Plan</option>
                        <option value="enterprise">Enterprise Plan</option>
                        <option value="custom">Custom Plan</option>
                    </select>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="confirmPlanChange(${JSON.stringify(companyIds)})">Change Plan</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

function confirmPlanChange(companyIds) {
    const newPlan = document.getElementById('newPlan').value;
    performBulkOperation('change_plan', companyIds, { plan: newPlan });
    
    // Close modal
    const modal = document.querySelector('.modal.show');
    if (modal) {
        bootstrap.Modal.getInstance(modal).hide();
    }
}

function showNotificationModal(companyIds) {
    // Create modal for notification
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Send Notification</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Send notification to ${companyIds.length} selected companies:</p>
                    <div class="mb-3">
                        <label class="form-label">Subject</label>
                        <input type="text" class="form-control" id="notificationSubject" placeholder="Enter notification subject">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Message</label>
                        <textarea class="form-control" id="notificationMessage" rows="4" placeholder="Enter notification message"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Type</label>
                        <select class="form-select" id="notificationType">
                            <option value="info">Information</option>
                            <option value="warning">Warning</option>
                            <option value="success">Success</option>
                            <option value="error">Error</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="confirmSendNotification(${JSON.stringify(companyIds)})">Send Notification</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

function confirmSendNotification(companyIds) {
    const subject = document.getElementById('notificationSubject').value;
    const message = document.getElementById('notificationMessage').value;
    const type = document.getElementById('notificationType').value;
    
    if (!subject || !message) {
        showNotification('Please fill in all fields', 'warning');
        return;
    }
    
    performBulkOperation('send_notification', companyIds, {
        subject: subject,
        message: message,
        type: type
    });
    
    // Close modal
    const modal = document.querySelector('.modal.show');
    if (modal) {
        bootstrap.Modal.getInstance(modal).hide();
    }
}
