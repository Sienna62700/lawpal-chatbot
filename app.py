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
POE_BOT_NAME = os.getenv("POE_BOT_NAME", "EmploymentLawHK")  # CHANGED THIS LINE

# Print configuration details
print("=== APP CONFIGURATION ===")
print(f"API Key configured: {'Yes' if POE_API_KEY else 'No'}")
print(f"Bot Name: {POE_BOT_NAME}")

def clean_response(text):
    """Clean the response text by removing citations and fixing formatting"""
    # Remove citation links like [[3]](https://poe.com/citation?message_id=17477466721405625253&citation=3)
    text = re.sub(r'\[\[[0-9]+\]\]\([^)]+\)', '', text)
    
    return text

@app.route('/')
def home():
# Read the HTML file directly from root directory
with open('index.html', 'r') as f:
    return f.read()

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
        
        print(f"Processing question: {question}")
        
        # Create a message using fastapi_poe's ProtocolMessage
        message = fp.ProtocolMessage(role="user", content=question)
        
        try:
            # Use the synchronous version for simplicity
            all_partials = list(fp.get_bot_response_sync(
                messages=[message], 
                bot_name=POE_BOT_NAME, 
                api_key=POE_API_KEY
            ))
            
            # Get only the final response (last element in the list)
            # This avoids concatenating partial streaming responses
            if all_partials:
                final_response = all_partials[-1]
                
                # Extract the text from the response
                if hasattr(final_response, 'text'):
                    response_text = final_response.text
                elif hasattr(final_response, 'content'):
                    response_text = final_response.content
                else:
                    response_text = str(final_response)
                
                # Clean up the response to remove citations and fix formatting
                cleaned_response = clean_response(response_text)
                    
                print(f"Received and cleaned response from Poe API")
                
                return jsonify({"response": cleaned_response})
            else:
                return jsonify({"response": "I didn't receive a proper response. Please try again."})
            
        except Exception as api_err:
            print(f"Poe API error: {str(api_err)}")
            
            # Local fallback for common employment rights questions
            if "verbal abuse" in question.lower() or "called me" in question.lower() or "insult" in question.lower():
                return jsonify({
                    "response": "In Hong Kong, verbal abuse in the workplace may constitute harassment. "\
                               "Under the Employment Ordinance and the Sex Discrimination Ordinance, employees are "\
                               "protected from harassment and discriminatory treatment. "\
                               "\n\nSteps you can take:\n"\
                               "1. Document all incidents with dates, times, and witnesses\n"\
                               "2. Report the behavior to HR or management\n"\
                               "3. File a complaint with the Equal Opportunities Commission if appropriate\n"\
                               "4. Consider consulting with a labor lawyer for specific advice"
                })
                
            return jsonify({
                "response": f"I encountered an error when trying to get a response from my knowledge base. "\
                           f"As a general guide, the Hong Kong Employment Ordinance covers your basic rights "\
                           f"including contracts, wages, leave, and protection from unfair dismissal. "\
                           f"For specific legal advice, please consult a qualified lawyer."
            })
            
    except Exception as e:
        # Log any other errors
        print(f"Error in /ask: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    import os
    # Use PORT environment variable for Railway, fallback to 8888 for local development
    port = int(os.environ.get('PORT', 8888))
    # Use 0.0.0.0 to accept external connections, localhost only works locally
    host = '0.0.0.0' if 'PORT' in os.environ else 'localhost'
    debug = 'PORT' not in os.environ  # Debug mode only when running locally
    
    app.run(debug=debug, host=host, port=port)