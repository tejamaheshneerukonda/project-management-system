/**
 * Employee Productivity JavaScript
 * Handles productivity tracking and focus timer functionality for employees
 */

// Timer variables
let timerInterval;
let timerRunning = false;
let timerMinutes = 25;
let timerSeconds = 0;

// Chart and Timer Functions
function initializeFocusChart() {
    const focusData = window.focusSessionsData || [];
    const ctx = document.getElementById('focusChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: focusData.map(item => item.date),
            datasets: [{
                label: 'Focus Duration (min)',
                data: focusData.map(item => item.duration),
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
                    text: 'Daily Focus Sessions'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Minutes'
                    }
                }
            }
        }
    });
}

function startFocusTimer() {
    if (!timerRunning) {
        timerRunning = true;
        timerInterval = setInterval(updateTimer, 1000);
        document.getElementById('startTimerBtn').textContent = 'Pause';
        document.getElementById('startTimerBtn').onclick = pauseFocusTimer;
    }
}

function pauseFocusTimer() {
    if (timerRunning) {
        timerRunning = false;
        clearInterval(timerInterval);
        document.getElementById('startTimerBtn').textContent = 'Resume';
        document.getElementById('startTimerBtn').onclick = startFocusTimer;
    }
}

function resetFocusTimer() {
    timerRunning = false;
    clearInterval(timerInterval);
    timerMinutes = 25;
    timerSeconds = 0;
    updateTimerDisplay();
    document.getElementById('startTimerBtn').textContent = 'Start';
    document.getElementById('startTimerBtn').onclick = startFocusTimer;
}

function updateTimer() {
    if (timerSeconds > 0) {
        timerSeconds--;
    } else if (timerMinutes > 0) {
        timerMinutes--;
        timerSeconds = 59;
    } else {
        // Timer finished
        timerRunning = false;
        clearInterval(timerInterval);
        showSuccessToast('Focus session completed! Great job!');
        resetFocusTimer();
        return;
    }
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const display = document.getElementById('timerDisplay');
    if (display) {
        display.textContent = `${timerMinutes.toString().padStart(2, '0')}:${timerSeconds.toString().padStart(2, '0')}`;
    }
}

function setTimerDuration(minutes) {
    timerMinutes = minutes;
    timerSeconds = 0;
    updateTimerDisplay();
}

function logFocusSession() {
    const duration = (25 - timerMinutes) + (timerSeconds / 60);
    console.log('Focus session logged:', duration, 'minutes');
    // This would send data to backend
    showSuccessToast(`Focus session logged: ${duration.toFixed(1)} minutes`);
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

function changeTimeRange(range) {
    console.log('Changing time range to:', range);
    // This would update the chart data based on the selected range
    location.reload(); // For now, just reload the page
}

// Initialize productivity management functionality
function initProductivityManagement() {
    console.log('Productivity management initialized');
    
    // Initialize focus chart
    initializeFocusChart();
    
    // Update timer display
    updateTimerDisplay();
    
    // Set up timer controls
    const startBtn = document.getElementById('startTimerBtn');
    if (startBtn) {
        startBtn.onclick = startFocusTimer;
    }
    
    const resetBtn = document.getElementById('resetTimerBtn');
    if (resetBtn) {
        resetBtn.onclick = resetFocusTimer;
    }
    
    const logBtn = document.getElementById('logSessionBtn');
    if (logBtn) {
        logBtn.onclick = logFocusSession;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initProductivityManagement();
});

// Export functions for global access
window.startFocusTimer = startFocusTimer;
window.pauseFocusTimer = pauseFocusTimer;
window.resetFocusTimer = resetFocusTimer;
window.setTimerDuration = setTimerDuration;
window.logFocusSession = logFocusSession;
window.exportChart = exportChart;
window.changeTimeRange = changeTimeRange;
