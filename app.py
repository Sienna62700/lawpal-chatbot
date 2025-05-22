from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get Poe API key from environment variable
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BOT_NAME = os.getenv("POE_BOT_NAME", "your-bot-name")  # Your Poe bot name

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/test')
def test():
    """Render the test page"""
    return render_template('test.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Process user questions and get responses from Poe API"""
    if not POE_API_KEY:
        return jsonify({"error": "API key not configured"}), 500
    
    # Get the question from the request
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    # This is a simplified example - you'll need to implement 
    # the actual Poe API integration based on their documentation
    try:
        # Replace this with actual Poe API call
        # This is a placeholder for the Poe API request
        response = requests.post(
            f"https://api.poe.com/bot/{POE_BOT_NAME}/message",
            headers={
                "Authorization": f"Bearer {POE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"message": question}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            bot_response = response.json().get("text", "Sorry, I couldn't get a response.")
            return jsonify({"response": bot_response})
        else:
            return jsonify({"error": f"API error: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500


if __name__ == '__main__':
    # Use a high port and specify host as localhost
    app.run(debug=True, host='localhost', port=8888)