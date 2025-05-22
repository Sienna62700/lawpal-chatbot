from flask import Flask, render_template, request, jsonify
import os
import re
import markdown
from dotenv import load_dotenv
import fastapi_poe as fp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API key from environment variable
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BOT_NAME = os.getenv("POE_BOT_NAME", "EmploymentLawHK")

# Print configuration details
print("=== APP CONFIGURATION ===")
print(f"API Key configured: {'Yes' if POE_API_KEY else 'No'}")
print(f"API Key (first 10 chars): {POE_API_KEY[:10] if POE_API_KEY else 'None'}")
print(f"Bot Name: '{POE_BOT_NAME}'")

def clean_response(text):
    """Clean the response text by removing citations and fixing formatting"""
    text = re.sub(r'\[\[[0-9]+\]\]\([^)]+\)', '', text)
    return text

@app.route('/')
def home():
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/debug-config')
def debug_config():
    """Debug endpoint to see exactly what configuration is being used"""
    return jsonify({
        "bot_name": POE_BOT_NAME,
        "api_key_configured": bool(POE_API_KEY),
        "api_key_first_10": POE_API_KEY[:10] if POE_API_KEY else None,
        "api_key_length": len(POE_API_KEY) if POE_API_KEY else 0,
        "environment_variables": {
            "POE_BOT_NAME": os.getenv("POE_BOT_NAME"),
            "POE_API_KEY_SET": bool(os.getenv("POE_API_KEY"))
        }
    })

@app.route('/ask', methods=['POST'])
def ask_question():
    """Process user questions and return responses from Poe API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        question = data.get('question', '')
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        if not POE_API_KEY:
            return jsonify({"error": "API key not configured"}), 500
        
        print(f"=== PROCESSING QUESTION ===")
        print(f"Question: {question}")
        print(f"Using bot: '{POE_BOT_NAME}'")
        print(f"API key starts with: {POE_API_KEY[:10]}...")
        print(f"API key length: {len(POE_API_KEY)}")
        
        # Create a message using fastapi_poe's ProtocolMessage
        message = fp.ProtocolMessage(role="user", content=question)
        
        try:
            print("Attempting to connect to Poe API...")
            
            # Try to get bot response
            all_partials = list(fp.get_bot_response_sync(
                messages=[message], 
                bot_name=POE_BOT_NAME, 
                api_key=POE_API_KEY
            ))
            
            print(f"Success! Received {len(all_partials)} partial responses")
            
            if all_partials:
                final_response = all_partials[-1]
                
                if hasattr(final_response, 'text'):
                    response_text = final_response.text
                elif hasattr(final_response, 'content'):
                    response_text = final_response.content
                else:
                    response_text = str(final_response)
                
                cleaned_response = clean_response(response_text)
                print(f"Returning cleaned response")
                
                return jsonify({"response": cleaned_response})
            else:
                return jsonify({"response": "I didn't receive a proper response. Please try again."})
            
        except Exception as api_err:
            print(f"=== POE API ERROR ===")
            print(f"Error type: {type(api_err).__name__}")
            print(f"Error message: {str(api_err)}")
            
            # More specific error handling
            error_str = str(api_err).lower()
            
            if "404" in error_str or "not found" in error_str:
                return jsonify({
                    "error": f"Bot '{POE_BOT_NAME}' not found. Please verify:\n"
                            f"1. Bot name is exactly correct: '{POE_BOT_NAME}'\n"
                            f"2. Bot exists in your Poe account\n"
                            f"3. Bot is published/active\n"
                            f"4. API key has permission to access this bot"
                }), 404
            elif "401" in error_str or "unauthorized" in error_str:
                return jsonify({
                    "error": "API key is invalid or expired. Please check your POE_API_KEY."
                }), 401
            elif "403" in error_str or "forbidden" in error_str:
                return jsonify({
                    "error": "API key doesn't have permission to access this bot."
                }), 403
            else:
                return jsonify({
                    "error": f"Poe API error: {str(api_err)}"
                }), 500
            
    except Exception as e:
        print(f"=== GENERAL ERROR ===")
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8888))
    host = '0.0.0.0' if 'PORT' in os.environ else 'localhost'
    debug = 'PORT' not in os.environ
    
    app.run(debug=debug, host=host, port=port)
