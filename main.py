import os
import json
import mockai
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def gen():
    try:
        data = request.get_json() or {}
        prompt = data.get("prompt", "random mock data")
        messages = data.get("messages", [])  # Receive messages list
        mock_type = request.headers.get("X-MockType", "json")
        return jsonify(mockai.generate(prompt, mock_type, messages))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)