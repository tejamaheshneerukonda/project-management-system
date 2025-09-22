/**
 * Leave Management JavaScript
 * Handles all leave request functionality for employees
 */

// Leave Management Functions
function requestLeave() {
    // Set default dates
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    document.getElementById('startDate').value = today.toISOString().split('T')[0];
    document.getElementById('endDate').value = nextWeek.toISOString().split('T')[0];
    
    new bootstrap.Modal(document.getElementById('requestLeaveModal')).show();
}

function viewLeaveDetails(requestId) {
    // Redirect to leave request details page
    window.location.href = `/employee/leave/${requestId}/details/`;
}

function cancelLeaveRequest(requestId) {
    if (confirm('Are you sure you want to cancel this leave request?')) {
        fetch(`/api/leave/${requestId}/cancel/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccessToast('Leave request cancelled successfully!');
                location.reload();
            } else {
                showErrorToast('Error cancelling leave request: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Error cancelling leave request. Please try again.');
        });
    }
}

function refreshLeave() {
    location.reload();
}

function calculateDays() {
    const startDate = new Date(document.getElementById('startDate').value);
    const endDate = new Date(document.getElementById('endDate').value);
    
    if (startDate && endDate && endDate >= startDate) {
        const timeDiff = endDate.getTime() - startDate.getTime();
        const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1; // +1 to include both start and end dates
        document.getElementById('totalDays').value = daysDiff;
    }
}

// Initialize leave management functionality
function initLeaveManagement() {
    console.log('Leave management initialized');
    
    // Calculate total days when dates change
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput) {
        startDateInput.addEventListener('change', calculateDays);
    }
    
    if (endDateInput) {
        endDateInput.addEventListener('change', calculateDays);
    }
    
    // Form submission
    const leaveRequestForm = document.getElementById('leaveRequestForm');
    if (leaveRequestForm) {
        leaveRequestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                leave_type: document.getElementById('leaveType').value,
                start_date: document.getElementById('startDate').value,
                end_date: document.getElementById('endDate').value,
                total_days: document.getElementById('totalDays').value,
                reason: document.getElementById('reason').value,
                emergency_contact: document.getElementById('emergencyContact').value,
                is_urgent: document.getElementById('urgentRequest').checked
            };
            
            // Submit to backend
            fetch('/api/leave/create/', {
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
                    bootstrap.Modal.getInstance(document.getElementById('requestLeaveModal')).hide();
                    showSuccessToast('Leave request submitted successfully!');
                    location.reload();
                } else {
                    showErrorToast('Error submitting leave request: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorToast('Error submitting leave request. Please try again.');
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initLeaveManagement();
});

// Export functions for global access
window.requestLeave = requestLeave;
window.viewLeaveDetails = viewLeaveDetails;
window.cancelLeaveRequest = cancelLeaveRequest;
window.refreshLeave = refreshLeave;
window.calculateDays = calculateDays;
