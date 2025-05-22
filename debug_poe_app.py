from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API keys
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BOT_NAME = os.getenv("POE_BOT_NAME")

# Debug information
print("=== APP CONFIGURATION ===")
print(f"API Key configured: {'Yes' if POE_API_KEY else 'No'}")
print(f"Bot Name: {POE_BOT_NAME}")

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
        question = data.get('question', '') if data else ''
        
        print(f"\n=== RECEIVED QUESTION: '{question}' ===")
        
        # Check for missing data
        if not question:
            return jsonify({"error": "No question provided"}), 400
            
        # Check API configuration
        if not POE_API_KEY or not POE_BOT_NAME:
            print("ERROR: Missing API key or bot name")
            return jsonify({"error": "API not fully configured"}), 500
        
        # ===== ATTEMPT 1: Try GraphQL endpoint =====
        try:
            print("\n--- TRYING POE GRAPHQL API ---")
            graphql_url = "https://api.poe.com/gql"
            
            headers = {
                "Authorization": f"Bearer {POE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            graphql_query = {
                "query": """
                mutation SendMessageMutation($bot: String!, $message: String!) {
                  sendMessage(bot: $bot, message: $message) {
                    messageId
                    text
                  }
                }
                """,
                "variables": {
                    "bot": POE_BOT_NAME,
                    "message": question
                }
            }
            
            print(f"Calling GraphQL API with: {json.dumps(graphql_query)[:100]}...")
            graphql_response = requests.post(graphql_url, headers=headers, json=graphql_query, timeout=30)
            
            print(f"GraphQL response status: {graphql_response.status_code}")
            print(f"GraphQL response headers: {dict(graphql_response.headers)}")
            print(f"GraphQL response content: {graphql_response.text[:200]}...")
            
            if graphql_response.status_code == 200:
                try:
                    graphql_data = graphql_response.json()
                    if "data" in graphql_data and "sendMessage" in graphql_data["data"]:
                        bot_response = graphql_data["data"]["sendMessage"].get("text", "")
                        if bot_response:
                            print("SUCCESS: Got response from GraphQL API")
                            return jsonify({"response": bot_response})
                except Exception as json_err:
                    print(f"Error parsing GraphQL response: {str(json_err)}")
        except Exception as graphql_err:
            print(f"GraphQL API attempt failed: {str(graphql_err)}")
            traceback.print_exc()
        
        # ===== ATTEMPT 2: Try REST API endpoint =====
        try:
            print("\n--- TRYING POE REST API ---")
            rest_url = f"https://api.poe.com/bot/{POE_BOT_NAME}/message"
            
            headers = {
                "Authorization": f"Bearer {POE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": question
            }
            
            print(f"Calling REST API with payload: {payload}")
            rest_response = requests.post(rest_url, headers=headers, json=payload, timeout=30)
            
            print(f"REST response status: {rest_response.status_code}")
            print(f"REST response headers: {dict(rest_response.headers)}")
            print(f"REST response content: {rest_response.text[:200]}...")
            
            if rest_response.status_code == 200:
                try:
                    rest_data = rest_response.json()
                    bot_response = rest_data.get("text", "")
                    if bot_response:
                        print("SUCCESS: Got response from REST API")
                        return jsonify({"response": bot_response})
                except Exception as json_err:
                    print(f"Error parsing REST response: {str(json_err)}")
        except Exception as rest_err:
            print(f"REST API attempt failed: {str(rest_err)}")
            traceback.print_exc()
        
        # ===== FALLBACK: Provide a temporary response =====
        print("\n--- BOTH API ATTEMPTS FAILED, USING FALLBACK ---")
        
        # Training data sample: some employment harassment information for testing
        training_data = {
            "bitch": "If your employer called you offensive names like 'bitch', this could constitute workplace harassment. Under employment laws in many jurisdictions, this may be classified as creating a hostile work environment, especially if it's part of a pattern. You should: 1) Document the incident with date, time, and context, 2) Report it to HR or management following your company's procedure, 3) Consider filing a complaint with your local employment authority if the issue isn't addressed internally."
        }
        
        # Check if any keywords match our training data
        for keyword, response in training_data.items():
            if keyword.lower() in question.lower():
                print(f"Using training data match for keyword: {keyword}")
                return jsonify({"response": response})
        
        # If no keyword matches, use general fallback
        fallback = f"I'm sorry, but I couldn't connect to my knowledge base right now. Your question was about '{question}'. Generally, employment rights cover areas like workplace harassment, discrimination, fair pay, working hours, and termination procedures. Please try asking again later or consult a legal professional for specific advice."
        return jsonify({"response": fallback})
            
    except Exception as e:
        print("\n=== UNCAUGHT EXCEPTION ===")
        print(str(e))
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8888)