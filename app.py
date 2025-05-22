from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# Read the HTML template
def get_html_template():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Error: index.html not found</h1>
        <p>Please make sure your index.html file is in the same directory as app.py</p>
        """

@app.route('/')
def home():
    html_content = get_html_template()
    return render_template_string(html_content)

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
            
        # Your chatbot logic here
        # For now, using the fallback responses from your original design
        response = get_employment_law_response(question)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_employment_law_response(question):
    """Generate responses for Hong Kong employment law questions"""
    question_lower = question.lower()
    
    # Enhanced responses based on your original design
    if any(word in question_lower for word in ['contract', 'agreement', 'employment contract']):
        return """Employment contracts in Hong Kong should include key terms such as:
• Job title and duties
• Wages and payment method
• Working hours and rest days
• Notice period for termination
• Annual leave entitlement

While written contracts are not mandatory under law, they are highly recommended to avoid disputes."""

    elif any(word in question_lower for word in ['notice', 'termination', 'dismiss', 'fire']):
        return """Notice periods in Hong Kong:
• Minimum 1 month notice (or payment in lieu)
• May be longer if specified in contract
• During probation: typically 7 days or as agreed
• Summary dismissal possible for serious misconduct

The Employment Ordinance provides protection against unreasonable dismissal."""

    elif any(word in question_lower for word in ['leave', 'holiday', 'vacation', 'annual leave']):
        return """Annual leave entitlements in Hong Kong:
• Minimum 7 days after 12 months service
• Increases by 1 day per year of service
• Maximum 14 days after 9+ years
• Must be taken within 12 months after entitlement
• Payment in lieu only allowed in specific circumstances"""

    elif any(word in question_lower for word in ['working hours', 'overtime', 'rest day']):
        return """Working hours in Hong Kong:
• No statutory standard working hours limit
• Rest day: minimum 1 day per 7-day period
• Meal breaks: not less than 30 minutes for shifts over 5 hours
• Overtime rates should be agreed in contract
• The Standard Working Hours Committee made recommendations in 2017"""

    elif any(word in question_lower for word in ['mpf', 'pension', 'provident fund', 'retirement']):
        return """MPF (Mandatory Provident Fund) requirements:
• Both employer and employee contribute 5%
• Based on relevant income ($7,100-$30,000 per month)
• Employees earning less than $7,100 exempt from contribution
• Employer must still contribute for low earners
• Contributions due by 10th of following month"""

    elif any(word in question_lower for word in ['maternity', 'pregnancy', 'paternity']):
        return """Maternity benefits in Hong Kong:
• 14 weeks paid maternity leave
• 80% of average daily wages
• Must give notice and provide medical certificate
• Protection against dismissal during pregnancy/maternity leave
• Paternity leave: 5 days for male employees"""

    elif any(word in question_lower for word in ['sick leave', 'medical', 'illness']):
        return """Sick leave entitlements:
• Paid sickness allowance after 4+ weeks employment
• 2/3 of average daily wages
• Maximum 120 days per 12-month period
• Must provide medical certificate
• Accumulated at rate of 2 paid sick days per month"""

    elif any(word in question_lower for word in ['wages', 'salary', 'pay', 'minimum wage']):
        return """Wage protection in Hong Kong:
• Minimum wage: Currently $40 per hour (subject to review)
• Wages must be paid at least monthly
• Payment within 7 days of due date
• Protection against unauthorized deductions
• Written payment records must be kept"""

    else:
        return """I'm here to help with Hong Kong employment law questions! I can assist with:

📋 Employment contracts and terms
⏰ Working hours and overtime
🏖️ Leave entitlements (annual, sick, maternity)
💰 Wages and MPF contributions  
⚖️ Termination and notice periods
🛡️ Employee rights and protections

Please feel free to ask about any specific employment law issue you're facing. Remember, this is general information only - for specific legal advice, consult a qualified lawyer.

請隨時詢問您面臨的任何具體僱傭法問題。請記住，這只是一般資訊 - 如需具體法律建議，請諮詢合資格的律師。"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=True)