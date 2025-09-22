/**
 * Employee Goals JavaScript
 * Handles goal management functionality for employees
 */

// Goal Management Functions
function addNewGoal() {
    // Set default dates
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate());
    
    document.getElementById('startDate').value = today.toISOString().split('T')[0];
    document.getElementById('targetDate').value = nextMonth.toISOString().split('T')[0];
    
    new bootstrap.Modal(document.getElementById('addGoalModal')).show();
}

function updateGoalProgress(goalId) {
    const newValue = prompt('Enter new progress value:');
    if (newValue !== null && newValue !== '') {
        // Update goal progress logic here
        fetch(`/api/goals/${goalId}/update-progress/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                progress: newValue
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Goal progress updated successfully!', 'success');
                location.reload();
            } else {
                showToast('Error updating goal: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating goal. Please try again.', 'error');
        });
    }
}

function markGoalComplete(goalId) {
    if (confirm('Are you sure you want to mark this goal as complete?')) {
        // Mark goal complete logic here
        fetch(`/api/goals/${goalId}/mark-complete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Goal marked as complete!', 'success');
                location.reload();
            } else {
                showToast('Error completing goal: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error completing goal. Please try again.', 'error');
        });
    }
}

function viewGoalDetails(goalId) {
    window.location.href = `/employee/goals/${goalId}/details/`;
}

function refreshGoals() {
    location.reload();
}

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

// Initialize goal management functionality
function initGoalManagement() {
    console.log('Goal management initialized');
    
    // Form submission
    const goalForm = document.getElementById('goalForm');
    if (goalForm) {
        goalForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('goalTitle').value,
                description: document.getElementById('goalDescription').value,
                goal_type: document.getElementById('goalType').value,
                priority: document.getElementById('goalPriority').value,
                start_date: document.getElementById('startDate').value,
                target_date: document.getElementById('targetDate').value,
                target_value: document.getElementById('targetValue').value,
                unit: document.getElementById('unit').value,
                success_criteria: document.getElementById('successCriteria').value
            };
            
            // Submit to backend
            fetch('/api/goals/create/', {
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
                    bootstrap.Modal.getInstance(document.getElementById('addGoalModal')).hide();
                    showSuccessToast('Goal created successfully!');
                    location.reload();
                } else {
                    showErrorToast('Error creating goal: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorToast('Error creating goal. Please try again.');
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initGoalManagement();
});

// Export functions for global access
window.addNewGoal = addNewGoal;
window.updateGoalProgress = updateGoalProgress;
window.markGoalComplete = markGoalComplete;
window.viewGoalDetails = viewGoalDetails;
window.refreshGoals = refreshGoals;
