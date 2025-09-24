// Employee Chat JavaScript Functionality

// Global variables
let chatSocket = null;
let pollingInterval = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let processedMessageIds = new Set();

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Clear form on page load to prevent persistence
    clearForm();
    
    // Initialize chat functionality
    scrollToBottom();
    initChatWebSocket();
    
    // Setup form handlers
    setupFormHandlers();
    
    // Keep WebSocket alive
    setInterval(() => {
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({type: 'ping'}));
        }
    }, 30000);
});

// Clear form to prevent message persistence
function clearForm() {
    const messageInput = document.getElementById('messageInput');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    
    if (messageInput) {
        messageInput.value = '';
    }
    if (fileInput) {
        fileInput.value = '';
    }
    if (filePreview) {
        filePreview.style.display = 'none';
    }
}

// Auto-scroll to bottom of messages
function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

// Initialize WebSocket connection
function initChatWebSocket() {
    // Get room ID from the page
    const roomIdElement = document.querySelector('[data-room-id]');
    if (!roomIdElement) {
        console.error('Room ID not found');
        startPolling();
        return;
    }
    
    const roomId = roomIdElement.getAttribute('data-room-id');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/room/${roomId}/`;
    
    console.log('Attempting to connect to WebSocket:', wsUrl);
    
    try {
        chatSocket = new WebSocket(wsUrl);
        
        chatSocket.onopen = function(e) {
            console.log('✅ Chat WebSocket connected successfully');
            reconnectAttempts = 0;
            if (pollingInterval) {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }
            // Show connection status to user
            showConnectionStatus('Connected', 'success');
        };
        
        chatSocket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                if (data.type === 'new_message') {
                    addNewMessage(data.message, data.sender, data.timestamp);
                } else if (data.type === 'pong') {
                    // Handle ping-pong for connection keep-alive
                    console.log('WebSocket ping-pong successful');
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        chatSocket.onclose = function(e) {
            console.log('❌ Chat WebSocket disconnected. Code:', e.code, 'Reason:', e.reason);
            showConnectionStatus('Disconnected - Using polling', 'warning');
            startPolling();
            
            // Attempt to reconnect only if it wasn't a manual close
            if (e.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
                console.log(`Attempting to reconnect... (${reconnectAttempts + 1}/${maxReconnectAttempts})`);
                setTimeout(() => {
                    reconnectAttempts++;
                    initChatWebSocket();
                }, 3000);
            } else if (reconnectAttempts >= maxReconnectAttempts) {
                console.log('Max reconnection attempts reached. Using polling only.');
                showConnectionStatus('Connection failed - Using polling', 'danger');
            }
        };
        
        chatSocket.onerror = function(e) {
            console.error('❌ Chat WebSocket error:', e);
            showConnectionStatus('Connection error - Using polling', 'danger');
            startPolling();
        };
    } catch (error) {
        console.error('Error initializing WebSocket:', error);
        showConnectionStatus('WebSocket not supported - Using polling', 'info');
        startPolling();
    }
}

// Show connection status to user
function showConnectionStatus(message, type) {
    // Remove existing status if any
    const existingStatus = document.getElementById('connectionStatus');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // Create status indicator
    const statusDiv = document.createElement('div');
    statusDiv.id = 'connectionStatus';
    statusDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    statusDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    statusDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'danger' ? 'times-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(statusDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (statusDiv && statusDiv.parentNode) {
            statusDiv.remove();
        }
    }, 5000);
}

// Add new message to the chat
function addNewMessage(message, sender, timestamp) {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;
    
    // Prevent duplicate messages
    const messageId = message.id;
    if (messageId && processedMessageIds.has(messageId)) {
        return;
    }
    if (messageId) {
        processedMessageIds.add(messageId);
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message-item mb-3';
    messageElement.setAttribute('data-message-id', messageId);
    
    const senderInitials = sender.first_name.charAt(0) + sender.last_name.charAt(0);
    const formattedTime = new Date(timestamp).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    let attachmentHtml = '';
    if (message.attachment) {
        const fileName = message.attachment_name || message.attachment.split('/').pop();
        const fileExtension = fileName.split('.').pop().toLowerCase();
        const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(fileExtension);
        
        if (isImage) {
            attachmentHtml = `
                <div class="attachment mt-2">
                    <div class="image-attachment">
                        <img src="${message.attachment}" alt="${fileName}" 
                             class="img-thumbnail attachment-image"
                             onclick="openImageModal('${message.attachment}', '${fileName}')">
                        <div class="attachment-actions mt-2">
                            <a href="${message.attachment}" download="${fileName}" 
                               class="btn btn-sm btn-outline-primary me-2">
                                <i class="fas fa-download me-1"></i>Download
                            </a>
                            <a href="${message.attachment}" target="_blank" 
                               class="btn btn-sm btn-outline-secondary">
                                <i class="fas fa-external-link-alt me-1"></i>View Full Size
                            </a>
                        </div>
                    </div>
                </div>
            `;
        } else {
            let fileIcon = 'fas fa-file';
            let iconColor = 'text-muted';
            
            if (fileExtension === 'pdf') {
                fileIcon = 'fas fa-file-pdf';
                iconColor = 'text-danger';
            } else if (['doc', 'docx'].includes(fileExtension)) {
                fileIcon = 'fas fa-file-word';
                iconColor = 'text-primary';
            } else if (['xls', 'xlsx'].includes(fileExtension)) {
                fileIcon = 'fas fa-file-excel';
                iconColor = 'text-success';
            } else if (['ppt', 'pptx'].includes(fileExtension)) {
                fileIcon = 'fas fa-file-powerpoint';
                iconColor = 'text-warning';
            } else if (fileExtension === 'txt') {
                fileIcon = 'fas fa-file-alt';
                iconColor = 'text-info';
            } else if (['zip', 'rar', '7z'].includes(fileExtension)) {
                fileIcon = 'fas fa-file-archive';
                iconColor = 'text-secondary';
            }
            
            attachmentHtml = `
                <div class="attachment mt-2">
                    <div class="file-attachment">
                        <div class="d-flex align-items-center p-2 border rounded bg-light">
                            <div class="flex-shrink-0 me-3">
                                <i class="${fileIcon} fa-2x ${iconColor}"></i>
                            </div>
                            <div class="flex-grow-1">
                                <div class="fw-bold">${fileName.length > 30 ? fileName.substring(0, 30) + '...' : fileName}</div>
                                <small class="text-muted">File attachment</small>
                            </div>
                            <div class="flex-shrink-0">
                                <a href="${message.attachment}" download="${fileName}" 
                                   class="btn btn-sm btn-primary me-2">
                                    <i class="fas fa-download me-1"></i>Download
                                </a>
                                <a href="${message.attachment}" target="_blank" 
                                   class="btn btn-sm btn-outline-secondary">
                                    <i class="fas fa-external-link-alt me-1"></i>Open
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    messageElement.innerHTML = `
        <div class="d-flex align-items-start">
            <div class="flex-shrink-0">
                <div class="avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" 
                     style="width: 40px; height: 40px;">
                    ${senderInitials}
                </div>
            </div>
            <div class="flex-grow-1 ms-3">
                <div class="d-flex justify-content-between align-items-start">
                    <h6 class="mb-1">
                        ${sender.first_name} ${sender.last_name}
                        ${message.is_edited ? '<small class="text-muted">(edited)</small>' : ''}
                    </h6>
                    <small class="text-muted">${formattedTime}</small>
                </div>
                <p class="mb-1">${message.content}</p>
                ${attachmentHtml}
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageElement);
    scrollToBottom();
}

// Start polling for new messages
function startPolling() {
    if (pollingInterval) return;
    
    pollingInterval = setInterval(() => {
        fetch(window.location.href + '?ajax=1&last_message=' + getLastMessageId())
            .then(response => response.json())
            .then(data => {
                if (data.success && data.new_messages) {
                    data.new_messages.forEach(msg => {
                        addNewMessage(msg.message, msg.sender, msg.timestamp);
                    });
                }
            })
            .catch(error => {
                console.error('Error checking for new messages:', error);
            });
    }, 3000);
}

// Get the ID of the last message
function getLastMessageId() {
    const messages = document.querySelectorAll('.message-item');
    if (messages.length === 0) return 0;
    
    const lastMessage = messages[messages.length - 1];
    return lastMessage.getAttribute('data-message-id') || 0;
}

// Setup form event handlers
function setupFormHandlers() {
    // File input handling
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileName = document.getElementById('fileName');
                const filePreview = document.getElementById('filePreview');
                
                if (fileName) fileName.textContent = file.name;
                if (filePreview) filePreview.style.display = 'block';
            }
        });
    }
    
    // Message form submission
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const messageInput = document.getElementById('messageInput');
            const submitButton = this.querySelector('button[type="submit"]');
            
            if (!messageInput.value.trim() && !formData.get('attachment')) {
                alert('Please enter a message or attach a file');
                return;
            }
            
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageInput.value = '';
                    clearFile();
                    // Prevent form persistence
                    messageForm.reset();
                } else {
                    alert('Error sending message: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error sending message. Please try again.');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            });
        });
    }
}

// Clear file selection
function clearFile() {
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    
    if (fileInput) fileInput.value = '';
    if (filePreview) filePreview.style.display = 'none';
}

// Image modal functionality
function openImageModal(imageUrl, fileName) {
    let modal = document.getElementById('imageModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'imageModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${fileName}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${imageUrl}" alt="${fileName}" class="img-fluid" style="max-height: 70vh;">
                    </div>
                    <div class="modal-footer">
                        <a href="${imageUrl}" download="${fileName}" class="btn btn-primary">
                            <i class="fas fa-download me-1"></i>Download
                        </a>
                        <a href="${imageUrl}" target="_blank" class="btn btn-outline-secondary">
                            <i class="fas fa-external-link-alt me-1"></i>Open in New Tab
                        </a>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    } else {
        modal.querySelector('.modal-title').textContent = fileName;
        modal.querySelector('.modal-body img').src = imageUrl;
        modal.querySelector('.modal-body img').alt = fileName;
        modal.querySelector('a[download]').href = imageUrl;
        modal.querySelector('a[download]').download = fileName;
        modal.querySelector('a[target="_blank"]').href = imageUrl;
    }
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}
