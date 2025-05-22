from flask import Flask, jsonify, request, render_template

# Create a minimal Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hello')
def hello():
    return jsonify({"message": "Hello, world!"})

@app.route('/ask', methods=['POST'])
def ask():
    return jsonify({"response": "This is a test response"})

if __name__ == '__main__':
    # Make sure debug is enabled
    app.config['DEBUG'] = True
    app.run(host='localhost', port=8888)