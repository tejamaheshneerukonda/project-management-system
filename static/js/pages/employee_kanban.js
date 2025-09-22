/**
 * Employee Kanban Board JavaScript
 * Handles drag and drop task management functionality for employees
 */

// Kanban Board Functions
function initializeDragAndDrop() {
    const columns = ['todoColumn', 'inProgressColumn', 'reviewColumn', 'doneColumn'];
    
    columns.forEach(columnId => {
        const column = document.getElementById(columnId);
        
        if (column) {
            column.addEventListener('dragover', function(e) {
                e.preventDefault();
                column.classList.add('drag-over');
            });
            
            column.addEventListener('dragleave', function(e) {
                column.classList.remove('drag-over');
            });
            
            column.addEventListener('drop', function(e) {
                e.preventDefault();
                column.classList.remove('drag-over');
                
                const taskId = e.dataTransfer.getData('text/plain');
                const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
                
                if (taskElement) {
                    column.appendChild(taskElement);
                    updateTaskStatus(taskId, getStatusFromColumn(columnId));
                    updateStatistics();
                }
            });
        }
    });
    
    // Make task cards draggable
    const taskCards = document.querySelectorAll('.task-card');
    taskCards.forEach(card => {
        card.draggable = true;
        card.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.dataset.taskId);
            this.classList.add('dragging');
        });
        
        card.addEventListener('dragend', function(e) {
            this.classList.remove('dragging');
        });
    });
}

function getStatusFromColumn(columnId) {
    const statusMap = {
        'todoColumn': 'TODO',
        'inProgressColumn': 'IN_PROGRESS',
        'reviewColumn': 'REVIEW',
        'doneColumn': 'DONE'
    };
    return statusMap[columnId] || 'TODO';
}

function updateTaskStatus(taskId, status) {
    // Update task status via API
    fetch(`/api/tasks/${taskId}/update-status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Task status updated successfully');
        } else {
            console.error('Error updating task status:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateStatistics() {
    const todoCount = document.getElementById('todoColumn').children.length;
    const inProgressCount = document.getElementById('inProgressColumn').children.length;
    const reviewCount = document.getElementById('reviewColumn').children.length;
    const doneCount = document.getElementById('doneColumn').children.length;
    
    // Update statistics display
    const statsElements = {
        'todoStats': todoCount,
        'inProgressStats': inProgressCount,
        'reviewStats': reviewCount,
        'doneStats': doneCount
    };
    
    Object.entries(statsElements).forEach(([id, count]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = count;
        }
    });
}

function addNewTask() {
    // Open add task modal
    const modal = new bootstrap.Modal(document.getElementById('addTaskModal'));
    modal.show();
}

function editTask(taskId) {
    console.log('Editing task:', taskId);
    // This would open an edit task modal
}

function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        // Delete task via API
        fetch(`/api/tasks/${taskId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskElement) {
                    taskElement.remove();
                    updateStatistics();
                    showSuccessToast('Task deleted successfully!');
                }
            } else {
                showErrorToast('Error deleting task: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Error deleting task. Please try again.');
        });
    }
}

function filterTasks(filter) {
    const taskCards = document.querySelectorAll('.task-card');
    
    taskCards.forEach(card => {
        if (filter === 'all' || card.dataset.priority === filter) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function refreshBoard() {
    location.reload();
}

// Initialize kanban board functionality
function initKanbanBoard() {
    console.log('Kanban board initialized');
    
    // Initialize drag and drop
    initializeDragAndDrop();
    
    // Update statistics
    updateStatistics();
    
    // Set up filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.filter;
            filterTasks(filter);
            
            // Update active button
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initKanbanBoard();
});

// Export functions for global access
window.addNewTask = addNewTask;
window.editTask = editTask;
window.deleteTask = deleteTask;
window.filterTasks = filterTasks;
window.refreshBoard = refreshBoard;
