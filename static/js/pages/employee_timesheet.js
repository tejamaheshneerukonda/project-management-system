/**
 * Employee Timesheet JavaScript
 * Handles time tracking and timesheet management functionality for employees
 */

// Timer variables
let timerInterval;
let startTime;
let isRunning = false;

// Timer Functions
function startTimer() {
    if (!isRunning) {
        startTime = new Date();
        isRunning = true;
        
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'inline-block';
        document.getElementById('pauseBtn').style.display = 'inline-block';
        
        timerInterval = setInterval(updateTimer, 1000);
    }
}

function stopTimer() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
        
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('stopBtn').style.display = 'none';
        document.getElementById('pauseBtn').style.display = 'none';
        
        // Auto-fill timesheet form
        const now = new Date();
        const duration = now - startTime;
        const hours = Math.floor(duration / (1000 * 60 * 60));
        const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
        
        document.getElementById('entryDate').value = now.toISOString().split('T')[0];
        document.getElementById('startTime').value = startTime.toTimeString().slice(0, 5);
        document.getElementById('endTime').value = now.toTimeString().slice(0, 5);
        document.getElementById('taskDescription').value = 'Timer session - ' + hours + 'h ' + minutes + 'm';
        
        // Show modal
        new bootstrap.Modal(document.getElementById('addTimesheetModal')).show();
    }
}

function pauseTimer() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
        
        document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-play me-2"></i>Resume';
        document.getElementById('pauseBtn').onclick = resumeTimer;
    }
}

function resumeTimer() {
    if (!isRunning) {
        startTime = new Date(Date.now() - (new Date() - startTime));
        isRunning = true;
        
        document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-pause me-2"></i>Pause';
        document.getElementById('pauseBtn').onclick = pauseTimer;
        
        timerInterval = setInterval(updateTimer, 1000);
    }
}

function updateTimer() {
    if (isRunning) {
        const now = new Date();
        const duration = now - startTime;
        
        const hours = Math.floor(duration / (1000 * 60 * 60));
        const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((duration % (1000 * 60)) / 1000);
        
        document.getElementById('currentTimer').textContent = 
            String(hours).padStart(2, '0') + ':' + 
            String(minutes).padStart(2, '0') + ':' + 
            String(seconds).padStart(2, '0');
    }
}

// Timesheet Management Functions
function addTimesheetEntry() {
    new bootstrap.Modal(document.getElementById('addTimesheetModal')).show();
}

function editTimesheet(timesheetId) {
    window.location.href = `/employee/timesheet/${timesheetId}/edit/`;
}

function submitTimesheet(timesheetId) {
    if (confirm('Are you sure you want to submit this timesheet entry?')) {
        // Submit timesheet logic here
        fetch(`/api/timesheets/${timesheetId}/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Timesheet submitted successfully!', 'success');
                location.reload();
            } else {
                showToast('Error submitting timesheet: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error submitting timesheet. Please try again.', 'error');
        });
    }
}

// Initialize timesheet management functionality
function initTimesheetManagement() {
    console.log('Timesheet management initialized');
    
    // Set today's date as default
    const entryDateInput = document.getElementById('entryDate');
    if (entryDateInput) {
        entryDateInput.value = new Date().toISOString().split('T')[0];
    }
    
    // Form submission
    const timesheetForm = document.getElementById('timesheetForm');
    if (timesheetForm) {
        timesheetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                date: document.getElementById('entryDate').value,
                start_time: document.getElementById('startTime').value,
                end_time: document.getElementById('endTime').value,
                task_description: document.getElementById('taskDescription').value,
                work_performed: document.getElementById('workPerformed').value
            };
            
            // Submit to backend
            fetch('/api/timesheets/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    bootstrap.Modal.getInstance(document.getElementById('addTimesheetModal')).hide();
                    showSuccessToast('Timesheet saved successfully!');
                    location.reload();
                } else {
                    showErrorToast('Error saving timesheet: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorToast('Error saving timesheet. Please try again.');
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTimesheetManagement();
});

// Toast notification function
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

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Export functions for global access
window.startTimer = startTimer;
window.stopTimer = stopTimer;
window.pauseTimer = pauseTimer;
window.resumeTimer = resumeTimer;
window.updateTimer = updateTimer;
window.addTimesheetEntry = addTimesheetEntry;
window.editTimesheet = editTimesheet;
window.submitTimesheet = submitTimesheet;
