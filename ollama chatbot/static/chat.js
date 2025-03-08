document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.getElementById('chatWidget');
    const toggleChat = document.getElementById('toggleChat');
    const chatMessages = document.getElementById('chatMessages');
    const userQuestion = document.getElementById('userQuestion');
    const sendQuestion = document.getElementById('sendQuestion');

    // Toggle chat visibility
    toggleChat.addEventListener('click', function() {
        chatWidget.classList.toggle('chat-minimized');
        toggleChat.textContent = chatWidget.classList.contains('chat-minimized') ? '+' : '−';
    });

    // Send question when button is clicked
    sendQuestion.addEventListener('click', sendUserQuestion);

    // Send question when Enter key is pressed
    userQuestion.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendUserQuestion();
        }
    });

    function sendUserQuestion() {
        const question = userQuestion.value.trim();
        if (!question) return;

        // Add user message to chat
        addMessage(question, 'user-message');
        
        // Clear input
        userQuestion.value = '';
        
        // Add loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message';
        loadingDiv.innerHTML = '<div class="loading"></div>';
        chatMessages.appendChild(loadingDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Send to backend
        const formData = new FormData();
        formData.append('question', question);

        fetch('/ask', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            chatMessages.removeChild(loadingDiv);
            
            // Add bot response
            addMessage(data.answer, 'bot-message');
        })
        .catch(error => {
            // Remove loading indicator
            chatMessages.removeChild(loadingDiv);
            
            // Add error message
            addMessage('Sorry, an error occurred. Please try again.', 'bot-message');
            console.error('Error:', error);
        });
    }

    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + className;
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});