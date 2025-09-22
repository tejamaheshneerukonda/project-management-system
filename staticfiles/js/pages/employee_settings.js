/**
 * Employee Settings JavaScript
 * Handles settings management and personalization functionality for employees
 */

// Settings Management Functions
function saveAllSettings() {
    const settings = {
        dashboard: {
            theme: document.getElementById('themeSelect').value,
            layout: document.getElementById('layoutSelect').value,
            widgets: getSelectedWidgets(),
            auto_refresh: document.getElementById('autoRefresh').checked,
            refresh_interval: parseInt(document.getElementById('refreshInterval').value)
        },
        notifications: {
            email_notifications: document.getElementById('emailNotifications').checked,
            push_notifications: document.getElementById('pushNotifications').checked,
            task_reminders: document.getElementById('taskReminders').checked,
            deadline_alerts: document.getElementById('deadlineAlerts').checked,
            meeting_reminders: document.getElementById('meetingReminders').checked
        },
        privacy: {
            profile_visibility: document.getElementById('profileVisibility').value,
            activity_status: document.getElementById('activityStatus').checked,
            location_sharing: document.getElementById('locationSharing').checked
        },
        preferences: {
            language: document.getElementById('languageSelect').value,
            timezone: document.getElementById('timezoneSelect').value,
            date_format: document.getElementById('dateFormat').value,
            time_format: document.getElementById('timeFormat').value
        }
    };
    
    fetch('/api/settings/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessToast('Settings saved successfully!');
        } else {
            showErrorToast('Error saving settings: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorToast('Error saving settings. Please try again.');
    });
}

function getSelectedWidgets() {
    const widgets = [];
    const widgetCheckboxes = document.querySelectorAll('input[name="dashboardWidgets"]:checked');
    widgetCheckboxes.forEach(checkbox => {
        widgets.push(checkbox.value);
    });
    return widgets;
}

function resetToDefaults() {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
        fetch('/api/settings/reset/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccessToast('Settings reset to defaults successfully!');
                location.reload();
            } else {
                showErrorToast('Error resetting settings: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Error resetting settings. Please try again.');
        });
    }
}

function exportSettings() {
    const settings = {
        dashboard: {
            theme: document.getElementById('themeSelect').value,
            layout: document.getElementById('layoutSelect').value,
            widgets: getSelectedWidgets(),
            auto_refresh: document.getElementById('autoRefresh').checked,
            refresh_interval: parseInt(document.getElementById('refreshInterval').value)
        },
        notifications: {
            email_notifications: document.getElementById('emailNotifications').checked,
            push_notifications: document.getElementById('pushNotifications').checked,
            task_reminders: document.getElementById('taskReminders').checked,
            deadline_alerts: document.getElementById('deadlineAlerts').checked,
            meeting_reminders: document.getElementById('meetingReminders').checked
        },
        privacy: {
            profile_visibility: document.getElementById('profileVisibility').value,
            activity_status: document.getElementById('activityStatus').checked,
            location_sharing: document.getElementById('locationSharing').checked
        },
        preferences: {
            language: document.getElementById('languageSelect').value,
            timezone: document.getElementById('timezoneSelect').value,
            date_format: document.getElementById('dateFormat').value,
            time_format: document.getElementById('timeFormat').value
        }
    };
    
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'settings-backup.json';
    link.click();
    
    URL.revokeObjectURL(url);
}

function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const settings = JSON.parse(e.target.result);
                    applyImportedSettings(settings);
                } catch (error) {
                    showErrorToast('Error reading settings file. Please make sure it\'s a valid JSON file.');
                }
            };
            reader.readAsText(file);
        }
    };
    
    input.click();
}

function applyImportedSettings(settings) {
    // Apply imported settings to form fields
    if (settings.dashboard) {
        if (settings.dashboard.theme) document.getElementById('themeSelect').value = settings.dashboard.theme;
        if (settings.dashboard.layout) document.getElementById('layoutSelect').value = settings.dashboard.layout;
        if (settings.dashboard.auto_refresh !== undefined) document.getElementById('autoRefresh').checked = settings.dashboard.auto_refresh;
        if (settings.dashboard.refresh_interval) document.getElementById('refreshInterval').value = settings.dashboard.refresh_interval;
    }
    
    if (settings.notifications) {
        if (settings.notifications.email_notifications !== undefined) document.getElementById('emailNotifications').checked = settings.notifications.email_notifications;
        if (settings.notifications.push_notifications !== undefined) document.getElementById('pushNotifications').checked = settings.notifications.push_notifications;
        if (settings.notifications.task_reminders !== undefined) document.getElementById('taskReminders').checked = settings.notifications.task_reminders;
        if (settings.notifications.deadline_alerts !== undefined) document.getElementById('deadlineAlerts').checked = settings.notifications.deadline_alerts;
        if (settings.notifications.meeting_reminders !== undefined) document.getElementById('meetingReminders').checked = settings.notifications.meeting_reminders;
    }
    
    if (settings.privacy) {
        if (settings.privacy.profile_visibility) document.getElementById('profileVisibility').value = settings.privacy.profile_visibility;
        if (settings.privacy.activity_status !== undefined) document.getElementById('activityStatus').checked = settings.privacy.activity_status;
        if (settings.privacy.location_sharing !== undefined) document.getElementById('locationSharing').checked = settings.privacy.location_sharing;
    }
    
    if (settings.preferences) {
        if (settings.preferences.language) document.getElementById('languageSelect').value = settings.preferences.language;
        if (settings.preferences.timezone) document.getElementById('timezoneSelect').value = settings.preferences.timezone;
        if (settings.preferences.date_format) document.getElementById('dateFormat').value = settings.preferences.date_format;
        if (settings.preferences.time_format) document.getElementById('timeFormat').value = settings.preferences.time_format;
    }
    
    showSuccessToast('Settings imported successfully! Click "Save All Settings" to apply them.');
}

function previewTheme(theme) {
    // Apply theme preview without saving
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${theme}`);
}

function resetThemePreview() {
    // Reset to current theme
    const currentTheme = document.getElementById('themeSelect').value;
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${currentTheme}`);
}

// Initialize settings functionality
function initSettings() {
    console.log('Settings initialized');
    
    // Initialize settings tabs
    const settingsTabs = document.querySelectorAll('#settingsTabs button[data-bs-toggle="pill"]');
    settingsTabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            console.log('Switched to tab:', event.target.textContent.trim());
        });
    });
    
    // Set up theme preview
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.addEventListener('change', function() {
            previewTheme(this.value);
        });
    }
    
    // Set up auto-save for certain settings
    const autoSaveElements = document.querySelectorAll('[data-auto-save="true"]');
    autoSaveElements.forEach(element => {
        element.addEventListener('change', function() {
            saveAllSettings();
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSettings();
});

// Export functions for global access
window.saveAllSettings = saveAllSettings;
window.resetToDefaults = resetToDefaults;
window.exportSettings = exportSettings;
window.importSettings = importSettings;
window.previewTheme = previewTheme;
window.resetThemePreview = resetThemePreview;
