from flask import Flask, request, jsonify
import sqlite3
import json
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# create db connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# email validation
def validate_email(email):
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) 

# password validation
def validate_password(password):
    return len(password) >= 6

# user created/updated data validation
def validate_user_data(data, for_update=False):
    required = ['name', 'email', 'password'] if not for_update else ['name', 'email']
    for field in required:
        if field not in data or not data[field]:
            return f"Missing or empty {field}"
        if field == 'email' and not validate_email(data[field]):
            return "Invalid email format"
        if field == 'password' and not for_update and not validate_password(data[field]):
            return "Password too short"
    return None


@app.route('/')
def home():
    return jsonify({"message": "User Management System"}), 200           #using jsonify for better response format

# list all the users 
@app.route('/users', methods=['GET'])
def get_all_users():
    with get_db_connection() as conn:                                         # opening a connection
        users = conn.execute("SELECT id, name, email FROM users").fetchall()
        return jsonify([dict(row) for row in users]), 200


# Get user by ID
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with get_db_connection() as conn:           
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user:
            return jsonify(dict(user)), 200
        return jsonify({"error": "User not found"}), 404


# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(force=True)
    error = validate_user_data(data)
    if error:
        return jsonify({"error": error}), 400

    hashed_password = generate_password_hash(data['password'])
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (data['name'], data['email'], hashed_password),
            )
            conn.commit()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409


# Update an existing user
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json(force=True)
    error = validate_user_data(data, for_update=True)
    if error:
        return jsonify({"error": error}), 400

    with get_db_connection() as conn:
        result = conn.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (data['name'], data['email'], user_id)
        )
        conn.commit()
        if result.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User updated"}), 200

# Delete a user
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with get_db_connection() as conn:
        result = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        if result.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted"}), 200


# Search users by name
@app.route('/search', methods=['GET'])
def search_users():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"error": "Please provide a name to search"}), 400

    with get_db_connection() as conn:
        pattern = f"%{name}%"
        users = conn.execute(
            "SELECT id, name, email FROM users WHERE name LIKE ?", (pattern,)
        ).fetchall()
        return jsonify([dict(row) for row in users]), 200

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    email = data.get('email')
    password = data.get('password')
    if not (email and password):
        return jsonify({"error": "Email and password required"}), 400

    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT id, name, email, password FROM users WHERE email = ?", (email,)
        ).fetchone()
        if user and check_password_hash(user['password'], password):
            return jsonify({"status": "success", "user_id": user["id"]}), 200
        return jsonify({"status": "failed"}), 401
    

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
