/**
 * Employee Team Directory JavaScript
 * Handles team member search, filtering, and communication functionality for employees
 */

// Team Directory Functions
function filterTeamMembers() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const departmentFilter = document.getElementById('departmentFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    
    const teamCards = document.querySelectorAll('.team-member-card');
    
    teamCards.forEach(card => {
        const name = card.querySelector('.member-name').textContent.toLowerCase();
        const department = card.querySelector('.member-department').textContent;
        const status = card.dataset.status;
        
        let show = true;
        
        // Search filter
        if (searchTerm && !name.includes(searchTerm)) {
            show = false;
        }
        
        // Department filter
        if (departmentFilter && department !== departmentFilter) {
            show = false;
        }
        
        // Status filter
        if (statusFilter && status !== statusFilter) {
            show = false;
        }
        
        card.style.display = show ? 'block' : 'none';
    });
    
    updateOnlineCount();
}

function toggleView(view) {
    const container = document.getElementById('teamMembersContainer');
    const cards = container.querySelectorAll('.team-member-card');
    
    if (view === 'grid') {
        cards.forEach(card => {
            card.className = 'col-xl-3 col-lg-4 col-md-6 mb-4 team-member-card';
        });
    } else {
        cards.forEach(card => {
            card.className = 'col-12 mb-3 team-member-card';
        });
    }
    
    // Update active button
    const viewButtons = document.querySelectorAll('.view-toggle-btn');
    viewButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === view) {
            btn.classList.add('active');
        }
    });
}

function updateOnlineCount() {
    const onlineMembers = document.querySelectorAll('.team-member-card[data-status="online"]');
    const onlineCountElement = document.getElementById('onlineCount');
    
    if (onlineCountElement) {
        onlineCountElement.textContent = onlineMembers.length;
    }
}

function sendMessage(memberId) {
    console.log('Sending message to member:', memberId);
    // This would open a messaging interface
    window.location.href = `/employee/messages/compose/?to=${memberId}`;
}

function viewProfile(memberId) {
    console.log('Viewing profile for member:', memberId);
    // This would open a member profile modal
    window.location.href = `/employee/profile/${memberId}/`;
}

function startVideoCall(memberId) {
    console.log('Starting video call with member:', memberId);
    // This would initiate a video call
    window.location.href = `/employee/video-call/${memberId}/`;
}

function addToFavorites(memberId) {
    fetch(`/api/team/favorites/${memberId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const favoriteBtn = document.querySelector(`[data-member-id="${memberId}"] .favorite-btn`);
            if (favoriteBtn) {
                favoriteBtn.innerHTML = '<i class="fas fa-heart text-danger"></i>';
                favoriteBtn.title = 'Remove from favorites';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function removeFromFavorites(memberId) {
    fetch(`/api/team/favorites/${memberId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const favoriteBtn = document.querySelector(`[data-member-id="${memberId}"] .favorite-btn`);
            if (favoriteBtn) {
                favoriteBtn.innerHTML = '<i class="fas fa-heart text-muted"></i>';
                favoriteBtn.title = 'Add to favorites';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function toggleFavorite(memberId) {
    const favoriteBtn = document.querySelector(`[data-member-id="${memberId}"] .favorite-btn`);
    if (favoriteBtn && favoriteBtn.innerHTML.includes('text-danger')) {
        removeFromFavorites(memberId);
    } else {
        addToFavorites(memberId);
    }
}

function filterByDepartment(department) {
    document.getElementById('departmentFilter').value = department;
    filterTeamMembers();
}

function refreshTeamDirectory() {
    location.reload();
}

function showOnlineOnly() {
    const teamCards = document.querySelectorAll('.team-member-card');
    
    teamCards.forEach(card => {
        const status = card.dataset.status;
        card.style.display = status === 'online' ? 'block' : 'none';
    });
    
    updateOnlineCount();
}

function showAllMembers() {
    const teamCards = document.querySelectorAll('.team-member-card');
    
    teamCards.forEach(card => {
        card.style.display = 'block';
    });
    
    updateOnlineCount();
}

// Initialize team directory functionality
function initTeamDirectory() {
    console.log('Team directory initialized');
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterTeamMembers();
        });
    }
    
    // Filter functionality
    const departmentFilter = document.getElementById('departmentFilter');
    if (departmentFilter) {
        departmentFilter.addEventListener('change', filterTeamMembers);
    }
    
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterTeamMembers);
    }
    
    // Initialize online count
    updateOnlineCount();
    
    // Set up view toggle buttons
    const viewButtons = document.querySelectorAll('.view-toggle-btn');
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            toggleView(view);
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTeamDirectory();
});

// Export functions for global access
window.filterTeamMembers = filterTeamMembers;
window.toggleView = toggleView;
window.sendMessage = sendMessage;
window.viewProfile = viewProfile;
window.startVideoCall = startVideoCall;
window.toggleFavorite = toggleFavorite;
window.filterByDepartment = filterByDepartment;
window.refreshTeamDirectory = refreshTeamDirectory;
window.showOnlineOnly = showOnlineOnly;
window.showAllMembers = showAllMembers;
