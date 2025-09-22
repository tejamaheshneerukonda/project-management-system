/**
 * Employee Gamification JavaScript
 * Handles achievements, points, and leaderboard functionality for employees
 */

// Gamification Functions
function animateAchievements() {
    const achievementCards = document.querySelectorAll('.achievement-icon');
    
    achievementCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.animation = 'bounceIn 0.6s ease-in-out';
        }, index * 100);
    });
}

function shareAchievements() {
    // Implement sharing functionality
    if (navigator.share) {
        navigator.share({
            title: 'My Achievements',
            text: `I've earned ${document.querySelector('.h5').textContent} points and ${document.querySelectorAll('.achievement-icon').length} achievements!`,
            url: window.location.href
        });
    } else {
        // Fallback for browsers that don't support Web Share API
        const text = `I've earned ${document.querySelector('.h5').textContent} points and ${document.querySelectorAll('.achievement-icon').length} achievements!`;
        navigator.clipboard.writeText(text).then(() => {
            showSuccessToast('Achievement text copied to clipboard!');
        });
    }
}

function viewLeaderboard() {
    // Show leaderboard modal or redirect to leaderboard page
    console.log('Viewing leaderboard');
    // This would open a leaderboard modal
}

function claimReward(rewardId) {
    if (confirm('Are you sure you want to claim this reward?')) {
        // Claim reward via API
        fetch(`/api/rewards/${rewardId}/claim/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccessToast('Reward claimed successfully!');
                location.reload();
            } else {
                showErrorToast('Error claiming reward: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Error claiming reward. Please try again.');
        });
    }
}

function viewAchievementDetails(achievementId) {
    console.log('Viewing achievement details:', achievementId);
    // This would open an achievement details modal
}

function filterAchievements(filter) {
    const achievementCards = document.querySelectorAll('.achievement-card');
    
    achievementCards.forEach(card => {
        if (filter === 'all' || card.dataset.category === filter) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function refreshGamification() {
    location.reload();
}

function showProgressAnimation() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach((bar, index) => {
        setTimeout(() => {
            const width = bar.dataset.width || '0%';
            bar.style.width = width;
            bar.style.transition = 'width 1s ease-in-out';
        }, index * 200);
    });
}

function updatePointsDisplay() {
    // Animate points counter
    const pointsElement = document.querySelector('.points-display');
    if (pointsElement) {
        const targetPoints = parseInt(pointsElement.dataset.points) || 0;
        let currentPoints = 0;
        const increment = Math.ceil(targetPoints / 50);
        
        const counter = setInterval(() => {
            currentPoints += increment;
            if (currentPoints >= targetPoints) {
                currentPoints = targetPoints;
                clearInterval(counter);
            }
            pointsElement.textContent = currentPoints.toLocaleString();
        }, 50);
    }
}

// Initialize gamification functionality
function initGamification() {
    console.log('Gamification initialized');
    
    // Add animation to achievement cards
    animateAchievements();
    
    // Show progress animations
    showProgressAnimation();
    
    // Update points display
    updatePointsDisplay();
    
    // Set up filter buttons
    const filterButtons = document.querySelectorAll('.achievement-filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.filter;
            filterAchievements(filter);
            
            // Update active button
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initGamification();
});

// Export functions for global access
window.shareAchievements = shareAchievements;
window.viewLeaderboard = viewLeaderboard;
window.claimReward = claimReward;
window.viewAchievementDetails = viewAchievementDetails;
window.filterAchievements = filterAchievements;
window.refreshGamification = refreshGamification;
