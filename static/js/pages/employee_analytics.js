/**
 * Employee Analytics JavaScript
 * Handles data visualization and analytics functionality for employees
 */

// Analytics Functions
function initializeTaskTrendsChart() {
    const taskTrendsData = window.taskTrendsData || [];
    const taskTrendsCtx = document.getElementById('taskTrendsChart').getContext('2d');
    
    new Chart(taskTrendsCtx, {
        type: 'line',
        data: {
            labels: taskTrendsData.map(item => item.date),
            datasets: [{
                label: 'Tasks Completed',
                data: taskTrendsData.map(item => item.completed),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Daily Task Completion'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Tasks'
                    }
                }
            }
        }
    });
}

function initializeWeeklyHoursChart() {
    const weeklyHoursData = window.weeklyHoursData || [];
    const weeklyHoursCtx = document.getElementById('weeklyHoursChart').getContext('2d');
    
    new Chart(weeklyHoursCtx, {
        type: 'doughnut',
        data: {
            labels: weeklyHoursData.map(item => item.day),
            datasets: [{
                data: weeklyHoursData.map(item => item.hours),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF6384'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Weekly Hours Distribution'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function initializeProjectContributionChart() {
    const projectData = window.projectContributionData || [];
    const projectCtx = document.getElementById('projectContributionChart').getContext('2d');
    
    new Chart(projectCtx, {
        type: 'bar',
        data: {
            labels: projectData.map(item => item.project),
            datasets: [{
                label: 'Hours Contributed',
                data: projectData.map(item => item.hours),
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Project Contribution Hours'
                }
            },
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

function changeTimeRange(range) {
    console.log('Changing time range to:', range);
    // This would update all charts based on the selected range
    location.reload(); // For now, just reload the page
}

function exportChart(chartId, format = 'png') {
    const canvas = document.getElementById(chartId);
    if (canvas) {
        const link = document.createElement('a');
        link.download = `chart.${format}`;
        link.href = canvas.toDataURL(`image/${format}`);
        link.click();
    }
}

function refreshAnalytics() {
    location.reload();
}

function toggleChartVisibility(chartId) {
    const chartContainer = document.getElementById(chartId);
    if (chartContainer) {
        chartContainer.style.display = chartContainer.style.display === 'none' ? 'block' : 'none';
    }
}

function generateReport() {
    console.log('Generating analytics report');
    // This would generate a comprehensive analytics report
    showInfoToast('Analytics report generation feature coming soon!');
}

function comparePeriods() {
    console.log('Comparing different time periods');
    // This would show a comparison between different time periods
    showInfoToast('Period comparison feature coming soon!');
}

// Initialize analytics functionality
function initAnalytics() {
    console.log('Analytics initialized');
    
    // Initialize all charts
    initializeTaskTrendsChart();
    initializeWeeklyHoursChart();
    initializeProjectContributionChart();
    
    // Set up time range buttons
    const timeRangeButtons = document.querySelectorAll('.time-range-btn');
    timeRangeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const range = this.dataset.range;
            changeTimeRange(range);
            
            // Update active button
            timeRangeButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initAnalytics();
});

// Export functions for global access
window.changeTimeRange = changeTimeRange;
window.exportChart = exportChart;
window.refreshAnalytics = refreshAnalytics;
window.toggleChartVisibility = toggleChartVisibility;
window.generateReport = generateReport;
window.comparePeriods = comparePeriods;
