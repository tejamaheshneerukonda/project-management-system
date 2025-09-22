// System Logs Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-submit form on filter change
    const filterForm = document.getElementById('filterForm');
    const levelSelect = document.getElementById('level');
    const categorySelect = document.getElementById('category');
    
    if (levelSelect) {
        levelSelect.addEventListener('change', function() {
            filterForm.submit();
        });
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            filterForm.submit();
        });
    }

    // Search input with debounce
    const searchInput = document.getElementById('search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                filterForm.submit();
            }, 500);
        });
    }

    // Date range validation
    const dateFromInput = document.getElementById('date_from');
    const dateToInput = document.getElementById('date_to');
    
    if (dateFromInput && dateToInput) {
        dateFromInput.addEventListener('change', function() {
            if (dateToInput.value && dateFromInput.value > dateToInput.value) {
                showErrorToast('From date cannot be after To date');
                dateFromInput.value = '';
            }
        });
        
        dateToInput.addEventListener('change', function() {
            if (dateFromInput.value && dateToInput.value < dateFromInput.value) {
                showErrorToast('To date cannot be before From date');
                dateToInput.value = '';
            }
        });
    }

    // Log entry interactions
    const logEntries = document.querySelectorAll('.log-entry');
    logEntries.forEach(function(entry) {
        entry.addEventListener('click', function() {
            // Toggle expanded view for long messages
            const message = this.querySelector('.log-message');
            if (message && message.textContent.length > 200) {
                message.classList.toggle('expanded');
                if (message.classList.contains('expanded')) {
                    message.style.maxHeight = 'none';
                    message.style.whiteSpace = 'pre-wrap';
                } else {
                    message.style.maxHeight = '3em';
                    message.style.whiteSpace = 'nowrap';
                    message.style.overflow = 'hidden';
                    message.style.textOverflow = 'ellipsis';
                }
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + F to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Ctrl/Cmd + R to refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            location.reload();
        }
        
        // Escape to clear filters
        if (e.key === 'Escape') {
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                filterForm.submit();
            }
        }
    });

    // Real-time updates simulation
    let lastUpdateTime = new Date().getTime();
    
    function checkForUpdates() {
        // This would typically make an AJAX request to check for new logs
        // For now, we'll just update the timestamp
        const now = new Date().getTime();
        if (now - lastUpdateTime > 30000) { // 30 seconds
            lastUpdateTime = now;
            updateLastRefreshTime();
        }
    }
    
    function updateLastRefreshTime() {
        const refreshIndicator = document.querySelector('.refresh-indicator');
        if (refreshIndicator) {
            refreshIndicator.textContent = 'Last updated: ' + new Date().toLocaleTimeString();
        }
    }

    // Export functionality
    window.exportLogs = function() {
        const params = new URLSearchParams(window.location.search);
        params.set('export', 'csv');
        
        // Show loading state
        const exportBtn = document.querySelector('[onclick="exportLogs()"]');
        if (exportBtn) {
            exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Exporting...';
            exportBtn.disabled = true;
        }
        
        // Create download link
        const link = document.createElement('a');
        link.href = window.location.pathname + '?' + params.toString();
        link.download = 'system_logs_' + new Date().toISOString().split('T')[0] + '.csv';
        link.click();
        
        // Reset button after delay
        setTimeout(function() {
            if (exportBtn) {
                exportBtn.innerHTML = '<i class="fas fa-download me-1"></i>Export';
                exportBtn.disabled = false;
            }
        }, 2000);
    };

    // Clear old logs functionality
    window.clearOldLogs = function() {
        if (confirm('Are you sure you want to clear logs older than 30 days? This action cannot be undone.')) {
            // Show loading state
            const clearBtn = document.querySelector('[onclick="clearOldLogs()"]');
            if (clearBtn) {
                clearBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Clearing...';
                clearBtn.disabled = true;
            }
            
            // This would typically make an AJAX request to clear old logs
            // For now, we'll just show a message
            setTimeout(function() {
                showInfoToast('Clear old logs functionality will be implemented in the next update.');
                if (clearBtn) {
                    clearBtn.innerHTML = '<i class="fas fa-trash me-1"></i>Clear Old';
                    clearBtn.disabled = false;
                }
            }, 1000);
        }
    };

    // Log level filtering with visual feedback
    const logLevels = document.querySelectorAll('.log-level');
    logLevels.forEach(function(level) {
        level.addEventListener('click', function() {
            const levelValue = this.textContent.trim();
            const levelSelect = document.getElementById('level');
            if (levelSelect) {
                levelSelect.value = levelValue;
                filterForm.submit();
            }
        });
    });

    // Category filtering with visual feedback
    const categoryIcons = document.querySelectorAll('.log-entry i[class*="fa-"]');
    categoryIcons.forEach(function(icon) {
        icon.addEventListener('click', function() {
            const categoryMap = {
                'fa-key': 'AUTH',
                'fa-user': 'USER',
                'fa-building': 'COMPANY',
                'fa-database': 'BACKUP',
                'fa-shield-alt': 'SECURITY',
                'fa-cog': 'SYSTEM',
                'fa-code': 'API',
                'fa-file': 'FILE',
                'fa-info-circle': 'OTHER'
            };
            
            const iconClass = this.className.split(' ').find(cls => cls.startsWith('fa-'));
            const categoryValue = categoryMap[iconClass];
            
            if (categoryValue) {
                const categorySelect = document.getElementById('category');
                if (categorySelect) {
                    categorySelect.value = categoryValue;
                    filterForm.submit();
                }
            }
        });
    });

    // Auto-refresh functionality
    let autoRefreshInterval;
    
    function startAutoRefresh() {
        autoRefreshInterval = setInterval(function() {
            if (document.visibilityState === 'visible') {
                location.reload();
            }
        }, 30000); // 30 seconds
    }
    
    function stopAutoRefresh() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
    }
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Stop auto-refresh when page is hidden
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });

    // Initialize page
    updateLastRefreshTime();
    console.log('System Logs page initialized');
});
