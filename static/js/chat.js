document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('chat-icon');
    const chatWindow = document.getElementById('chat-window');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const closeChat = document.getElementById('close-chat');
    
    let socket = io();

    // Toggle chat window
    chatIcon.addEventListener('click', () => {
        chatWindow.classList.toggle('chat-hidden');
        chatIcon.classList.toggle('chat-hidden');
    });

    closeChat.addEventListener('click', () => {
        chatWindow.classList.add('chat-hidden');
        chatIcon.classList.remove('chat-hidden');
    });

    // Send message function
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // Add user message to chat
            addMessage('user', message);
            
            // Send to server
            socket.emit('user_message', {message: message});
            
            // Clear input
            chatInput.value = '';
        }
    }

    // Send message on button click
    sendButton.addEventListener('click', sendMessage);

    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Receive bot response
    socket.on('bot_response', (data) => {
        addMessage('bot', data.message);
    });

    // Add message to chat window
    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', sender);
        
        const content = document.createElement('div');
        content.classList.add('message-content');
        content.textContent = message;
        
        messageDiv.appendChild(content);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add welcome message
    addMessage('bot', 'Hello! I\'m KudumbaBot. How can I help you today?');
});
