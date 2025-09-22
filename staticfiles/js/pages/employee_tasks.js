/**
 * Employee Tasks JavaScript
 * Handles task management functionality for employees
 */

// Task Management Functions
function updateTaskStatus(taskId, status) {
    if (confirm('Are you sure you want to update this task status?')) {
        fetch(`/api/tasks/${taskId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                status: status
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccessToast('Task status updated successfully!');
                location.reload();
            } else {
                showErrorToast('Error updating task: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Error updating task. Please try again.');
        });
    }
}

function markAllComplete() {
    if (confirm('Are you sure you want to mark all visible tasks as complete?')) {
        const taskIds = Array.from(document.querySelectorAll('.task-item')).map(item => {
            const button = item.querySelector('button[onclick*="updateTaskStatus"]');
            return button ? button.onclick.toString().match(/\d+/)[0] : null;
        }).filter(id => id);
        
        taskIds.forEach(taskId => {
            updateTaskStatus(taskId, 'DONE');
        });
    }
}

function refreshTasks() {
    location.reload();
}

// Initialize task management functionality
function initTaskManagement() {
    console.log('Task management initialized');
    
    // Add any additional initialization code here
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTaskManagement();
});

// Export functions for global access
window.updateTaskStatus = updateTaskStatus;
window.markAllComplete = markAllComplete;
window.refreshTasks = refreshTasks;
