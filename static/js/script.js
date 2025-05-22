// JavaScript for the Employment Rights chatbot

document.addEventListener('DOMContentLoaded', function() {
    const questionForm = document.getElementById('question-form');
    const userQuestionInput = document.getElementById('user-question');
    const chatMessages = document.getElementById('chat-messages');
    
    console.log("Chat interface initialized");
    
    // Handle form submission
    questionForm.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log("Form submitted");
        
        const userQuestion = userQuestionInput.value.trim();
        if (!userQuestion) {
            console.log("Empty question, ignoring");
            return;
        }
        
        console.log("Sending question:", userQuestion);
        
        // Add user message to chat
        addMessage(userQuestion, 'user');
        
        // Clear input field
        userQuestionInput.value = '';
        
        // Show loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message';
        loadingDiv.innerHTML = '<p>Thinking...</p>';
        chatMessages.appendChild(loadingDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Send the question to our backend - very simplified
        console.log("Sending fetch request to /ask");
        
        // Create a simple JSON object
        const data = JSON.stringify({ question: userQuestion });
        console.log("Request data:", data);
        
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: data
        })
        .then(response => {
            console.log("Received response status:", response.status);
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received data:", data);
            
            // Remove loading message
            chatMessages.removeChild(loadingDiv);
            
            // Add bot response
            if (data.error) {
                console.error("Error:", data.error);
                addMessage('Sorry, I encountered an error: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            
            // Try to remove loading message if it exists
            try {
                chatMessages.removeChild(loadingDiv);
            } catch (e) {
                console.warn("Could not remove loading div:", e);
            }
            
            // Show error message
            addMessage('Sorry, there was a problem connecting to the server: ' + error.message, 'bot');
        });
    });
    
// Function to add a message to the chat
    function addMessage(text, sender) {
        console.log(`Adding ${sender} message:`, text);
        const messageDiv = document.createElement('div');
        messageDiv.className = sender === 'user' ? 'message user-message' : 'message bot-message';
        
        // Handle markdown formatting (basic conversion of **bold** to <strong>bold</strong>)
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format text with paragraphs
        formattedText = formattedText.split('\n').map(line => 
            line ? `<p>${line}</p>` : '<br>'
        ).join('');
        
        messageDiv.innerHTML = formattedText;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the new message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});