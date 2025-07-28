import os
import json
import mockai
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import db  # db.py file for mongodb

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/yt')
def yt():
    url = request.args.get("url")
    return mockai.ytgen(url)

@app.route('/generate', methods=['POST'])
def gen():
    try:
        data = request.get_json() or {}
        prompt = data.get("prompt", "random mock data")
        messages = data.get("messages", [])
        mock_type = request.headers.get("X-MockType", "json")
        return jsonify(mockai.generate(prompt, mock_type, messages))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== BIRTHDAY REMINDER API ROUTES ======

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    name = data.get("name")
    number = data.get("number")
    password = data.get("password")
    birthday = data.get("birthday")
    if not all([name, number, password, birthday]):
        return jsonify({"error": "Missing required fields"}), 400
    user = db.create_user(name, number, password, birthday)
    if user is None:
        return jsonify({"error": "User already exists"}), 409
    return jsonify({"message": "User created successfully", "user": {"name": user["name"], "number": user["number"], "birthday": user["birthday"]}}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    number = data.get("number")
    password = data.get("password")
    if not number or not password:
        return jsonify({"error": "Missing number or password"}), 400
    user = db.authenticate_user(number, password)
    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401
    user.pop("password", None)
    return jsonify({"message": "Login successful", "user": user})

@app.route('/reminders', methods=['GET'])
def get_reminders():
    number = request.args.get("number")
    if not number:
        return jsonify({"error": "User number required"}), 400
    reminders = db.get_reminders(number)
    return jsonify({"reminders": reminders})

@app.route('/reminders', methods=['POST'])
def add_reminder():
    data = request.get_json() or {}
    user_number = data.get("user_number")
    friend_name = data.get("name")
    friend_number = data.get("number")
    date = data.get("date")
    note = data.get("note", "")
    if not all([user_number, friend_name, friend_number, date]):
        return jsonify({"error": "Missing fields"}), 400
    reminder_id = db.add_reminder(user_number, friend_name, friend_number, date, note)
    if reminder_id is None:
        return jsonify({"error": "Failed to add reminder"}), 500
    return jsonify({"message": "Reminder added", "reminder_id": reminder_id}), 201

@app.route('/reminders/<reminder_id>', methods=['PUT'])
def update_reminder(reminder_id):
    data = request.get_json() or {}
    user_number = data.get("user_number")
    if not user_number:
        return jsonify({"error": "User number required"}), 400
    fields = {k: data.get(k) for k in ['name', 'number', 'date', 'note']}
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    success = db.update_reminder(user_number, reminder_id, **fields)
    if not success:
        return jsonify({"error": "Update failed"}), 404
    return jsonify({"message": "Reminder updated"})

@app.route('/reminders/<reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    user_number = request.args.get("user_number")
    if not user_number:
        return jsonify({"error": "User number required"}), 400
    success = db.delete_reminder(user_number, reminder_id)
    if not success:
        return jsonify({"error": "Delete failed"}), 404
    return jsonify({"message": "Reminder deleted"})

@app.route('/profile/<number>', methods=['GET'])
def get_profile(number):
    user = db.get_user_profile(number)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))  # Use Render's PORT or default to 10000
    app.run(host='0.0.0.0', port=port)
