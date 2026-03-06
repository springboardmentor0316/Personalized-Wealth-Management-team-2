from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import jwt
import datetime
import os
from functools import wraps

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
PORT = 3000

# In-memory user storage (in production, use a database)
users = []

# Helper functions
def find_user_by_email(email):
    return next((user for user in users if user['email'] == email), None)

def generate_token(user):
    payload = {
        'id': user['id'],
        'email': user['email'],
        'fullName': user['fullName'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Routes
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        full_name = data.get('fullName')
        email = data.get('email')
        password = data.get('password')

        # Validation
        if not full_name or not email or not password:
            return jsonify({'message': 'All fields are required'}), 400

        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400

        # Check if user already exists
        existing_user = find_user_by_email(email)
        if existing_user:
            return jsonify({'message': 'User already registered'}), 409

        # Create new user (storing password in plain text for demo - use hashing in production)
        new_user = {
            'id': str(int(datetime.datetime.now().timestamp())),
            'fullName': full_name,
            'email': email,
            'password': password,  # In production, always hash passwords
            'createdAt': datetime.datetime.now().isoformat()
        }

        # Save user
        users.append(new_user)
        print(f"User registered: id={new_user['id']}, email={new_user['email']}")

        # Return user data without password
        user_response = {
            'id': new_user['id'],
            'fullName': new_user['fullName'],
            'email': new_user['email']
        }

        return jsonify({
            'message': 'User registered successfully',
            'user': user_response
        }), 201

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Validation
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        # Find user
        user = find_user_by_email(email)
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401

        # Check password (plain text comparison for demo - use hashing in production)
        if user['password'] != password:
            return jsonify({'message': 'Invalid email or password'}), 401

        # Generate JWT token
        token = generate_token(user)
        print(f"User logged in: id={user['id']}, email={user['email']}")

        # Return user data without password
        user_response = {
            'id': user['id'],
            'fullName': user['fullName'],
            'email': user['email']
        }

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_response
        }), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/users', methods=['GET'])
def get_users():
    # Return users without passwords (for debugging - remove in production)
    users_without_passwords = []
    for user in users:
        user_copy = user.copy()
        del user_copy['password']
        users_without_passwords.append(user_copy)
    
    return jsonify(users_without_passwords)

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

if __name__ == '__main__':
    print(f"Server running on http://localhost:{PORT}")
    print("Frontend available at: http://localhost:3000")
    print("API endpoints:")
    print("  POST /register - User registration")
    print("  POST /login - User login")
    print("  GET /users - Get all users (debug)")
    app.run(host='0.0.0.0', port=PORT, debug=True)
