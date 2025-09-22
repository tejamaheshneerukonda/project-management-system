/**
 * Employee Projects JavaScript
 * Handles project management functionality for employees
 */

// Project Management Functions
function viewProjectTasks(projectId) {
    // Redirect to tasks page with project filter
    window.location.href = `/employee/tasks/?project=${projectId}`;
}

function viewProjectDetails(projectId) {
    // Open project details modal or redirect to project details page
    window.location.href = `/employee/projects/${projectId}/details/`;
}

function refreshProjects() {
    location.reload();
}

// Initialize project management functionality
function initProjectManagement() {
    console.log('Project management initialized');
    
    // Add any additional initialization code here
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initProjectManagement();
});

// Export functions for global access
window.viewProjectTasks = viewProjectTasks;
window.viewProjectDetails = viewProjectDetails;
window.refreshProjects = refreshProjects;
