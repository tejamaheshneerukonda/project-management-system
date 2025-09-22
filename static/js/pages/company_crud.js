/* Generic CRUD Operations for Company Dashboard */

// Generic notification function
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Generic delete confirmation function
function confirmDelete(itemType, itemId, itemName, deleteUrl) {
    if (confirm(`Are you sure you want to delete this ${itemType}? This action cannot be undone.`)) {
        fetch(deleteUrl, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`${itemType} "${itemName}" deleted successfully`, 'success');
                // Reload page to show updated list
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification(data.error || `Failed to delete ${itemType}`, 'error');
            }
        })
        .catch(error => {
            showNotification(`Error deleting ${itemType}`, 'error');
        });
    }
}

// Generic view function
function viewItem(itemType, itemId, getUrl, modalTitle) {
    if (!itemId) {
        showNotification(`${itemType} details not available`, 'warning');
        return;
    }
    
    fetch(getUrl, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showItemDetailsModal(data[itemType.toLowerCase()], modalTitle);
        } else {
            showNotification(data.error || `Failed to load ${itemType} details`, 'error');
        }
    })
    .catch(error => {
        showNotification(`Error loading ${itemType} details`, 'error');
    });
}

// Generic edit function
function editItem(itemType, itemId, getUrl, updateUrl, formId) {
    if (!itemId) {
        showNotification(`${itemType} cannot be edited`, 'warning');
        return;
    }
    
    fetch(getUrl, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            populateEditForm(data[itemType.toLowerCase()], formId);
        } else {
            showNotification(data.error || `Failed to load ${itemType} details`, 'error');
        }
    })
    .catch(error => {
        showNotification(`Error loading ${itemType} details`, 'error');
    });
}

// Generic function to show item details modal
function showItemDetailsModal(item, title) {
    const modalHtml = `
        <div class="modal fade" id="itemDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-info-circle me-2"></i>${title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${generateItemDetailsHTML(item)}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if it exists
    const existingModal = document.getElementById('itemDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('itemDetailsModal'));
    modal.show();
}

// Generic function to generate item details HTML
function generateItemDetailsHTML(item) {
    let html = '<div class="row">';
    
    for (const [key, value] of Object.entries(item)) {
        if (key !== 'id' && value !== null && value !== undefined) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            const displayValue = typeof value === 'string' && value.includes('T') && value.includes('Z') 
                ? new Date(value).toLocaleDateString() 
                : value;
            
            html += `
                <div class="col-md-6 mb-3">
                    <h6>${label}</h6>
                    <p class="text-muted">${displayValue || 'Not specified'}</p>
                </div>
            `;
        }
    }
    
    html += '</div>';
    return html;
}

// Generic function to populate edit form
function populateEditForm(item, formId) {
    const form = document.getElementById(formId);
    if (!form) {
        showNotification('Edit form not found', 'error');
        return;
    }
    
    // Populate form fields
    for (const [key, value] of Object.entries(item)) {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) {
            field.value = value || '';
        }
    }
    
    // Change modal title and button text if it's a modal form
    const modal = form.closest('.modal');
    if (modal) {
        const title = modal.querySelector('.modal-title');
        const submitBtn = modal.querySelector('.btn-primary');
        
        if (title) {
            title.innerHTML = '<i class="fas fa-edit me-2"></i>Edit Item';
        }
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-save me-1"></i>Update';
        }
        
        // Store item ID for update
        modal.setAttribute('data-item-id', item.id);
        
        // Show modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

// Generic function to handle form submission (create/update)
function handleFormSubmission(formId, createUrl, updateUrl, itemType) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    // Check if we're editing an existing item
    const modal = form.closest('.modal');
    const itemId = modal ? modal.getAttribute('data-item-id') : null;
    const isEdit = itemId !== null;
    
    // Add loading state
    const submitBtn = form.querySelector('.btn-primary');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>' + (isEdit ? 'Updating...' : 'Adding...');
    submitBtn.disabled = true;
    
    let url, method;
    if (isEdit) {
        url = updateUrl.replace('0', itemId);
        method = 'PUT';
    } else {
        url = createUrl;
        method = 'POST';
    }
    
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        if (data.success) {
            // Close modal if it exists
            if (modal) {
                const bootstrapModal = bootstrap.Modal.getInstance(modal);
                bootstrapModal.hide();
            }
            
            // Show success message
            showNotification(isEdit ? `${itemType} updated successfully!` : `${itemType} added successfully!`, 'success');
            
            // Reset form for next use
            resetForm(form, modal);
            
            // Reload page to show updated list
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Operation failed', 'error');
        }
    })
    .catch(error => {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        showNotification('An error occurred', 'error');
    });
}

// Generic function to reset form
function resetForm(form, modal) {
    // Reset form
    form.reset();
    
    // Reset modal title and button text if it exists
    if (modal) {
        const title = modal.querySelector('.modal-title');
        const submitBtn = modal.querySelector('.btn-primary');
        
        if (title) {
            title.innerHTML = '<i class="fas fa-plus me-2"></i>Add New Item';
        }
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-plus me-1"></i>Add';
        }
        
        // Remove item ID
        modal.removeAttribute('data-item-id');
    }
}

// Initialize page animations
document.addEventListener('DOMContentLoaded', function() {
    // Add staggered animation to cards
    const cards = document.querySelectorAll('.stat-card, .card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add hover effects to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});
