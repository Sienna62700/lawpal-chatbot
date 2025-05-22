from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API keys
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BOT_NAME = os.getenv("POE_BOT_NAME")

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Process user questions and return responses from Poe API"""
    try:
        # Get the question from the request
        data = request.get_json()
        
        # Check if data and question exist
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        question = data.get('question', '')
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Check if API key is configured
        if not POE_API_KEY:
            return jsonify({"error": "API key not configured"}), 500
            
        # Check if bot name is configured
        if not POE_BOT_NAME:
            return jsonify({"error": "Bot name not configured"}), 500
        
        # Try to call the Poe API
        try:
            # This is the Poe API endpoint (may need to be updated based on Poe's documentation)
            url = "https://api.poe.com/api/message"
            
            # Prepare headers with authentication
            headers = {
                "Authorization": f"Bearer {POE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepare the request payload
            payload = {
                "bot": POE_BOT_NAME,
                "message": question
            }
            
            # Make the API request
            print(f"Calling Poe API with bot: {POE_BOT_NAME}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Check the status code
            print(f"Poe API response status: {response.status_code}")
            
            # If the API call was successful
            if response.status_code == 200:
                response_json = response.json()
                print("API response:", response_json)
                
                # Extract the bot's response text
                # Note: The exact structure depends on Poe's API response format
                bot_response = response_json.get("text", "")
                
                # Fall back to a default message if the API didn't return text
                if not bot_response:
                    bot_response = "I received your question but couldn't generate a response. Please try again."
                
                return jsonify({"response": bot_response})
            else:
                # If the API call failed, log the error and return a fallback response
                print(f"API error: {response.status_code}")
                print("Response content:", response.text)
                
                # For now, provide a fallback response so the app doesn't break
                fallback = f"I'm sorry, but I wasn't able to get an answer from my knowledge base. You asked: '{question}'. Please try again later."
                return jsonify({"response": fallback})
                
        except requests.exceptions.RequestException as e:
            # Handle network errors, timeouts, etc.
            print(f"Request error: {str(e)}")
            return jsonify({"error": f"API request error: {str(e)}"}), 500
        
    except Exception as e:
        # Log any other errors
        print(f"Error in /ask: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='localhost', port=8888)