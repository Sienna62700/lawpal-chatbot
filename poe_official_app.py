from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import fastapi_poe as fp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API key from environment variable
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BOT_NAME = os.getenv("POE_BOT_NAME")

# Print configuration details
print("=== APP CONFIGURATION ===")
print(f"API Key configured: {'Yes' if POE_API_KEY else 'No'}")
print(f"Bot Name: {POE_BOT_NAME}")

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
            print("Bot name not specified, using default Claude model")
            bot_name = "Claude-3-opus-20240229"  # Default to Claude if no bot name
        else:
            bot_name = POE_BOT_NAME
        
        print(f"Querying Poe bot: {bot_name}")
        
        # Create a message using fastapi_poe's ProtocolMessage
        message = fp.ProtocolMessage(role="user", content=question)
        
        # Get response from the bot using fastapi_poe
        full_response = ""
        try:
            # Use the synchronous version for simplicity
            for partial in fp.get_bot_response_sync(
                messages=[message], 
                bot_name=bot_name, 
                api_key=POE_API_KEY
            ):
                # Accumulate the response
                if hasattr(partial, 'text'):
                    full_response += partial.text
                elif hasattr(partial, 'content'):
                    full_response += partial.content
                # Print progress for debugging
                print(".", end="", flush=True)
            
            print("\nReceived complete response from Poe API")
            
            # If we got no response, use a fallback
            if not full_response:
                full_response = "I didn't receive a proper response from the AI. Please try again."
            
            return jsonify({"response": full_response})
            
        except Exception as api_err:
            print(f"Poe API error: {str(api_err)}")
            # If the API call fails, use a fallback response with the error
            fallback = f"I encountered an error when trying to get a response: {str(api_err)}"
            return jsonify({"response": fallback})
            
    except Exception as e:
        # Log any other errors
        print(f"Error in /ask: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='localhost', port=8888)