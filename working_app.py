from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API keys (we'll use these later)
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BOT_NAME = os.getenv("POE_BOT_NAME")

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Process user questions and return responses"""
    try:
        # Get the question from the request
        data = request.get_json()
        
        # Check if data and question exist
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        question = data.get('question', '')
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # For now, return a canned response
        # Later we'll integrate with the Poe API
        response = f"You asked: '{question}'. This is a placeholder response. In the future, I'll be able to provide information about employment rights."
        
        return jsonify({"response": response})
        
    except Exception as e:
        # Log any errors (would appear in the terminal)
        print(f"Error in /ask: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='localhost', port=8888)