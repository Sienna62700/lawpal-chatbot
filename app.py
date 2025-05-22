from flask import Flask, render_template, request, jsonify, session
import os
import re
import markdown
from dotenv import load_dotenv
import fastapi_poe as fp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # For session management

# Get API key from environment variable
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BOT_NAME = os.getenv("POE_BOT_NAME", "EmploymentLawHK")

# Print configuration details
print("=== APP CONFIGURATION ===")
print(f"API Key configured: {'Yes' if POE_API_KEY else 'No'}")
print(f"Bot Name: {POE_BOT_NAME}")

def clean_response(text):
    """Clean the response text by removing citations and fixing formatting"""
    # Remove citation links like [[3]](https://poe.com/citation?message_id=17477466721405625253&citation=3)
    text = re.sub(r'\[\[[0-9]+\]\]\([^)]+\)', '', text)
    
    # Convert markdown to HTML for proper formatting
    html_text = markdown.markdown(text, extensions=['markdown.extensions.nl2br'])
    return html_text

@app.route('/')
def home():
    # Use template from templates folder
    return render_template('index.html')

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    session.pop('conversation', None)
    return jsonify({"status": "Conversation cleared"})

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
        
        # Get conversation history from session
        if 'conversation' not in session:
            session['conversation'] = []
            
        # Fix any existing assistant roles to bot roles (for backwards compatibility)
        for msg in session['conversation']:
            if msg.get('role') == 'assistant':
                msg['role'] = 'bot'
            
        print(f"Current conversation length: {len(session['conversation'])}")
        
        # Add the new user message
        session['conversation'].append({"role": "user", "content": question})
        print(f"Added user message, new length: {len(session['conversation'])}")
        
        # Create message list for Poe API (include conversation history)
        messages = []
        for i, msg in enumerate(session['conversation']):
            print(f"Message {i}: {msg['role']} - {msg['content'][:50]}...")
            messages.append(fp.ProtocolMessage(role=msg["role"], content=msg["content"]))
        
        print(f"Sending {len(messages)} messages to Poe API")
        
        try:
            # Use the synchronous version with full conversation history
            all_partials = list(fp.get_bot_response_sync(
                messages=messages,  # Send full conversation history
                bot_name=POE_BOT_NAME, 
                api_key=POE_API_KEY
            ))
            
            print(f"Received {len(all_partials)} partial responses")
            
            # Get only the final response (last element in the list)
            if all_partials:
                final_response = all_partials[-1]
                print(f"Final response type: {type(final_response)}")
                
                # Extract the text from the response
                if hasattr(final_response, 'text'):
                    response_text = final_response.text
                    print(f"Using .text: {response_text[:100]}...")
                elif hasattr(final_response, 'content'):
                    response_text = final_response.content
                    print(f"Using .content: {response_text[:100]}...")
                else:
                    response_text = str(final_response)
                    print(f"Using str(): {response_text[:100]}...")
                
                # Clean up the response to remove citations and fix formatting
                cleaned_response = clean_response(response_text)
                
                # Add bot response to conversation history
                session['conversation'].append({"role": "bot", "content": response_text})
                
                # Keep conversation history reasonable (last 20 messages)
                if len(session['conversation']) > 20:
                    session['conversation'] = session['conversation'][-20:]
                
                print(f"Successfully processed response")
                
                return jsonify({"response": cleaned_response})
            else:
                print("No partials received from Poe API")
                return jsonify({"response": "I didn't receive a proper response. Please try again."})
            
        except Exception as api_err:
            print(f"Poe API error: {str(api_err)}")
            print(f"API error type: {type(api_err)}")
            import traceback
            traceback.print_exc()
            
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
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    import os
    # Use PORT environment variable for Railway, fallback to 8888 for local development
    port = int(os.environ.get('PORT', 8888))
    # Use 0.0.0.0 to accept external connections, localhost only works locally
    host = '0.0.0.0' if 'PORT' in os.environ else 'localhost'
    debug = 'PORT' not in os.environ  # Debug mode only when running locally
    
    app.run(debug=debug, host=host, port=port)