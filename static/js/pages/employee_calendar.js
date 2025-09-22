/**
 * Employee Calendar JavaScript
 * Handles calendar functionality and event management for employees
 */

// Calendar variables
let calendar;
let currentView = 'month';
let currentDate = new Date();

// Calendar Functions
function initializeCalendar() {
    const calendarEl = document.getElementById('calendarContainer');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: false, // We're using custom header
        height: 'auto',
        events: [
            // Sample events - in real implementation, these would come from the backend
            {
                title: 'Team Meeting',
                start: '2024-09-25T10:00:00',
                end: '2024-09-25T11:00:00',
                color: '#007bff',
                type: 'meeting'
            },
            {
                title: 'Project Deadline',
                start: '2024-09-30',
                color: '#dc3545',
                type: 'deadline'
            },
            {
                title: 'Leave Request',
                start: '2024-09-28',
                end: '2024-09-30',
                color: '#28a745',
                type: 'leave'
            }
        ],
        eventClick: function(info) {
            viewEventDetails(info.event);
        },
        dateClick: function(info) {
            addNewEvent(info.dateStr);
        },
        eventDrop: function(info) {
            updateEventDate(info.event);
        },
        eventResize: function(info) {
            updateEventDuration(info.event);
        }
    });
    
    calendar.render();
    updateCalendarHeader();
}

function updateCalendarHeader() {
    const headerTitle = document.getElementById('calendarTitle');
    if (headerTitle) {
        const date = calendar.getDate();
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        headerTitle.textContent = `${monthNames[date.getMonth()]} ${date.getFullYear()}`;
    }
}

function changeView(view) {
    currentView = view;
    calendar.changeView(view);
    updateViewButtons();
}

function updateViewButtons() {
    const viewButtons = document.querySelectorAll('.view-btn');
    viewButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === currentView) {
            btn.classList.add('active');
        }
    });
}

function navigateCalendar(direction) {
    if (direction === 'prev') {
        calendar.prev();
    } else if (direction === 'next') {
        calendar.next();
    } else if (direction === 'today') {
        calendar.today();
    }
    updateCalendarHeader();
}

function addNewEvent(dateStr = null) {
    const eventData = {
        title: prompt('Event title:') || 'New Event',
        start: dateStr || new Date().toISOString().split('T')[0],
        color: '#007bff'
    };
    
    calendar.addEvent(eventData);
    
    // In a real implementation, this would save to the backend
    console.log('New event added:', eventData);
}

function viewEventDetails(event) {
    const eventInfo = {
        title: event.title,
        start: event.start.toISOString(),
        end: event.end ? event.end.toISOString() : null,
        color: event.color
    };
    
    showInfoToast(`Event: ${eventInfo.title}\nStart: ${new Date(eventInfo.start).toLocaleString()}\nEnd: ${eventInfo.end ? new Date(eventInfo.end).toLocaleString() : 'All day'}`);
}

function updateEventDate(event) {
    console.log('Event date updated:', event.title, 'to', event.start.toISOString());
    // This would update the event date in the backend
}

function updateEventDuration(event) {
    console.log('Event duration updated:', event.title, 'from', event.start.toISOString(), 'to', event.end.toISOString());
    // This would update the event duration in the backend
}

function filterEvents(filter) {
    const events = calendar.getEvents();
    
    events.forEach(event => {
        if (filter === 'all' || event.extendedProps.type === filter) {
            event.setProp('display', 'block');
        } else {
            event.setProp('display', 'none');
        }
    });
}

function exportCalendar() {
    const events = calendar.getEvents();
    const exportData = events.map(event => ({
        title: event.title,
        start: event.start.toISOString(),
        end: event.end ? event.end.toISOString() : null,
        type: event.extendedProps.type || 'general'
    }));
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'calendar-events.json';
    link.click();
    
    URL.revokeObjectURL(url);
}

function refreshCalendar() {
    location.reload();
}

// Initialize calendar functionality
function initCalendar() {
    console.log('Calendar initialized');
    
    // Initialize calendar
    initializeCalendar();
    
    // Set up navigation buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const direction = this.dataset.direction;
            navigateCalendar(direction);
        });
    });
    
    // Set up view buttons
    const viewButtons = document.querySelectorAll('.view-btn');
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            changeView(view);
        });
    });
    
    // Set up filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.filter;
            filterEvents(filter);
            
            // Update active button
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCalendar();
});

// Export functions for global access
window.changeView = changeView;
window.navigateCalendar = navigateCalendar;
window.addNewEvent = addNewEvent;
window.viewEventDetails = viewEventDetails;
window.filterEvents = filterEvents;
window.exportCalendar = exportCalendar;
window.refreshCalendar = refreshCalendar;
